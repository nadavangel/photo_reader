"""Module for processing Eva microscope image data."""

from __future__ import annotations

import logging
import re
import typing
from pathlib import Path

from photo.microscopebase import MicroscopeBase
from photo.photo import Photo
from photo.validators import validate_directory
from photo.wells import WellName, WellPos

logger = logging.getLogger("mylSplitToWells")


class Eva(MicroscopeBase):
    """Represents data from an Eva microscope."""

    regEx_file_name = r"(?P<row>[A-Za-z]+)(?P<col>\d+)[-]*W(?P<well>\d+)[-]*P(?P<pos>\d+)[-]*Z(?P<z>\d+)[-]*T(?P<time>\d+)[-]*(?P<channel>\w+).tif"

    def __init__(self, folder: typing.Union[Path, str]):
        """
        Initialize the Eva instance.

        :param folder: The path to the folder containing microscope images.
        """
        data_folder = str(validate_directory(folder) / "data")
        logger.debug(f"Initializing Eva with data folder: {data_folder}")
        super().__init__(folder=data_folder)

    @staticmethod
    def _parse_file_name(line: str, pos_names: typing.Optional[WellName] = None):
        """
        Parse a filename to extract position information.

        :param line: The filename string.
        :param pos_names: Optional well name mapping.
        :return: A tuple (success_flag, position_or_none).
        """
        logger.debug(f"Parsing file name: {line}")
        reg = re.match(Eva.regEx_file_name, string=line)
        if reg is None:
            logger.warning(f"Failed to parse file name: {line}")
            return (False, None)
        di = reg.groupdict()
        pos = WellPos(row=di["row"], col=int(di["col"]), site=int(di["pos"]))
        pos_str = f"{pos.row.upper()}{pos.col}"
        if pos_names is not None and pos_str in pos_names:
            pos.name = pos_names[pos_str]
        logger.debug(f"Parsed position: {pos}")
        return (True, pos)

    def _match(self, pos_names: typing.Optional[WellName] = None):
        """
        Match files in the source folder to well positions.

        :param pos_names: Optional well name mapping.
        :return: A list of skipped files.
        """
        self._pos_photo = {}
        skiped_files = []
        logger.info("Matching files to positions")
        for file in self._files_list:
            if not file.is_file():
                logger.warning(f"Skipping non-file: {file}")
                skiped_files.append(file)
                continue
            file_name = file.name.strip()
            suc, pos = self._parse_file_name(file_name, pos_names=pos_names)
            if suc:
                self._add_photo(pos, Photo(path=file, pos=pos))
                logger.debug(f"Matched file {file_name} to position {pos}")
            else:
                logger.warning(f"Failed to match file: {file_name}")
        if len(skiped_files) > 0:
            logger.info(f"Skipped files: {skiped_files}")
        return skiped_files
