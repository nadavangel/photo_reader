import re
from pathlib import Path

from photo import MicroscopeBase, WellPos, Photo


class Eva(MicroscopeBase):
	regEx_file_name = r"(?P<row>[A-Za-z]+)(?P<col>\d+)[-]*W(?P<well>\d+)[-]*P(?P<pos>\d+)[-]*Z(?P<z>\d+)[-]*T(?P<time>\d+)[-]*(?P<channel>\w+).tif"
	
	def __init__(self, folder: Path | str):
		data_folder = str(self.path_value(folder) / 'data')
		super().__init__(folder=data_folder)
	
	@staticmethod
	def _parse_file_name(line: str):
		reg = re.match(Eva.regEx_file_name, string=line)
		if reg is None:
			return (False, None)
		di = reg.groupdict()
		pos = WellPos(row=di["row"], col=int(di["col"]), site=int(di["pos"]))
		return (True, pos)
	
	def _match(self):
		self._pos_photo = {}
		
		for file in self._files_list:
			if not file.is_file():
				continue
			file_name = file.name.strip()
			suc, pos = self._parse_file_name(file_name)
			if suc:
				pic = Photo(path=file, pos=pos)
				if pos not in self._pos_photo:
					self._pos_photo[pos] = [pic]
				else:
					self._pos_photo[pos].append(pic)
					