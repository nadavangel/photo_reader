"""Module for factory methods to instantiate the appropriate microscope processor."""

from photo import Eva, MicroscopeBase, SpinningDisk
import logging

logger = logging.getLogger("mylSplitToWells")


class Microscope:
    """Factory class to create the appropriate microscope processor based on input folder."""

    def __new__(cls, *args, **kwargs):
        """
        Create and return an instance of Eva or SpinningDisk based on the folder content.

        :param folder: The path to the folder containing microscope images.
        :return: An instance of Eva or SpinningDisk.
        """
        folder = MicroscopeBase.path_value(kwargs.get("folder"))
        data_dir = folder / "data"
        if data_dir.is_dir():
            cls = Eva
        else:
            cls = SpinningDisk

        return cls(folder=folder)
