import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from photo.microscopebase import MicroscopeBase, MicroscopeException, get_exception_location
from photo.wells import WellPos
from photo.photo import Photo


class ConcreteMicroscope(MicroscopeBase):
    def _match(self, pos_names=None):
        return []


def test_get_exception_location():
    try:
        raise ValueError("test error")
    except ValueError:
        filename, lineno = get_exception_location()
        assert filename == "test_microscopebase.py"
        assert isinstance(lineno, int)


def test_microscopebase_init(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    assert m.path == tmp_path
    assert not m._pos_photo
    assert isinstance(m._files_list, list)


def test_microscopebase_add_photo(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    pos = WellPos(row="A", col=1, site=1)
    photo = MagicMock(spec=Photo)

    m._add_photo(pos, photo)
    assert m._pos_photo[pos] == [photo]

    photo2 = MagicMock(spec=Photo)
    m._add_photo(pos, photo2)
    assert m._pos_photo[pos] == [photo, photo2]


def test_microscopebase_move_success(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    m = ConcreteMicroscope(src)
    pos = WellPos(row="A", col=1, site=1)
    photo = MagicMock(spec=Photo)
    photo.path = MagicMock()
    photo.path.name = "test.tif"
    m._add_photo(pos, photo)

    result = m.move(dest)
    assert result == (dest.absolute() / "out")
    photo.copy.assert_called()


def test_microscopebase_move_exception(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    with patch.object(m, "_move", side_effect=MicroscopeException("error")):
        assert m.move(tmp_path) is None


def test_microscopebase_move_typeerror(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    with patch.object(m, "_move", side_effect=TypeError("error")):
        assert m.move(tmp_path) is None


def test_microscopebase_move_not_a_folder(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("not a folder")

    with pytest.raises(TypeError):
        m._move(file_path)


def test_microscopebase_move_microscope_exception_if_not_dir(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    dest = tmp_path / "nonexistent"

    mock_path = MagicMock(spec=Path)
    mock_path.is_dir.return_value = False
    mock_path.__str__.return_value = str(dest)
    mock_path.absolute.return_value = mock_path

    with patch("photo.microscopebase.validate_directory", return_value=mock_path):
        with pytest.raises(MicroscopeException, match="is not a folder"):
            m._move(dest)


def test_microscopebase_move_no_subdir(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    m = ConcreteMicroscope(src)
    pos = WellPos(row="A", col=1, site=1)
    photo = MagicMock(spec=Photo)
    photo.path = MagicMock()
    photo.path.name = "test.tif"
    m._add_photo(pos, photo)

    result = m._move(dest, create_dubdir=False, prefix="pre")
    assert result == (dest.absolute() / "out")
    photo.copy.assert_called_with(dest.absolute() / "out", prefix="A01_pre")


def test_microscopebase_move_file_prefix(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    m = ConcreteMicroscope(src)
    pos = WellPos(row="A", col=1, site=1)
    photo = MagicMock(spec=Photo)
    photo.path = MagicMock()
    photo.path.name = "test.tif"
    m._add_photo(pos, photo)

    m._move(dest, file_prefix="fp")
    photo.copy.assert_called_with(dest.absolute() / "out" / "A01", prefix="fp_")


def test_microscopebase_move_skipped_files(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    class SkipMicroscope(ConcreteMicroscope):
        def _match(self, pos_names=None):
            f1 = MagicMock(spec=Path)
            f1.name = "skipped1.tif"
            return [f1]

    m = SkipMicroscope(src)
    with patch("photo.microscopebase.logger") as mock_logger:
        m.move(dest)
        mock_logger.warning.assert_called()
        args = mock_logger.warning.call_args[0][0]
        assert "Skipped 1 file: skipped1.tif" in args

    class MultiSkipMicroscope(ConcreteMicroscope):
        def _match(self, pos_names=None):
            f1 = MagicMock(spec=Path)
            f1.name = "skipped1.tif"
            f2 = MagicMock(spec=Path)
            f2.name = "skipped2.tif"
            return [f1, f2]

    m = MultiSkipMicroscope(src)
    with patch("photo.microscopebase.logger") as mock_logger:
        m.move(dest)
        mock_logger.warning.assert_called()
        args = mock_logger.warning.call_args[0][0]
        assert "Skipped 2 files: skipped1.tif, skipped2.tif" in args


def test_microscopebase_path_setter(tmp_path):
    m = ConcreteMicroscope(tmp_path)
    new_path = tmp_path / "new"
    new_path.mkdir()
    m.path = str(new_path)
    assert m.path == new_path
