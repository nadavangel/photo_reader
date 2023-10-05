import logging
import sys
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import tkinter.ttk

import photo


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
		folder_selected = filedialog.askdirectory(parent = self._parent, initialdir=self.folder_path)
		if folder_selected:
			self.folderPath.set(folder_selected)
	
	@property
	def folder_path(self):
		return self.folderPath.get()


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

		self.src_folder = FolderSelect(self, "Select source folder")
		self.src_folder.grid(row=0)
		
		self.dest_folder = FolderSelect(self, "Select destention folder")
		self.dest_folder.grid(row=1)
		
		self.name = Input(self, "Name")
		self.name.grid(row=2)
		
		self.progressbar = Progressbar(self, orient='horizontal', mode='indeterminate', length=200)
		
		self.btnRun = Button(self, text="Run", command=self.run)
		self.btnRun.grid(row=3)
		
		self.label = Label(self, text='')
		self.label.grid(row=4)
		
		self.progressbar.grid_forget()
	
	def run(self):
		src = self.src_folder.folderPath.get()
		dst = self.dest_folder.folderPath.get()
		name=self.name.value
		
		if src is None:
			print('Please select source (plate/Spinning disc) folder:')
			folder = filedialog.askdirectory(title="Select source folder")
		else:
			folder = src
		
		if folder is None or folder == "":
			raise Exception("No source folder was selected")
		
		if dst is None:
			print('Please destention folder:')
			dest = filedialog.askdirectory(title="Select destention folder")
		else:
			dest = dst
		
		if dest is None or dest == "":
			raise Exception("No destention folder was selected")

		mic = photo.Microscope(folder=folder)
		self.start_run()
		run_thread = threading.Thread(target=mic.move, kwargs={'dest': dest, "prefix": name})
		run_thread.start()
		
		self.monitor(run_thread=run_thread)
		
		return 0
	
	def start_run(self):
		self.progressbar.grid(row=5)
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
	logging.basicConfig(stream=sys.stdout, level=logging.INFO,
	                    format='%(asctime)s %(levelname)-7s %(message)s')
	window = App()
	window.title("Split To Wells")
	# window.iconbitmap("microscope.ico")

	window.mainloop()

if __name__ == '__main__':
	re = main()
	sys.exit(re)
