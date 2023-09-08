import logging
import sys
from tkinter import *
from tkinter import filedialog, messagebox

import photo


class FolderSelect(Frame):
	def __init__(self, parent=None, folderDescription="", **kw):
		Frame.__init__(self, master=parent, **kw)
		self.folderPath = StringVar()
		self.lblName = Label(self, text=folderDescription)
		self.lblName.grid(row=0, column=0)
		self.entPath = Entry(self, textvariable=self.folderPath)
		self.entPath.grid(row=0, column=1)
		self.btnFind = Button(self, text="Browse Folder", command=self.setFolderPath)
		self.btnFind.grid(row=0, column=2)
	
	def setFolderPath(self):
		folder_selected = filedialog.askdirectory()
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

def run(src, dst, name):
	if src is None:
		print('Please select source (plate/Spinning disc) folder:')
		folder = filedialog.askdirectory(title="Select source folder")
	else:
		folder = src
	
	if folder is None or folder == "":
		raise Exception("No source folder was selected")
		return 0
	
	if dst is None:
		print('Please destention folder:')
		dest = filedialog.askdirectory(title="Select destention folder")
	else:
		dest = dst
	
	if dest is None or dest == "":
		raise Exception("No destention folder was selected")
		return 0
	
	mic = photo.Microscope(folder=folder)
	dest = mic.move(dest, prefix=name)
	messagebox.showinfo(title="Done", message="Done")
	
	return 0

def main() -> int:  # pragma: no cover
	logging.basicConfig(stream=sys.stdout, level=logging.INFO,
	                    format='%(asctime)s %(levelname)-7s %(message)s')
	window = Tk()
	window.title("Split To Wells")
	# window.iconbitmap("microscope.ico")
	
	src_folder = FolderSelect(window, "Select source folder")
	src_folder.grid(row=0)
	
	dest_folder = FolderSelect(window, "Select destention folder")
	dest_folder.grid(row=1)
	
	name = Input(window, "Name")
	name.grid(row=2)
	
	btnRun = Button(window, text="Run", command=lambda: run(src = src_folder.folderPath.get(), dst=dest_folder.folderPath.get(), name=name.value))
	btnRun.grid(row=3)
	
	window.mainloop()

if __name__ == '__main__':
	re = main()
	sys.exit(re)