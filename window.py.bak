import logging
from logging import FileHandler
import sys
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

import photo
from photo import WellNameTxt, MicroscopeException, get_exception_location
import configparser
import datetime

DEFAULT_CONFIG_FILE = ".config.ini"

logger = logging.getLogger("mylSplitToWells")


class FolderSelect(Frame):
    """
    A tkinter Frame for selecting and displaying a folder path.

    Provides a label, an entry field for the path, and a button to browse
    for a directory using a file dialog.
    """
    def __init__(self, parent=None, folderDescription="", path: str = "", **kw):
        """
        Initialize the FolderSelect frame.

        Args:
            parent: The parent tkinter widget.
            folderDescription: The label text describing the folder selection.
            path: The initial path value.
            **kw: Additional keyword arguments for the Frame.
        """
        Frame.__init__(self, master=parent, **kw)
        self._parent = parent
        self.folderPath = StringVar()
        self.folderPath.set(path)
        self.lblName = Label(self, text=folderDescription)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.folderPath)
        self.entPath.grid(row=0, column=1)
        self.btnFind = Button(self, text="Browse Folder", command=self.setFolderPath)
        self.btnFind.grid(row=0, column=2)

    def setFolderPath(self):
        """
        Open a directory selection dialog and update the folder path.
        """
        folder_selected = filedialog.askdirectory(
            parent=self._parent, initialdir=self.folder_path
        )
        if folder_selected:
            self.folderPath.set(folder_selected)

    @property
    def folder_path(self):
        """
        Get the current folder path.

        Returns:
            The string representing the folder path.
        """
        return self.folderPath.get()


class Multitext(Frame):
    """
    A tkinter Frame for displaying and editing multi-line text.

    Provides a label and a scrolled text area.
    """
    def __init__(self, parent=None, title="", **kw):
        """
        Initialize the Multitext frame.

        Args:
            parent: The parent tkinter widget.
            title: The label text describing the text area.
            **kw: Additional keyword arguments for the Frame and ScrolledText.
        """
        Frame.__init__(self, master=parent, **kw)
        self._parent = parent
        self.folderPath = StringVar()
        self.lblName = Label(self, text=title)
        self.lblName.grid(row=0, column=0)

        self.text = ScrolledText(self, wrap=WORD, **kw)
        self.text.grid(row=0, column=1)

    @property
    def value(self):
        """
        Get the current text content.

        Returns:
            The string content of the scrolled text area.
        """
        return self.text.get("1.0", END)

    @staticmethod
    def selectAllOperation(event, textWidget):
        """
        Select all text in the given widget if it is a ScrolledText instance.

        Args:
            event: The triggering event.
            textWidget: The widget to select text from.

        Returns:
            "break" to prevent further event processing if successful, None otherwise.
        """
        if isinstance(textWidget, ScrolledText):
            lines = textWidget.get("1.0", "end").split("\n")
            lines.pop()
        else:
            event.widget.event_generate("<<SelectAll>>")
            return "break"

        textWidget.tag_remove(SEL, "1.0", "end")
        for idx, line in enumerate(lines):
            textWidget.tag_add(SEL, f"{idx + 1}.0", f"{idx + 1}.{len(line)}")


class Input(Frame):
    """
    A tkinter Frame for receiving single-line text input.

    Provides a label and an entry field.
    """
    def __init__(self, parent=None, description="", **kw):
        """
        Initialize the Input frame.

        Args:
            parent: The parent tkinter widget.
            description: The label text describing the input field.
            **kw: Additional keyword arguments for the Frame.
        """
        Frame.__init__(self, master=parent, **kw)
        self.lblName = Label(self, text=description)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self)
        self.entPath.grid(row=0, column=1)

    @property
    def value(self):
        """
        Get the current input value.

        Returns:
            The string content of the entry field.
        """
        return self.entPath.get()


