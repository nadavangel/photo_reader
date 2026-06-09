import pytest

from photo.validators import validate_directory, validate_file


def test_validate_directory_str(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    assert validate_directory(str(d)) == d


def test_validate_directory_path(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    assert validate_directory(d) == d


def test_validate_directory_not_path_type():
    with pytest.raises(TypeError, match="Path is not from type 'Path'"):
        validate_directory(123)


def test_validate_directory_not_exists(tmp_path):
    d = tmp_path / "nonexistent"
    with pytest.raises(TypeError, match="is not a directory"):
        validate_directory(d)


def test_validate_file_str(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    assert validate_file(str(f)) == f


def test_validate_file_path(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    assert validate_file(f) == f


def test_validate_file_not_path_type():
    with pytest.raises(TypeError, match="Path is not from type 'Path'"):
        validate_file(123)


def test_validate_file_not_exists(tmp_path):
    f = tmp_path / "nonexistent.txt"
    with pytest.raises(TypeError, match="is not a file"):
        validate_file(f)
