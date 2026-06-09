from unittest.mock import patch

from photo.utils import Microscope


def test_microscope_eva(tmp_path):
    # Setup
    folder = tmp_path / "test_folder"
    folder.mkdir()
    data_dir = folder / "data"
    data_dir.mkdir()

    # Execute & Assert
    with patch("photo.validators.validate_directory", return_value=folder):
        with patch("photo.utils.Eva") as mock_eva:
            microscope = Microscope(str(folder))
            mock_eva.assert_called_once_with(folder=folder)
            assert microscope == mock_eva.return_value


def test_microscope_spinning_disk(tmp_path):
    # Setup
    folder = tmp_path / "test_folder"
    folder.mkdir()

    # Execute & Assert
    with patch("photo.validators.validate_directory", return_value=folder):
        with patch("photo.utils.SpinningDisk") as mock_sd:
            microscope = Microscope(str(folder))
            mock_sd.assert_called_once_with(folder=folder)
            assert microscope == mock_sd.return_value