class App(Tk):
    """
    The main application window (Tkinter based).

    Manages the UI layout, configuration loading/saving, and the file splitting process.
    """
    def __init__(self, cfg: configparser.ConfigParser = None):
        """
        Initialize the App window.

        Args:
            cfg: The configuration object to load settings from.
        """
        super().__init__()
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._row = 0
        self._cfg = cfg

        self.src_folder = FolderSelect(
            self,
            "Select source folder",
            path=self._cfg.get("Settings", "src_folder", fallback=""),
        )
        self.src_folder.grid(row=self._row)
        self._row += 1

        self.dest_folder = FolderSelect(
            self,
            "Select destination folder",
            path=self._cfg.get("Settings", "dest_folder", fallback=""),
        )
        self.dest_folder.grid(row=self._row)
        self._row += 1

        self.name = Input(self, "Name")
        self.name.grid(row=self._row)
        self._row += 1

        self.material = Multitext(self, title="Material info", width=20, height=3)
        self.material.grid(row=self._row)
        self._row += 1

        self.createSubdirValue = BooleanVar()
        self.createSubdirCheckbox = Checkbutton(
            self,
            text="Create subdir",
            variable=self.createSubdirValue,
            onvalue=True,
            offvalue=False,
        )
        if self._cfg.has_option("Settings", "create_subdir"):
            create_subdir = self._cfg.getboolean(
                "Settings", "create_subdir", fallback=True
            )
            if create_subdir:
                self.createSubdirCheckbox.select()
            else:
                self.createSubdirCheckbox.deselect()
        self.createSubdirCheckbox.grid(row=self._row)
        self._row += 1

        self.file_prefix = Input(self, "File prefix")
        self.file_prefix.grid(row=self._row)
        self._row += 1

        self.btnRun = Button(self, text="Run", command=self.run)
        self.btnRun.grid(row=self._row)
        self._row += 1

        self.label = Label(self, text="")
        self.label.grid(row=self._row)
        self._row += 1

        self.progressbar = Progressbar(
            self, orient="horizontal", mode="indeterminate", length=200
        )
        self.progressbar.grid_forget()

        self.bind_all("<Key>", self._onKeyRelease, "+")

    @staticmethod
    def _onKeyRelease(event):
        """
        Handle key release events for cut, copy, paste, and select-all.

        Args:
            event: The triggering event.
        """
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

        if event.keycode == 65 and ctrl:  # ctrl+a
            Multitext.selectAllOperation(event=event, textWidget=event.widget)
            return "break"

    def run(self):
        """
        Run the file splitting operation in a separate thread.
        """
        src = self.src_folder.folderPath.get()
        dst = self.dest_folder.folderPath.get()
        name = self.name.value
        file_prefix = self.file_prefix.value

        if src is None:
            print("Please select source (plate/Spinning disc) folder:")
            folder = filedialog.askdirectory(title="Select source folder")
        else:
            folder = src

        if folder is None or folder == "":
            logger.error("No source folder was selected")
            return

        if dst is None:
            print("Please select destination folder:")
            dest = filedialog.askdirectory(title="Select destination folder")
        else:
            dest = dst

        if dest is None or dest == "":
            logger.error("No destination folder was selected")
            return

        well_name = None
        if self.material.value != "":
            well_name = WellNameTxt(buff=self.material.value)

        try:
            mic = photo.Microscope(folder=folder)
        except MicroscopeException as e:
            ex_file, ex_line = get_exception_location()
            logger.error(
                f'Error occurred while initializing microscope : "{e}" (at {ex_file}:{ex_line})'
            )
            return
        except TypeError as e:
            ex_file, ex_line = get_exception_location()
            logger.error(
                f'Type error occurred while initializing microscope: "{e}" (at {ex_file}:{ex_line})'
            )
            return

        self.start_run()
        run_thread = threading.Thread(
            target=mic.move,
            kwargs={
                "dest": dest,
                "prefix": name,
                "create_dubdir": self.createSubdirValue.get(),
                "pos_names": well_name,
                "file_prefix": file_prefix,
            },
        )
        run_thread.daemon = True
        run_thread.start()

        self.monitor(run_thread=run_thread)

        return 0

    def start_run(self):
        """
        Show the progress bar and disable the run button.
        """
        self.progressbar.grid(row=self._row)
        self.progressbar.start(20)
        self.btnRun.config(state=DISABLED)

    def stop_run(self):
        """
        Stop the progress bar, re-enable the run button, and show a completion message.
        """
        self.progressbar.stop()
        self.progressbar.grid_forget()
        self.btnRun.config(state=NORMAL)
        messagebox.showinfo(title="Done", message="Done")

    def monitor(self, run_thread):
        """
        Monitor the running thread and stop the UI process upon completion.

        Args:
            run_thread: The thread running the file splitting process.
        """
        if run_thread.is_alive():
            self.after(100, lambda: self.monitor(run_thread))
        else:
            self.stop_run()

    def _save_configuration(self) -> None:
        """
        Save the current UI state to the configuration file.
        """
        if "Settings" not in self._cfg:
            self._cfg["Settings"] = {}
        self._cfg["Settings"]["src_folder"] = self.src_folder.folder_path
        self._cfg["Settings"]["dest_folder"] = self.dest_folder.folder_path
        self._cfg["Settings"]["file_prefix"] = self.file_prefix.value
        self._cfg["Settings"]["name"] = self.name.value
        self._cfg["Settings"]["create_subdir"] = str(
            self.createSubdirValue.get()
        )  # Boolean value
        self._cfg["Settings"]["well_name"] = self.material.value  # Multitext value

        save_cfg(DEFAULT_CONFIG_FILE, self._cfg)

    def on_closing(self):
        """
        Handle the application closing event by saving configuration.
        """
        logger.info("Closing application")
        self._save_configuration()
        self.destroy()


