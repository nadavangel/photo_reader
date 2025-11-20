import abc

from photo.photo import Photo
from photo.wells import WellPos, WellName
from pathlib import Path, WindowsPath
import logging
import traceback
from typing import Tuple
import sys
logger = logging.getLogger("mylSplitToWells")
class MicroscopeException(Exception):
	pass


def get_exception_location() -> Tuple[str, int]:
	exc_type, exc_value, exc_traceback = sys.exc_info()

	last_frame = traceback.extract_tb(exc_traceback)[-1]
    
	full_filename = last_frame.filename
	lineno = last_frame.lineno
	function_name = last_frame.name
	line_of_code = last_frame.line
	filename = Path(full_filename).name
	return (filename, lineno)

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
	
	def move(self, *args, **kwargs):
		try:
			return self._move(*args, **kwargs)
		except MicroscopeException as e:
			ex_file, ex_line = get_exception_location()
			logger.error(f"Error occurred while moving files: {e} (at {ex_file}:{ex_line})")
			return None
		except TypeError as e:
			ex_file, ex_line = get_exception_location()
			logger.error(f"Type error occurred while moving files: {e} (at {ex_file}:{ex_line})")
			return None


	def _move(self, dest: Path | str, prefix : str = "", create_dubdir:bool = True, pos_names: WellName | None = None, file_prefix: str = ""):
		base_dest_dir = self.path_value(dest)
		if not base_dest_dir.is_dir():
			raise MicroscopeException(f"{str(base_dest_dir)} is not a folder")
		dest_dir = base_dest_dir.absolute() / 'out'
		dest_dir.mkdir(parents=True, exist_ok=True)
		logger.info(f"Create {str(dest_dir)}")
		skipped_files = self._match(pos_names)
		
		for pos in self._pos_photo:
			if create_dubdir:
				pos_dir = dest_dir / str(pos)
				pos_dir.mkdir(parents=True, exist_ok=True)
				logger.debug(f"Create {str(pos_dir)}")
				pos_prefix = prefix
			else:
				pos_dir = dest_dir
				pos_prefix = f"{str(pos)}_{prefix}"

			if file_prefix:
				pos_prefix = f"{file_prefix}_{pos_prefix}"
				
			for file in self._pos_photo[pos]:
				file.copy(pos_dir, prefix=pos_prefix)
				logger.info(f"Copy \"{str(file.path.name)}\" to {str(pos)}")
		
		if len(skipped_files) > 0:
			skipped_files_names = ', '.join([file.name for file in skipped_files])
			logger.warning(f"Skipped {len(skipped_files)} file{'s' if len(skipped_files) > 1 else ''}: {skipped_files_names}")

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
