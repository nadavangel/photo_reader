"""Module for base class and exception handling for microscope data processing."""

import abc
import logging
import traceback
import sys
from pathlib import Path
from typing import Tuple

from photo.photo import Photo
from photo.wells import WellPos, WellName

logger = logging.getLogger("mylSplitToWells")


class MicroscopeException(Exception):
    """Exception raised for errors in microscope data processing."""

    pass


def get_exception_location() -> Tuple[str, int]:
    """
    Get the filename and line number where an exception occurred.

    :return: A tuple containing the filename and line number.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()

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
    _files_list: list[Path]
    _pos_photo: dict[WellPos, list[Photo]]

    def __init__(self, folder: Path | str):
        """
        Initialize the MicroscopeBase instance.

        :param folder: The path to the folder containing microscope images.
        """
        self.path = folder
        self._fill_files()

    def _fill_files(self):
        """Populate the list of files from the source folder."""
        self._files_list = list(self.path.iterdir())

    @abc.abstractmethod
    def _match(self, pos_names: WellName | None = None):
        """
        Abstract method to match files to well positions.

        :param pos_names: Optional well name mapping.
        """
        pass

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
            logger.error(
                f"Error occurred while moving files: {e} (at {ex_file}:{ex_line})"
            )
            return None
        except TypeError as e:
            ex_file, ex_line = get_exception_location()
            logger.error(
                f"Type error occurred while moving files: {e} (at {ex_file}:{ex_line})"
            )
            return None

    def _move(
        self,
        dest: Path | str,
        prefix: str = "",
        create_dubdir: bool = True,
        pos_names: WellName | None = None,
        file_prefix: str = "",
    ):
        """
        Core logic for moving files to the destination.

        :param dest: Destination directory path.
        :param prefix: Optional prefix for files.
        :param create_dubdir: Whether to create subdirectories for each position.
        :param pos_names: Optional well name mapping.
        :param file_prefix: Optional file prefix.
        :return: The destination directory path.
        """
        base_dest_dir = self.path_value(dest)
        if not base_dest_dir.is_dir():
            raise MicroscopeException(f"{str(base_dest_dir)} is not a folder")
        dest_dir = base_dest_dir.absolute() / "out"
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Create {str(dest_dir)}")
        skipped_files = self._match(pos_names)

        for pos in self._pos_photo:
            if create_dubdir:
                pos_dir = dest_dir / str(pos)
                pos_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Create {str(pos_dir)}")
                pos_prefix = prefix
            else:
                pos_dir = dest_dir
                pos_prefix = f"{str(pos)}_{prefix}"

            if file_prefix:
                pos_prefix = f"{file_prefix}_{pos_prefix}"

            for file in self._pos_photo[pos]:
                file.copy(pos_dir, prefix=pos_prefix)
                logger.info(f'Copy "{str(file.path.name)}" to {str(pos)}')

        if len(skipped_files) > 0:
            skipped_files_names = ", ".join([file.name for file in skipped_files])
            logger.warning(
                f"Skipped {len(skipped_files)} file{'s' if len(skipped_files) > 1 else ''}: {skipped_files_names}"
            )

        return dest_dir

    @property
    def path(self) -> Path:
        """Get the source path."""
        return self._path

    @staticmethod
    def path_value(value: Path | str) -> Path:
        """
        Validate and convert a string or Path object to a Path object.

        :param value: The path value (Path or str).
        :return: A Path object.
        """
        if isinstance(value, str):
            val = Path(value)
        elif isinstance(value, Path):
            val = value
        else:
            raise TypeError("Path is not from type 'Path'")

        if not val.is_dir():
            raise TypeError(f'Path "{str(val)}", is not a dirctory.')
        return val

    @path.setter
    def path(self, value: Path | str):
        """
        Set the source path.

        :param value: The source path (Path or str).
        """
        self._path = self.path_value(value)
