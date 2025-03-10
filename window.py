import logging
from logging import FileHandler
import sys
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

import photo
from photo import WellNameTxt
import subprocess

logger = logging.getLogger("mylSplitToWells")
class FolderSelect(Frame):
	def __init__(self, parent=None, folderDescription="", **kw):
		Frame.__init__(self, master=parent, **kw)
		self._parent = parent
		self.folderPath = StringVar()
		self.lblName = Label(self, text=folderDescription)
		self.lblName.grid(row=0, column=0)
		self.entPath = Entry(self, textvariable=self.folderPath)
		self.entPath.grid(row=0, column=1)
		self.btnFind = Button(self, text="Browse Folder", command=self.setFolderPath)
		self.btnFind.grid(row=0, column=2)
	
	def setFolderPath(self):
		folder_selected = filedialog.askdirectory(parent=self._parent, initialdir=self.folder_path)
		if folder_selected:
			self.folderPath.set(folder_selected)
	
	@property
	def folder_path(self):
		return self.folderPath.get()


class Multitext(Frame):
	def __init__(self, parent=None, title="", **kw):
		Frame.__init__(self, master=parent, **kw)
		self._parent = parent
		self.folderPath = StringVar()
		self.lblName = Label(self, text=title)
		self.lblName.grid(row=0, column=0)
		
		self.text = ScrolledText(self, wrap=WORD, **kw)
		self.text.grid(row=0, column=1)
	
	@property
	def value(self):
		return self.text.get("1.0", END)
	
	@staticmethod
	def selectAllOperation(event, textWidget):
		if (isinstance(textWidget, ScrolledText)):
			lines = textWidget.get("1.0", "end").split('\n')
			lines.pop()
		else:
			event.widget.event_generate("<<SelectAll>>")
			return "break"
		
		textWidget.tag_remove(SEL, '1.0', 'end')
		for idx, line in enumerate(lines):
			textWidget.tag_add(SEL, f'{idx+1}.0', f'{idx+1}.{len(line)}')
		


class Input(Frame):
	def __init__(self, parent=None, description="", **kw):
		Frame.__init__(self, master=parent, **kw)
		self.lblName = Label(self, text=description)
		self.lblName.grid(row=0, column=0)
		self.entPath = Entry(self)
		self.entPath.grid(row=0, column=1)
	
	@property
	def value(self):
		return self.entPath.get()


class App(Tk):
	def __init__(self):
		super().__init__()
		self.resizable(0, 0)
		self._row = 0
		self.src_folder = FolderSelect(self, "Select source folder")
		self.src_folder.grid(row=self._row)
		self._row += 1
		
		self.dest_folder = FolderSelect(self, "Select destination folder")
		self.dest_folder.grid(row=self._row)
		self._row += 1
		
		self.name = Input(self, "Name")
		self.name.grid(row=self._row)
		self._row += 1
		
		self.material = Multitext(self, title="Material info", width=20, height=3)
		self.material.grid(row=self._row)
		self._row += 1
		
		self.createSubdirValue = BooleanVar()
		self.createSubdirCheckbox = Checkbutton(self, text='Create subdir', variable=self.createSubdirValue,
		                                        onvalue=True, offvalue=False)
		#self.createSubdirCheckbox.select()
		self.createSubdirCheckbox.grid(row=self._row)
		self._row += 1

		self.file_prefix = Input(self, "File prefix")
		self.file_prefix.grid(row=self._row)
		self._row += 1
		
		self.btnRun = Button(self, text="Run", command=self.run)
		self.btnRun.grid(row=self._row)
		self._row += 1
		
		self.label = Label(self, text='')
		self.label.grid(row=self._row)
		self._row += 1
		
		self.progressbar = Progressbar(self, orient='horizontal', mode='indeterminate', length=200)
		self.progressbar.grid_forget()
		
		self.bind_all("<Key>", self._onKeyRelease, "+")
	
	@staticmethod
	def _onKeyRelease(event):
		ctrl = (event.state & 0x4) != 0
		if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
			event.widget.event_generate("<<Cut>>")
			return "break"
		
		if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
			event.widget.event_generate("<<Paste>>")
			return "break"
		
		if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
			event.widget.event_generate("<<Copy>>")
			return "break"
		
		if (event.keycode == 65 and ctrl):  # ctrl+a
			Multitext.selectAllOperation(event=event, textWidget=event.widget)
			return "break"
			
	def run(self):
		src = self.src_folder.folderPath.get()
		dst = self.dest_folder.folderPath.get()
		name = self.name.value
		file_prefix = self.file_prefix.value
		
		if src is None:
			print('Please select source (plate/Spinning disc) folder:')
			folder = filedialog.askdirectory(title="Select source folder")
		else:
			folder = src
		
		if folder is None or folder == "":
			raise Exception("No source folder was selected")
		
		if dst is None:
			print('Please select destination folder:')
			dest = filedialog.askdirectory(title="Select destination folder")
		else:
			dest = dst
		
		if dest is None or dest == "":
			raise Exception("No destination folder was selected")
		
		well_name = None
		if self.material.value != "":
			well_name = WellNameTxt(buff=self.material.value)
		
		mic = photo.Microscope(folder=folder)
		self.start_run()
		run_thread = threading.Thread(target=mic.move,
		                              kwargs={
			                              'dest': dest,
			                              "prefix": name,
			                              "create_dubdir": self.createSubdirValue.get(),
			                              "pos_names": well_name,
										  "file_prefix": file_prefix
		                              })
		run_thread.daemon = True
		run_thread.start()
		
		self.monitor(run_thread=run_thread)
		
		return 0
	
	def start_run(self):
		self.progressbar.grid(row=self._row)
		self.progressbar.start(20)
		self.btnRun.config(state=DISABLED)
	
	def stop_run(self):
		self.progressbar.stop()
		self.progressbar.grid_forget()
		self.btnRun.config(state=NORMAL)
		messagebox.showinfo(title="Done", message="Done")
	
	def monitor(self, run_thread):
		if run_thread.is_alive():
			self.after(100, lambda: self.monitor(run_thread))
		else:
			self.stop_run()


def main() -> int:  # pragma: no cover
	formatter_stdot = logging.Formatter(
		'%(asctime)s %(levelname)-7s %(message)s')
	formatter_file = logging.Formatter(
		'%(asctime)s.%(msecs)03d %(levelname)-7s [%(funcName)-20s] [%(filename)25s:%(lineno)-4d] %(message)s',
		datefmt ='%d/%m/%Y %H:%M:%S')
	logger.setLevel(logging.DEBUG)

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)
	stream_handler.setFormatter(formatter_stdot)

	logFilePath = "SplitToWells.log"
	file_handler = FileHandler(logFilePath, encoding='utf-8',mode='w')
	file_handler.setFormatter(formatter_file)
	file_handler.setLevel(logging.DEBUG)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)

						
	window = App()
	window.title("Split To Wells")
	# window.iconbitmap("microscope.ico")
	
	logger.info("Starting SplitToWells")
	window.mainloop()


if __name__ == '__main__':
	re = main()
	sys.exit(re)
