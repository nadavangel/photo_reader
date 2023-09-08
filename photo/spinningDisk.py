import re
from pathlib import Path
from photo.photo import WellPos, Photo

from photo.microscope import Microscope, MicroscopeException


class SpinninDick(Microscope):
	_nd_files: list[Path]
	regEx_nd = (r"\"?Stage(?P<stage>\d+)\"?,?\s*\"?row:(?P<row>[A-Z]+),?\s*column:(?P<column>\d+),?\s*site:(?P<site>\d+)\"?\s*$")
	regEx_file_name = r"^(?P<batch>\w*)_.*_s(?P<stage>\d+).tif$"
	
	def __init__(self, folder: Path | str):
		super().__init__(folder=folder)
		self._find_nd_file()
		
	def _find_nd_file(self):
		arr = [x for x in self._files_list if x.is_file() and x.suffix == '.nd']
		if len(arr) == 0:
			raise MicroscopeException(f"There is no nd file in {str(self.path)}")
		self._nd_files = arr
		for file in self._nd_files:
			self._files_list.remove(file)
	
	@staticmethod
	def _parse_line(line: str):
		reg = re.match(SpinninDick.regEx_nd, string=line)
		if reg is None:
			return (False, -1, None)
		di = reg.groupdict()
		pos = WellPos(row=di["row"], col=int(di["column"]), site=int(di["site"]))
		return (True, int(di["stage"]), pos)
	
	@staticmethod
	def _parse_file_name(line: str):
		reg = re.match(SpinninDick.regEx_file_name, string=line)
		if reg is None:
			return (False, -1, None)
		di = reg.groupdict()
		return (True, int(di["stage"]), di['batch'])
	
	def _match(self):
		stage_dict = {}
		self._pos_photo = {}
		for nd_file in self._nd_files:
			batch = {}
			with open(nd_file, 'r') as f:
				while True:
					raw_line = f.readline()
					if not raw_line:
						break
					line = raw_line.strip()
					suc, stage, pos = self._parse_line(line)
					if suc:
						batch[stage] = pos
			stage_dict[nd_file.stem] = batch
					
		for file in self._files_list:
			if not file.is_file():
				continue
			file_name = file.name.strip()
			suc, stage, batch = self._parse_file_name(file_name)
			if suc:
				pos = stage_dict[batch][stage]
				pic = Photo(path=file, pos=pos)
				if pos not in self._pos_photo:
					self._pos_photo[pos] = [pic]
				else:
					self._pos_photo[pos].append(pic)
					
	