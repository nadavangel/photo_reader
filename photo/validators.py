"""Module for path validation functions."""

from pathlib import Path


def validate_directory(value: Path | str) -> Path:
    """
    Validate and convert a string or Path object to a Path object representing a directory.

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


def validate_file(value: Path | str) -> Path:
    """
    Validate and convert a string or Path object to a Path object representing a file.

    :param value: The path value (Path or str).
    :return: A Path object.
    """
    if isinstance(value, str):
        val = Path(value)
    elif isinstance(value, Path):
        val = value
    else:
        raise TypeError("Path is not from type 'Path'")

    if not val.is_file():
        raise TypeError(f'Path "{str(val)}", is not a file.')
    return val
