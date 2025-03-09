import re
from pathlib import Path
from photo import MicroscopeBase, MicroscopeException, WellPos, Photo, WellName

import logging
logger = logging.getLogger("mylSplitToWells")

class SpinningDisk(MicroscopeBase):
	_nd_files: list[Path]
	regEx_nd = (r"\"?Stage(?P<stage>\d+)\"?,?\s*\"?row:(?P<row>[A-Z]+),?\s*column:(?P<column>\d+),?\s*site:(?P<site>\d+)\"?\s*$")
	regEx_file_name = r"^(?P<batch>[\w\-\_]*)_.*_s(?P<stage>\d+).*\.(tif|stk)$"
	
	def __init__(self, folder: Path | str):
		logger.debug(f"Initializing SpinningDisk with folder: {folder}")
		super().__init__(folder=folder)
		self._find_nd_file()
		
	def _find_nd_file(self):
		logger.info("Searching for .nd files")
		arr = [x for x in self._files_list if x.is_file() and x.suffix == '.nd']
		if len(arr) == 0:
			logger.error(f"No .nd file found in {str(self.path)}")
			raise MicroscopeException(f"There is no nd file in {str(self.path)}")
		self._nd_files = arr
		for file in self._nd_files:
			logger.info(f"Found .nd file: {file}")
			self._files_list.remove(file)
	
	@staticmethod
	def _parse_line(line: str, pos_names: WellName | None = None):
		logger.debug(f"Parsing line: {line}")
		reg = re.match(SpinningDisk.regEx_nd, string=line)
		if reg is None:
			logger.debug("Line did not match regex")
			return (False, -1, None)
		di = reg.groupdict()
		pos = WellPos(row=di["row"], col=int(di["column"]), site=int(di["site"]))
		pos_str = f"{pos.row.upper()}{pos.col}"
		if pos_names is not None and pos_str in pos_names:
			pos.name = pos_names[pos_str]
		logger.debug(f"Parsed position: {pos}")
		return (True, int(di["stage"]), pos)
	
	@staticmethod
	def _parse_file_name(line: str):
		logger.debug(f"Parsing file name: {line}")
		reg = re.match(SpinningDisk.regEx_file_name, string=line)
		if reg is None:
			logger.debug("File name did not match regex")
			return (False, -1, None)
		di = reg.groupdict()
		logger.debug(f"Parsed file name: batch={di['batch']}, stage={di['stage']}")
		return (True, int(di["stage"]), di['batch'])
	
	def _match(self, pos_names: WellName | None = None):
		logger.info("Matching positions with photos")
		stage_dict = {}
		self._pos_photo = {}
		for nd_file in self._nd_files:
			batch = {}
			logger.info(f"Processing .nd file: {nd_file}")
			with open(nd_file, 'r') as f:
				while True:
					raw_line = f.readline()
					if not raw_line:
						break
					line = raw_line.strip()
					suc, stage, pos = self._parse_line(line, pos_names=pos_names)
					if suc:
						batch[stage] = pos
			stage_dict[nd_file.stem] = batch
		
		skiped_files = []
		for file in self._files_list:
			if not file.is_file():
				continue
			file_name = file.name.strip()
			suc, stage, batch = self._parse_file_name(file_name)
			if suc:
				if batch not in stage_dict:
					logger.warning(f"Batch {batch} not found in nd files, skip {file_name}")
					skiped_files.append(file)
					continue
				if stage not in stage_dict[batch]:
					logger.warning(f"Stage {stage} not found in nd files, skip {file_name}")
					skiped_files.append(file)
					continue

				pos = stage_dict[batch][stage]
				pic = Photo(path=file, pos=pos)
				if pos not in self._pos_photo:
					self._pos_photo[pos] = [pic]
				else:
					self._pos_photo[pos].append(pic)
				logger.debug(f"Matched photo {file} to position {pos}")
		if len(skiped_files) > 0:
			logger.info(f"Skipped files: {skiped_files}")
		return skiped_files
					
	