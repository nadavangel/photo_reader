"""Module for command-line interface for splitting microscope images into well folders."""

from __future__ import annotations

import argparse
import importlib.metadata
import logging
import pathlib
import sys
import time
from datetime import timedelta

from photo.microscopebase import MicroscopeException, get_exception_location
from photo.utils import Microscope
from photo.wells import WellNameTxt

APP_VERSION = importlib.metadata.version("photo_reader")


def get_folder_input(prompt: str) -> pathlib.Path:
    """
    Get a valid folder path from standard input.

    Prompts the user with the given prompt, validates that the input is not empty,
    exists, and is a directory. Loops until a valid path is provided.

    Args:
        prompt: The message to display to the user.

    Returns:
        A pathlib.Path object representing the validated directory path.
    """
    while True:
        path_input = input(prompt).strip()
        if not path_input:
            print("Error: Path cannot be empty")
            continue

        path = pathlib.Path(path_input)
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            continue

        if not path.is_dir():
            print(f"Error: Path is not a directory: {path}")
            continue

        return path


def get_text_input(prompt: str, required: bool = False) -> str:
    """
    Get text input from standard input.

    Prompts the user with the given prompt and ensures that if required,
    the input is not empty.

    Args:
        prompt: The message to display to the user.
        required: Whether the input field is mandatory.

    Returns:
        The stripped text input from the user.
    """
    while True:
        value = input(prompt).strip()
        if not value and required:
            print("Error: This field is required")
            continue
        return value


def get_yes_no_input(prompt: str, default: bool = True) -> bool:
    """
    Get a yes/no response from standard input.

    Prompts the user with the given prompt and a default value indicator.
    Accepts 'y', 'yes', 'n', or 'no' (case-insensitive).

    Args:
        prompt: The message to display to the user.
        default: The default boolean value if the user just presses Enter.

    Returns:
        True if the user selects yes, False if the user selects no.
    """
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Error: Please enter 'y' (yes) or 'n' (no)")


def main() -> int:
    """
    Main entry point for the SplitToWells CLI application.

    Parses command line arguments, configures logging, gathers necessary input,
    initializes the microscope processor, and executes the file splitting operation.

    Returns:
        0 if the process completes successfully, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=f"Split To Wells v{APP_VERSION} - Split microscope images into well folders.")
    parser.add_argument("-f", "--folder", type=pathlib.Path, help="Source folder (plate/Spinning disc)")
    parser.add_argument("-d", "--dest", type=pathlib.Path, help="Destination folder")
    parser.add_argument("-n", "--name", type=str, default="", help="Name/prefix for the output")
    parser.add_argument(
        "-m",
        "--material",
        type=str,
        default="",
        help="Material info with well names (tab-separated: position\\tname)",
    )
    parser.add_argument("-p", "--file-prefix", type=str, default="", help="File prefix for output files")
    parser.add_argument(
        "--no-subdir",
        action="store_true",
        help="Do not create subdirectories for each position",
    )
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of threads for parallel processing")
    parser.add_argument(
        "-v",
        "--verbose",
        help="debug logs",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
    )

    args = parser.parse_args()
    logging.basicConfig(
        stream=sys.stdout,
        level=args.verbose,
        format="%(asctime)s %(levelname)-7s %(message)s",
    )

    logger = logging.getLogger("SplitToWells")
    logger.info("Starting SplitToWells CLI")

    # Get source folder
    if args.folder is None:
        print("Please select source (plate/Spinning disc) folder:")
        folder = get_folder_input("Enter source folder path: ")
    else:
        folder = args.folder

    if folder is None or folder == "":
        logger.error("No source folder was selected")
        return 1

    # Get destination folder
    if args.dest is None:
        print("Please select destination folder:")
        dest = get_folder_input("Enter destination folder path: ")
    else:
        dest = args.dest

    if dest is None or dest == "":
        logger.error("No destination folder was selected")
        return 1

    # Get name/prefix
    if args.name == "":
        name = get_text_input("Enter name/prefix for output files (optional): ")
    else:
        name = args.name

    # Get material/wells info
    material_text = args.material
    if material_text == "":
        print("Enter material info with well names (tab-separated: position<TAB>name)")
        print("Press Enter twice when done, or leave empty to skip:")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        material_text = "\n".join(lines) if lines else ""

    # Parse well names if provided
    well_name = None
    if material_text:
        try:
            well_name = WellNameTxt(buff=material_text)
            logger.debug(f"Parsed material info: {material_text}")
        except (ValueError, KeyError, TypeError) as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f"Error parsing material info: {e} (at {ex_file}:{ex_line})")
            return 1

    # Get file prefix
    if args.file_prefix == "":
        file_prefix = get_text_input("Enter file prefix for output files (optional): ")
    else:
        file_prefix = args.file_prefix

    # Get subdirectory creation preference
    if args.no_subdir:
        create_subdir = False
    else:
        create_subdir = get_yes_no_input("Create subdirectories for each position?", default=True)

    # Initialize microscope
    try:
        mic = Microscope(folder=str(folder))
        logger.info(f"Initialized microscope from folder: {folder}")
    except MicroscopeException as e:
        ex_file, ex_line = get_exception_location()
        logger.error(f'Error occurred while initializing microscope: "{e}" (at {ex_file}:{ex_line})')
        return 1
    except TypeError as e:
        ex_file, ex_line = get_exception_location()
        logger.error(f'Type error occurred while initializing microscope: "{e}" (at {ex_file}:{ex_line})')
        return 1

    # Process files
    try:
        start = time.time()
        dest_result = mic.move(
            dest=dest,
            prefix=name,
            create_dubdir=create_subdir,
            pos_names=well_name,
            file_prefix=file_prefix,
        )
        end = time.time()
        total_time = timedelta(seconds=end - start)

        logger.info(f"Done, it took {str(total_time)}, the files are at {str(dest_result)}")
        return 0
    except (MicroscopeException, TypeError, OSError) as e:
        ex_file, ex_line = get_exception_location()
        logger.error(f"Error occurred while processing files: {e} (at {ex_file}:{ex_line})")
        return 1


if __name__ == "__main__":
    EXIT_CODE = main()
    input("Press Enter to exit")
    sys.exit(EXIT_CODE)
