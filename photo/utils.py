"""Module for factory methods to instantiate the appropriate microscope processor."""

from __future__ import annotations

import logging

from photo.eva import Eva
from photo.microscopebase import MicroscopeBase
from photo.spinning_disk import SpinningDisk
from photo.validators import validate_directory

logger = logging.getLogger("mylSplitToWells")


def Microscope(folder: str) -> MicroscopeBase:  # pylint: disable=invalid-name
    """
    Factory function to create the appropriate microscope processor based on input folder.

    :param folder: The path to the folder containing microscope images.
    :return: An instance of Eva or SpinningDisk.
    """
    folder_path = validate_directory(folder)
    data_dir = folder_path / "data"
    if data_dir.is_dir():
        return Eva(folder=folder_path)

    return SpinningDisk(folder=folder_path)
