"""Module for base class and exception handling for microscope data processing."""

from __future__ import annotations

import abc
import logging
import sys
import traceback
import typing
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from photo.photo import Photo
from photo.validators import validate_directory
from photo.wells import WellName, WellPos

logger = logging.getLogger("mylSplitToWells")


class MicroscopeException(Exception):
    """Exception raised for errors in microscope data processing."""


def get_exception_location() -> typing.Tuple[str, typing.Optional[int]]:
    """
    Get the filename and line number where an exception occurred.

    :return: A tuple containing the filename and line number.
    """
    _, _, exc_traceback = sys.exc_info()

    last_frame = traceback.extract_tb(exc_traceback)[-1]

    full_filename = last_frame.filename
    lineno = last_frame.lineno
    # function_name = last_frame.name
    # line_of_code = last_frame.line
    filename = Path(full_filename).name
    return (filename, lineno)


class MicroscopeBase(abc.ABC):
    """Abstract base class for different types of microscope data sources."""

    _path: Path
    _files_list: typing.List[Path]
    _pos_photo: typing.Dict[WellPos, typing.List[Photo]]

    def __init__(self, folder: typing.Union[Path, str]):
        """
        Initialize the MicroscopeBase instance.

        :param folder: The path to the folder containing microscope images.
        """
        self.path = folder
        self._pos_photo = {}
        self._fill_files()

    def _fill_files(self):
        """Populate the list of files from the source folder."""
        self._files_list = list(self.path.iterdir())

    @abc.abstractmethod
    def _match(self, pos_names: typing.Optional[WellName] = None):
        """
        Abstract method to match files to well positions.

        :param pos_names: Optional well name mapping.
        """

    def _add_photo(self, pos: WellPos, photo: Photo):
        """
        Add a photo to the internal position-to-photo mapping.

        :param pos: The well position.
        :param photo: The photo object.
        """
        if pos not in self._pos_photo:
            self._pos_photo[pos] = [photo]
        else:
            self._pos_photo[pos].append(photo)

    def move(self, *args, **kwargs):
        """
        Move files to the destination directory with error handling.

        :param args: Positional arguments for _move.
        :param kwargs: Keyword arguments for _move.
        :return: The destination directory path, or None if an error occurred.
        """
        try:
            return self._move(*args, **kwargs)
        except MicroscopeException as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f"Error occurred while moving files: {e} (at {ex_file}:{ex_line})")
            return None
        except TypeError as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f"Type error occurred while moving files: {e} (at {ex_file}:{ex_line})")
            return None
        except Exception as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f"Unexpected error occurred while moving files: {e} (at {ex_file}:{ex_line})")
            return None

    def _move(
        self,
        dest: typing.Union[Path, str],
        prefix: str = "",
        create_dubdir: bool = True,
        pos_names: typing.Optional[WellName] = None,
        file_prefix: str = "",
        threads: int = 1,
    ):
        """
        Core logic for moving files to the destination.

        :param dest: Destination directory path.
        :param prefix: Optional prefix for files.
        :param create_dubdir: Whether to create subdirectories for each position.
        :param pos_names: Optional well name mapping.
        :param file_prefix: Optional file prefix.
        :param threads: Number of threads to use for file copying.
        :return: The destination directory path.
        """
        base_dest_dir = validate_directory(dest)
        if not base_dest_dir.is_dir():
            raise MicroscopeException(f"{str(base_dest_dir)} is not a folder")
        dest_dir = base_dest_dir.absolute() / "out"
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Create {str(dest_dir)}")
        skipped_files = self._match(pos_names)

        copy_tasks = []
        for pos, photos in self._pos_photo.items():
            if create_dubdir:
                pos_dir = dest_dir / str(pos)
                pos_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Create {str(pos_dir)}")
                pos_prefix = prefix
            else:
                pos_dir = dest_dir
                pos_prefix = f"{str(pos)}_{prefix}"

            if file_prefix:
                current_prefix = f"{file_prefix}_{pos_prefix}"
            else:
                current_prefix = pos_prefix

            for photo in photos:
                copy_tasks.append((photo, pos_dir, current_prefix))

        if threads > 1:
            logger.info(f"Starting parallel copy with {threads} threads")
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(photo.copy, dest_dir, prefix=prefix) for photo, dest_dir, prefix in copy_tasks]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error copying file: {e}")
        else:
            for photo, pos_dir, current_prefix in copy_tasks:
                photo.copy(pos_dir, prefix=current_prefix)
                logger.info(f'Copy "{str(photo.path.name)}" to {str(pos_dir.name)}')

        if len(skipped_files) > 0:
            skipped_files_names = ", ".join([file.name for file in skipped_files])
            logger.warning(f"Skipped {len(skipped_files)} file{'s' if len(skipped_files) > 1 else ''}: {skipped_files_names}")

        return dest_dir

    @property
    def path(self) -> Path:
        """Get the source path."""
        return self._path

    @path.setter
    def path(self, value: typing.Union[Path, str]):
        """
        Set the source path.

        :param value: The source path (Path or str).
        """
        self._path = validate_directory(value)
