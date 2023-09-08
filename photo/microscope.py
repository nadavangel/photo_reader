import abc

from photo.photo import Photo, WellPos
from pathlib import Path


class MicroscopeException(Exception):
	pass


class Microscope(abc.ABC):
	_path: Path
	_files_list: list[Path]
	_pos_photo: dict[WellPos, list[Photo]]
	
	def __init__(self, folder: Path | str):
		self.path = folder
		self._fill_files()
	
	def _fill_files(self):
		self._files_list = list(self.path.iterdir())
	
	@abc.abstractmethod
	def _match(self):
		pass
	
	def move(self, dest: Path | str):
		self._match()
		base_dest_dir = self.path_value(dest)
		if not base_dest_dir.is_dir():
			raise MicroscopeException(f"{str(base_dest_dir)} is not a folder")
		dest_dir = base_dest_dir.absolute() / 'out'
		dest_dir.mkdir(parents=True, exist_ok=False)
		for pos in self._pos_photo:
			pos_dir = dest_dir / str(pos)
			pos_dir.mkdir(parents=True, exist_ok=True)
			for file in self._pos_photo[pos]:
				print(f"{str(pos)}: {str(file.path)}")
				file.copy(pos_dir)
	
	@property
	def path(self) -> Path:
		return self._path
	
	@staticmethod
	def path_value(value: Path | str) -> Path:
		if type(value) is str:
			val = Path(value)
		elif type(value) is Path:
			val = value
		else:
			raise TypeError("Path is not from type 'Path'")
		
		if not val.is_dir():
			raise TypeError(f"Path \"{str(val)}\", is not a dirctory.")
		return val
	
	@path.setter
	def path(self, value: Path | str):
		self._path = self.path_value(value)
