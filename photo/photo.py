import shutil
from pathlib import Path

from photo.wells import WellPos


class Photo():
	_well: WellPos
	_name: str
	_path: Path
	
	def __init__(self, path: Path, pos: WellPos | tuple = None):
		if pos is not None:
			self.pos = pos
		
		self._path = path
	
	@property
	def pos(self):
		return self._well
	
	@pos.setter
	def pos(self, pos: WellPos | tuple):
		if type(pos) is tuple:
			self._well = WellPos.create(pos)
		elif type(pos) is WellPos:
			self._well = pos
		else:
			raise TypeError("pos is not a WellPos or tuple")
	
	def set_well(self, row: str, col: int, site=1):
		self._well = WellPos(row=row, col=col, site=site)
	
	@property
	def name(self):
		return self._name
	
	@name.setter
	def name(self, value: str):
		self._name = value
	
	@property
	def path(self):
		return self._path
	
	@path.setter
	def path(self, value: Path | str):
		if type(value) is str:
			val = Path(value)
		elif type(value) is Path:
			val = value
		else:
			raise TypeError("Path is not from type 'Path'")
		
		if not val.is_file():
			raise TypeError(f"Path \"{str(val)}\", is not a file.")
		self._path = val

	def copy(self, dest: Path, new_name:str = "", prefix : str = ""):
		if new_name != "":
			name = new_name
		else:
			name = self.path.stem
			
		if prefix != "":
			name = prefix + "_" + name
			
		new_path = dest / name
		shutil.copy(self.path, new_path)
