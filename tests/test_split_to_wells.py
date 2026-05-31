import pathlib
from unittest.mock import patch
from split_to_wells import get_folder_input, get_text_input, get_yes_no_input, main
from photo.microscopebase import MicroscopeException


def test_get_folder_input(tmp_path):
    nonexistent = tmp_path / "nonexistent"
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a dir")

    # We use real paths to avoid patching Path.exists and is_dir globally
    with patch("builtins.input", side_effect=["", str(nonexistent), str(file_path), str(tmp_path)]):
        result = get_folder_input("prompt")
        assert result == pathlib.Path(str(tmp_path))


def test_get_text_input():
    with patch("builtins.input", side_effect=["", "some text"]):
        assert get_text_input("prompt", required=True) == "some text"

    with patch("builtins.input", return_value=""):
        assert get_text_input("prompt", required=False) == ""


def test_get_yes_no_input():
    with patch("builtins.input", side_effect=["", "y", "yes", "n", "no", "invalid", "y"]):
        assert get_yes_no_input("p", default=True) is True
        assert get_yes_no_input("p", default=True) is True
        assert get_yes_no_input("p", default=True) is True
        assert get_yes_no_input("p", default=True) is False
        assert get_yes_no_input("p", default=True) is False
        assert get_yes_no_input("p", default=True) is True  # invalid then y


def test_main_missing_args(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    with patch("sys.argv", ["split_to_wells.py"]):
        with patch("split_to_wells.get_folder_input", side_effect=[src, dest]):
            with patch("split_to_wells.get_text_input", side_effect=["name", "fp"]):
                with patch("builtins.input", side_effect=["", ""]):  # material info (loop until empty line)
                    with patch("split_to_wells.get_yes_no_input", return_value=True):
                        with patch("split_to_wells.Microscope") as mock_mic:
                            mock_mic_instance = mock_mic.return_value
                            mock_mic_instance.move.return_value = dest / "out"
                            assert main() == 0


def test_main_with_args(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    args = [
        "split_to_wells.py",
        "--folder",
        str(src),
        "--dest",
        str(dest),
        "--name",
        "testname",
        "--material",
        "A01\tSample1",
        "--file-prefix",
        "fp",
        "--no-subdir",
    ]
    with patch("sys.argv", args):
        with patch("split_to_wells.Microscope") as mock_mic:
            mock_mic_instance = mock_mic.return_value
            mock_mic_instance.move.return_value = dest / "out"
            assert main() == 0


def test_main_microscope_exception(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    args = ["split_to_wells.py", "--folder", str(src), "--dest", str(dest), "--name", "n", "--file-prefix", "p", "--no-subdir"]
    with patch("sys.argv", args):
        with patch("builtins.input", side_effect=[""]):  # material info
            with patch("split_to_wells.Microscope", side_effect=MicroscopeException("init error")):
                assert main() == 1


def test_main_type_error(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    args = ["split_to_wells.py", "--folder", str(src), "--dest", str(dest), "--name", "n", "--file-prefix", "p", "--no-subdir"]
    with patch("sys.argv", args):
        with patch("builtins.input", side_effect=[""]):  # material info
            with patch("split_to_wells.Microscope", side_effect=TypeError("type error")):
                assert main() == 1


def test_main_move_exception(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    args = ["split_to_wells.py", "--folder", str(src), "--dest", str(dest), "--name", "n", "--file-prefix", "p", "--no-subdir"]
    with patch("sys.argv", args):
        with patch("builtins.input", side_effect=[""]):  # material info
            with patch("split_to_wells.Microscope") as mock_mic:
                mock_mic_instance = mock_mic.return_value
                mock_mic_instance.move.side_effect = MicroscopeException("move error")
                assert main() == 1


def test_main_material_parse_error(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    args = ["split_to_wells.py", "--folder", str(src), "--dest", str(dest), "--name", "n", "--file-prefix", "p", "--no-subdir", "--material", "bad"]
    with patch("sys.argv", args):
        with patch("split_to_wells.WellNameTxt", side_effect=ValueError("parse error")):
            assert main() == 1


def test_main_no_folder(tmp_path):
    with patch("sys.argv", ["split_to_wells.py"]):
        with patch("split_to_wells.get_folder_input", return_value=""):
            assert main() == 1


def test_main_no_dest(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    with patch("sys.argv", ["split_to_wells.py", "--folder", str(src)]):
        with patch("split_to_wells.get_folder_input", return_value=""):
            assert main() == 1


def test_main_material_with_content(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    with patch("sys.argv", ["split_to_wells.py", "--folder", str(src), "--dest", str(dest)]):
        with patch("builtins.input", side_effect=["n", "A01\tS1", "", "p", "y"]):  # name, mat1, mat_end, prefix, subdir
            with patch("split_to_wells.Microscope") as mock_mic:
                mock_mic_instance = mock_mic.return_value
                mock_mic_instance.move.return_value = dest / "out"
                assert main() == 0