def create_and_read_cfg(path: str) -> configparser.ConfigParser:
    """
    Read configuration from a file or create a default object if the file is missing.

    Args:
        path: The path to the configuration file.

    Returns:
        A configparser.ConfigParser object populated with settings from the file.
    """
    config = configparser.ConfigParser()
    try:
        with open(path, "r", encoding="utf-8") as cfgfile:
            config.read_file(cfgfile)
            logger.debug(f"Configuration loaded from {path}")
    except FileNotFoundError:
        logger.warning(
            f"Configuration file {path} not found. Creating default configuration."
        )
    return config


def save_cfg(path: str, config: configparser.ConfigParser) -> None:
    """
    Save the configuration to a file.

    Includes an update timestamp in the 'Meta' section.

    Args:
        path: The path to the configuration file.
        config: The configuration object to save.
    """
    config["Meta"] = {
        "Update time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(path, "w", encoding="utf-8") as cfgfile:
            config.write(cfgfile)
            logger.debug(f"Configuration saved to '{path}', contents:\n{config}")
    except Exception as e:
        ex_file, ex_line = get_exception_location()
        logger.error(
            f"Error occurred while saving configuration to '{path}': {e} (at {ex_file}:{ex_line})"
        )


def main() -> int:
    """
    Main entry point for the SplitToWells GUI application.

    Configures logging, loads settings, initializes the application window,
    and starts the main GUI loop.

    Returns:
        0.
    """
    formatter_stdot = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    formatter_file = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)-7s [%(funcName)-20s] [%(filename)25s:%(lineno)-4d] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter_stdot)

    logFilePath = "SplitToWells.log"
    file_handler = FileHandler(logFilePath, encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter_file)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    config = create_and_read_cfg(DEFAULT_CONFIG_FILE)

    window = App(cfg=config)
    window.title("Split To Wells")
    # window.iconbitmap("microscope.ico")

    logger.info("Starting SplitToWells")
    window.mainloop()
    return 0


if __name__ == "__main__":
    re = main()
    sys.exit(re)
