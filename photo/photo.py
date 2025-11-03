import shutil
from pathlib import Path
import re

from photo.wells import WellPos
import logging
logger = logging.getLogger("mylSplitToWells")
class Photo():
	_well: WellPos
	_name: str
	_path: Path
	
	def __init__(self, path: Path, pos: WellPos | tuple = None):
		if pos is not None:
			self.pos = pos
		
		self._path = path
		logger.debug(f"Photo initialized with path: {path} and pos: {pos}")
	
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
		logger.debug(f"Position set to: {self._well}")
	
	def set_well(self, row: str, col: int, site=1):
		self._well = WellPos(row=row, col=col, site=site)
		logger.debug(f"Well set to: {self._well}")
	
	@property
	def name(self):
		return self._name
	
	@name.setter
	def name(self, value: str):
		self._name = value
		logger.debug(f"Name set to: {self._name}")
	
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
		logger.debug(f"Path set to: {self._path}")

	def copy(self, dest: Path, new_name:str = "", prefix : str = ""):
		if new_name != "":
			name = new_name
		else:
			name = self.path.stem
			
		if prefix != "":
			name = prefix + "_" + name
			
		full_name = sanitize_path(f"{name}{self.path.suffix}")
		new_path = dest / full_name
		shutil.copy2(self.path, new_path)
		logger.info(f"Copied file to: \"{new_path}\"")

def sanitize_path(path:str) -> str:
	"""
	Sanitize a file path by replacing invalid characters with underscores. For Windows file systems.
	:param path: The file path to sanitize.
	:return: The sanitized file path.
	"""
	# Forbidden characters in Windows
	forbidden = r'[<>:"/\\|?*]'
	sanitized = re.sub(forbidden, '_', path)
	# Remove trailing spaces and dots
	sanitized = re.sub(r'[\s.]+$', '_', sanitized)
	# Reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
	reserved = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$', re.IGNORECASE)
	if reserved.match(sanitized):
		sanitized += '_'
	if sanitized != path:
		print(f"Warning: Invalid characters found in path '{path}'. Replacing with '_'.")
	return sanitized
