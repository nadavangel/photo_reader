import logging
import sys
import time
from datetime import datetime

import photo
from tkinter import filedialog
import argparse
import pathlib

def main() -> int:  # pragma: no cover

	
	parser = argparse.ArgumentParser(prog="SplitToWells")
	parser.add_argument("-f", "--folder", type=pathlib.Path)
	parser.add_argument('-v', '--verbose', help='debug logs', action='store_const', const=logging.DEBUG,
	                    default=logging.INFO)
	args = parser.parse_args()
	logging.basicConfig(stream=sys.stdout, level=args.verbose,
	                    format='%(asctime)s %(levelname)-7s %(message)s')
	
	if args.folder is None:
		folder = filedialog.askdirectory()
	else:
		folder = args.folder
	
	if folder is None or folder == "":
		logging.info("No folder was selected")
		return 0
	start = time.time()
	mic = photo.Microscope(folder=folder)
	dest = mic.move(folder)
	end = time.time()
	total_time = datetime.timedelta(seconds=end-start)
	
	logging.info(f"Done, it took {str(total_time)}, the files are at {str(dest)}")
	return 1


if __name__ == '__main__':
	sys.exit(main())  # pragma: no cover
	