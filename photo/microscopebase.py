import abc
import logging

from photo.photo import Photo
from photo.wells import WellPos, WellName
from pathlib import Path, WindowsPath


class MicroscopeException(Exception):
	pass


class MicroscopeBase(abc.ABC):
	_path: Path
	_files_list: list[Path]
	_pos_photo: dict[WellPos, list[Photo]]
	
	def __init__(self, folder: Path | str):
		self.path = folder
		self._fill_files()
	
	def _fill_files(self):
		self._files_list = list(self.path.iterdir())
	
	@abc.abstractmethod
	def _match(self, pos_names: WellName | None = None):
		pass
	
	def move(self, dest: Path | str, prefix : str = "", create_dubdir:bool = True, pos_names: WellName | None = None):
		base_dest_dir = self.path_value(dest)
		if not base_dest_dir.is_dir():
			raise MicroscopeException(f"{str(base_dest_dir)} is not a folder")
		dest_dir = base_dest_dir.absolute() / 'out'
		dest_dir.mkdir(parents=True, exist_ok=True)
		logging.info(f"Create {str(dest_dir)}")
		self._match(pos_names)
		
		for pos in self._pos_photo:
			if create_dubdir:
				pos_dir = dest_dir / str(pos)
				pos_dir.mkdir(parents=True, exist_ok=True)
				logging.debug(f"Create {str(pos_dir)}")
				pos_prefix = prefix
			else:
				pos_dir = dest_dir
				pos_prefix = f"{str(pos)}_{prefix}"
				
			for file in self._pos_photo[pos]:
				file.copy(pos_dir, prefix=pos_prefix)
				logging.info(f"Copy {str(file.path.name)} to {str(pos)}")
		return dest_dir
	
	@property
	def path(self) -> Path:
		return self._path
	
	@staticmethod
	def path_value(value: Path | str) -> Path:
		if type(value) is str:
			val = Path(value)
		elif type(value) is Path or type(value) is WindowsPath:
			val = value
		else:
			raise TypeError("Path is not from type 'Path'")
		
		if not val.is_dir():
			raise TypeError(f"Path \"{str(val)}\", is not a dirctory.")
		return val
	
	@path.setter
	def path(self, value: Path | str):
		self._path = self.path_value(value)
