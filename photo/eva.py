import re
from pathlib import Path

from photo import MicroscopeBase, WellPos, Photo, WellName
import logging
logger = logging.getLogger("mylSplitToWells")

class Eva(MicroscopeBase):
	regEx_file_name = r"(?P<row>[A-Za-z]+)(?P<col>\d+)[-]*W(?P<well>\d+)[-]*P(?P<pos>\d+)[-]*Z(?P<z>\d+)[-]*T(?P<time>\d+)[-]*(?P<channel>\w+).tif"
	
	def __init__(self, folder: Path | str):
		data_folder = str(self.path_value(folder) / 'data')
		logger.debug(f"Initializing Eva with data folder: {data_folder}")
		super().__init__(folder=data_folder)
	
	@staticmethod
	def _parse_file_name(line: str, pos_names: WellName | None = None):
		logger.debug(f"Parsing file name: {line}")
		reg = re.match(Eva.regEx_file_name, string=line)
		if reg is None:
			logger.warning(f"Failed to parse file name: {line}")
			return (False, None)
		di = reg.groupdict()
		pos = WellPos(row=di["row"], col=int(di["col"]), site=int(di["pos"]))
		pos_str = f"{pos.row.upper()}{pos.col}"
		if pos_names is not None and pos_str in pos_names:
			pos.name = pos_names[pos_str]
		logger.debug(f"Parsed position: {pos}")
		return (True, pos)
	
	def _match(self, pos_names: WellName | None = None):
		self._pos_photo = {}
		skiped_files = []
		logger.info("Matching files to positions")
		for file in self._files_list:
			if not file.is_file():
				logger.warning(f"Skipping non-file: {file}")
				skiped_files.append(file)
				continue
			file_name = file.name.strip()
			suc, pos = self._parse_file_name(file_name, pos_names=pos_names)
			if suc:
				pic = Photo(path=file, pos=pos)
				if pos not in self._pos_photo:
					self._pos_photo[pos] = [pic]
				else:
					self._pos_photo[pos].append(pic)
				logger.debug(f"Matched file {file_name} to position {pos}")
			else:
				logger.warning(f"Failed to match file: {file_name}")
		if len(skiped_files) > 0:
			logger.info(f"Skipped files: {skiped_files}")
		return skiped_files