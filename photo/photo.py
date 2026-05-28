"""Module for representing microscope images as Photo objects."""

import logging
import re
import shutil
from pathlib import Path

from photo.validators import validate_file
from photo.wells import WellPos

logger = logging.getLogger("mylSplitToWells")


class Photo:
    """Represents a single microscope image file with associated well position metadata."""

    _well: WellPos
    _name: str
    _path: Path

    def __init__(self, path: Path, pos: WellPos | tuple = None):
        """
        Initialize a Photo instance.

        :param path: The filesystem path to the image file.
        :param pos: The well position as a WellPos object or (row, col, site) tuple.
        """
        if pos is not None:
            self.pos = pos

        self._path = path
        logger.debug(f"Photo initialized with path: {path} and pos: {pos}")

    @property
    def pos(self):
        """Get the well position."""
        return self._well

    @pos.setter
    def pos(self, pos: WellPos | tuple):
        """
        Set the well position.

        :param pos: The well position as a WellPos object or (row, col, site) tuple.
        """
        if isinstance(pos, tuple):
            self._well = WellPos.create(pos)
        elif isinstance(pos, WellPos):
            self._well = pos
        else:
            raise TypeError("pos is not a WellPos or tuple")
        logger.debug(f"Position set to: {self._well}")

    def set_well(self, row: str, col: int, site=1):
        """
        Set the well position explicitly.

        :param row: Well row identifier (e.g., 'A').
        :param col: Well column identifier.
        :param site: Well site number.
        """
        self._well = WellPos(row=row, col=col, site=site)
        logger.debug(f"Well set to: {self._well}")

    @property
    def name(self):
        """Get the name/prefix associated with the image."""
        return self._name

    @name.setter
    def name(self, value: str):
        """
        Set the name/prefix associated with the image.

        :param value: The name/prefix string.
        """
        self._name = value
        logger.debug(f"Name set to: {self._name}")

    @property
    def path(self):
        """Get the image file path."""
        return self._path

    @path.setter
    def path(self, value: Path | str):
        """
        Set the image file path.

        :param value: The filesystem path to the image file (Path or str).
        """
        self._path = validate_file(value)
        logger.debug(f"Path set to: {self._path}")

    def copy(self, dest: Path, new_name: str = "", prefix: str = ""):
        """
        Copy the image to a destination directory with an optional new name and prefix.

        :param dest: The destination directory path.
        :param new_name: An optional new name for the file.
        :param prefix: An optional prefix to add to the filename.
        """
        if new_name != "":
            name = new_name
        else:
            name = self.path.stem

        if prefix != "":
            name = prefix + "_" + name

        full_name = sanitize_path(f"{name}{self.path.suffix}")
        new_path = dest / full_name
        shutil.copy2(self.path, new_path)
        logger.info(f'Copied file to: "{new_path}"')


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path by replacing invalid characters with underscores for Windows compatibility.

    :param path: The file path to sanitize.
    :return: The sanitized file path.
    """
    # Forbidden characters in Windows
    forbidden = r'[<>:"/\\|?*]'
    sanitized = re.sub(forbidden, "_", path)
    # Remove trailing spaces and dots
    sanitized = re.sub(r"[\s.]+$", "_", sanitized)
    # Reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
    reserved = re.compile(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$", re.IGNORECASE)
    if reserved.match(sanitized):
        sanitized += "_"
    if sanitized != path:
        print(f"Warning: Invalid characters found in path '{path}'. Replacing with '_'.")
    return sanitized
