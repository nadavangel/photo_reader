import logging
import sys
import time
from datetime import timedelta

import photo
from photo import WellNameTxt, MicroscopeException, get_exception_location
from tkinter import filedialog
import argparse
import pathlib

def main() -> int:  # pragma: no cover
	
	parser = argparse.ArgumentParser(prog="SplitToWells", description="Split microscope images to well folders")
	parser.add_argument("-f", "--folder", type=pathlib.Path, help="Source folder (plate/Spinning disc)")
	parser.add_argument("-d", "--dest", type=pathlib.Path, help="Destination folder")
	parser.add_argument("-n", "--name", type=str, default="", help="Name/prefix for the output")
	parser.add_argument("-m", "--material", type=str, default="", help="Material info with well names (tab-separated: position\\tname)")
	parser.add_argument("-p", "--file-prefix", type=str, default="", help="File prefix for output files")
	parser.add_argument("--no-subdir", action="store_true", help="Do not create subdirectories for each position")
	parser.add_argument('-v', '--verbose', help='debug logs', action='store_const', const=logging.DEBUG,
	                    default=logging.INFO)
	
	args = parser.parse_args()
	logging.basicConfig(stream=sys.stdout, level=args.verbose,
	                    format='%(asctime)s %(levelname)-7s %(message)s')
	
	logger = logging.getLogger("SplitToWells")
	logger.info("Starting SplitToWells CLI")
	
	# Get source folder
	if args.folder is None:
		print('Please select source (plate/Spinning disc) folder:')
		folder = filedialog.askdirectory(title="Select source folder")
	else:
		folder = args.folder
		
	if folder is None or folder == "":
		logger.error("No source folder was selected")
		return 1
		
	# Get destination folder
	if args.dest is None:
		print('Please select destination folder:')
		dest = filedialog.askdirectory(title="Select destination folder")
	else:
		dest = args.dest
	
	if dest is None or dest == "":
		logger.error("No destination folder was selected")
		return 1
	
	# Parse well names if provided
	well_name = None
	if args.material:
		try:
			well_name = WellNameTxt(buff=args.material)
			logger.debug(f"Parsed material info: {args.material}")
		except Exception as e:
			ex_file, ex_line = get_exception_location()
			logger.error(f"Error parsing material info: {e} (at {ex_file}:{ex_line})")
			return 1
	
	# Initialize microscope
	try:
		mic = photo.Microscope(folder=folder)
		logger.info(f"Initialized microscope from folder: {folder}")
	except MicroscopeException as e:
		ex_file, ex_line = get_exception_location()
		logger.error(f"Error occurred while initializing microscope: \"{e}\" (at {ex_file}:{ex_line})")
		return 1
	except TypeError as e:
		ex_file, ex_line = get_exception_location()
		logger.error(f"Type error occurred while initializing microscope: \"{e}\" (at {ex_file}:{ex_line})")
		return 1
	
	# Process files
	try:
		start = time.time()
		dest_result = mic.move(
			dest=dest,
			prefix=args.name,
			create_dubdir=not args.no_subdir,
			pos_names=well_name,
			file_prefix=args.file_prefix
		)
		end = time.time()
		total_time = timedelta(seconds=end-start)
		
		logger.info(f"Done, it took {str(total_time)}, the files are at {str(dest_result)}")
		return 0
	except Exception as e:
		ex_file, ex_line = get_exception_location()
		logger.error(f"Error occurred while processing files: {e} (at {ex_file}:{ex_line})")
		return 1


if __name__ == '__main__':
	re = main()
	input("Press Enter to exit")
	sys.exit(re)
