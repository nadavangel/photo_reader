from photo import Eva, MicroscopeBase, SpinninDick


class Microscope():
	def __new__(cls, *args, **kwargs):
		folder = MicroscopeBase.path_value(kwargs.get('folder'))
		data_dir = folder / 'data'
		if data_dir.is_dir():
			cls = Eva
		else:
			cls = SpinninDick
			
		return cls(folder=folder)
