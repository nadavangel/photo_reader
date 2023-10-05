import abc
from dataclasses import field, dataclass
from pathlib import Path, WindowsPath


@dataclass
class WellPos():
	row: str  # A-P
	col: int
	site: int
	name: str = field(default="")
	
	@classmethod
	def create(cls, pos: tuple):
		if type(pos) is not tuple:
			raise TypeError("Pos is not tuple")
		if len(pos) == 3:
			site = pos[2]
		else:
			site = 1
		return cls(row=pos[0], col=pos[1], site=site)
	
	def samePos(self, other):
		return self.row == other.row and self.col == other.col
	
	def __hash__(self):
		return hash(f"{self.row}{self.col}{self.site}{self.name}")
	
	def __str__(self) -> str:
		if self.name != "":
			name = "_" + self.name
		else:
			name = self.name
		return f"{self.row}{self.col:02}{name}"


class WellName():
	_info: dict[str, str]
	
	def __init__(self):
		super().__init__()
		self._info = {}
		self._fill()
	
	def __setitem__(self, key: str, value: str):
		self._info[key.upper()] = value
	
	def __getitem__(self, item: str):
		return self._info[item]
	
	def __contains__(self, item:str):
		return item in self._info

	@abc.abstractmethod
	def _fill(self):
		pass

class WellNameTxt(WellName):
	_buff: str
	_delimiter: str
	
	def __init__(self, buff: str, delimiter: str = '\t'):
		self._buff = buff
		self._delimiter = delimiter
		super().__init__()
		
	def _fill(self):
		lines = self._buff.splitlines()
		header = False
		for raw_line in lines:
			if not header:
				header = True
				continue
			line = raw_line.strip()
			if not line or line.count(self._delimiter) < 1:
				continue
			pos_srt, name = line.split(sep=self._delimiter, maxsplit=2)
			self[pos_srt] = name

