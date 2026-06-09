"""Module for path validation functions."""

from __future__ import annotations

import typing
from pathlib import Path


def validate_directory(value: typing.Union[Path, str]) -> Path:
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
        raise TypeError(f'Path "{str(val)}", is not a directory.')
    return val


def validate_file(value: typing.Union[Path, str]) -> Path:
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
