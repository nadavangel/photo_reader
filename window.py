"""
This module contains the GUI application for splitting photos into wells.
"""

from __future__ import annotations

import configparser
import datetime
import logging
import sys
import threading
import tkinter as tk
import typing
from logging import FileHandler
from tkinter import DISABLED, END, NORMAL, SEL, WORD, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Progressbar

from photo.microscopebase import MicroscopeException, get_exception_location
from photo.utils import Microscope
from photo.wells import WellNameTxt

DEFAULT_CONFIG_FILE = ".config.ini"

logger = logging.getLogger("mylSplitToWells")


class FolderSelect(tk.Frame):
    """
    A tkinter Frame for selecting and displaying a folder path.

    Provides a label, an entry field for the path, and a button to browse
    for a directory using a file dialog.
    """

    def __init__(self, parent=None, folder_description="", path: str = "", **kw):
        """
        Initialize the FolderSelect frame.

        Args:
            parent: The parent tkinter widget.
            folder_description: The label text describing the folder selection.
            path: The initial path value.
            **kw: Additional keyword arguments for the Frame.
        """
        tk.Frame.__init__(self, master=parent, **kw)
        self._parent = parent
        self.folder_path_var = tk.StringVar()
        self.folder_path_var.set(path)
        self.lbl_name = tk.Label(self, text=folder_description)
        self.lbl_name.grid(row=0, column=0)
        self.ent_path = tk.Entry(self, textvariable=self.folder_path_var)
        self.ent_path.grid(row=0, column=1)
        self.btn_find = tk.Button(self, text="Browse Folder", command=self.set_folder_path)
        self.btn_find.grid(row=0, column=2)

    def set_folder_path(self):
        """
        Open a directory selection dialog and update the folder path.
        """
        folder_selected = filedialog.askdirectory(parent=self._parent, initialdir=self.folder_path)
        if folder_selected:
            self.folder_path_var.set(folder_selected)

    @property
    def folder_path(self):
        """
        Get the current folder path.

        Returns:
            The string representing the folder path.
        """
        return self.folder_path_var.get()


class Multitext(tk.Frame):
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
        tk.Frame.__init__(self, master=parent, **kw)
        self._parent = parent
        self.lbl_name = tk.Label(self, text=title)
        self.lbl_name.grid(row=0, column=0)

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
    def select_all_operation(event, text_widget):
        """
        Select all text in the given widget if it is a ScrolledText instance.

        Args:
            event: The triggering event.
            text_widget: The widget to select text from.

        Returns:
            "break" to prevent further event processing if successful, None otherwise.
        """
        if isinstance(text_widget, ScrolledText):
            lines = text_widget.get("1.0", "end").split("\n")
            lines.pop()
        else:
            event.widget.event_generate("<<SelectAll>>")
            return "break"

        text_widget.tag_remove(SEL, "1.0", "end")
        for idx, line in enumerate(lines):
            text_widget.tag_add(SEL, f"{idx + 1}.0", f"{idx + 1}.{len(line)}")
        return "break"


class Input(tk.Frame):
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
        tk.Frame.__init__(self, master=parent, **kw)
        self.lbl_name = tk.Label(self, text=description)
        self.lbl_name.grid(row=0, column=0)
        self.ent_path = tk.Entry(self)
        self.ent_path.grid(row=0, column=1)

    @property
    def value(self):
        """
        Get the current input value.

        Returns:
            The string content of the entry field.
        """
        return self.ent_path.get()


class AppUI:
    """
    A container for the UI components of the application.
    """

    def __init__(self, master, cfg):
        row = 0
        self.src_folder = FolderSelect(
            master,
            "Select source folder",
            path=cfg.get("Settings", "src_folder", fallback=""),
        )
        self.src_folder.grid(row=row)
        row += 1

        self.dest_folder = FolderSelect(
            master,
            "Select destination folder",
            path=cfg.get("Settings", "dest_folder", fallback=""),
        )
        self.dest_folder.grid(row=row)
        row += 1

        self.name = Input(master, "Name")
        self.name.grid(row=row)
        row += 1

        self.material = Multitext(master, title="Material info", width=20, height=3)
        self.material.grid(row=row)
        row += 1

        self.create_subdir_value = tk.BooleanVar()
        self.create_subdir_checkbox = tk.Checkbutton(
            master,
            text="Create subdir",
            variable=self.create_subdir_value,
            onvalue=True,
            offvalue=False,
        )
        if cfg.has_option("Settings", "create_subdir"):
            create_subdir = cfg.getboolean("Settings", "create_subdir", fallback=True)
            if create_subdir:
                self.create_subdir_checkbox.select()
            else:
                self.create_subdir_checkbox.deselect()
        self.create_subdir_checkbox.grid(row=row)
        row += 1

        self.file_prefix = Input(master, "File prefix")
        self.file_prefix.grid(row=row)
        row += 1

        self.btn_run = tk.Button(master, text="Run")  # command is set later
        self.btn_run.grid(row=row)
        row += 1

        self.label = tk.Label(master, text="")
        self.label.grid(row=row)
        row += 1

        self.progressbar = Progressbar(master, orient="horizontal", mode="indeterminate", length=200)
        self.row_count = row


class App(tk.Tk):
    """
    The main application window (Tkinter based).

    Manages the UI layout, configuration loading/saving, and the file splitting process.
    """

    def __init__(self, cfg: typing.Optional[configparser.ConfigParser] = None):
        """
        Initialize the App window.

        Args:
            cfg: The configuration object to load settings from.
        """
        super().__init__()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._cfg = cfg
        self.ui = AppUI(self, self._cfg)
        self.ui.btn_run.config(command=self.run)

        self.bind_all("<Key>", self._on_key_release, "+")

    @staticmethod
    def _on_key_release(event):
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
            Multitext.select_all_operation(event=event, text_widget=event.widget)
            return "break"
        return None

    def run(self):
        """
        Run the file splitting operation in a separate thread.
        """
        src = self.ui.src_folder.folder_path
        dst = self.ui.dest_folder.folder_path
        name = self.ui.name.value
        file_prefix = self.ui.file_prefix.value

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
        if self.ui.material.value != "":
            well_name = WellNameTxt(buff=self.ui.material.value)

        try:
            mic = Microscope(folder=folder)
        except MicroscopeException as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f'Error occurred while initializing microscope : "{e}" (at {ex_file}:{ex_line})')
            return
        except TypeError as e:
            ex_file, ex_line = get_exception_location()
            logger.error(f'Type error occurred while initializing microscope: "{e}" (at {ex_file}:{ex_line})')
            return

        self.start_run()
        run_thread = threading.Thread(
            target=mic.move,
            kwargs={
                "dest": dest,
                "prefix": name,
                "create_dubdir": self.ui.create_subdir_value.get(),
                "pos_names": well_name,
                "file_prefix": file_prefix,
            },
        )
        run_thread.daemon = True
        run_thread.start()

        self.monitor(run_thread=run_thread)

    def start_run(self):
        """
        Show the progress bar and disable the run button.
        """
        self.ui.progressbar.grid(row=self.ui.row_count)
        self.ui.progressbar.start(20)
        self.ui.btn_run.config(state=DISABLED)

    def stop_run(self):
        """
        Stop the progress bar, re-enable the run button, and show a completion message.
        """
        self.ui.progressbar.stop()
        self.ui.progressbar.grid_forget()
        self.ui.btn_run.config(state=NORMAL)
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
        if self._cfg is None:
            return

        if "Settings" not in self._cfg:
            self._cfg["Settings"] = {}
        self._cfg["Settings"]["src_folder"] = self.ui.src_folder.folder_path
        self._cfg["Settings"]["dest_folder"] = self.ui.dest_folder.folder_path
        self._cfg["Settings"]["file_prefix"] = self.ui.file_prefix.value
        self._cfg["Settings"]["name"] = self.ui.name.value
        self._cfg["Settings"]["create_subdir"] = str(self.ui.create_subdir_value.get())  # Boolean value
        self._cfg["Settings"]["well_name"] = self.ui.material.value  # Multitext value

        _save_cfg(DEFAULT_CONFIG_FILE, self._cfg)

    def on_closing(self):
        """
        Handle the application closing event by saving configuration.
        """
        logger.info("Closing application")
        self._save_configuration()
        self.destroy()


def _create_and_read_cfg(path: str) -> configparser.ConfigParser:
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
        logger.warning(f"Configuration file {path} not found. Creating default configuration.")
    return config


def _save_cfg(path: str, config: configparser.ConfigParser) -> None:
    """
    Save the configuration to a file.

    Includes an update timestamp in the 'Meta' section.

    Args:
        path: The path to the configuration file.
        config: The configuration object to save.
    """
    config["Meta"] = {"Update time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        with open(path, "w", encoding="utf-8") as cfgfile:
            config.write(cfgfile)
            logger.debug(f"Configuration saved to '{path}', contents:\n{config}")
    except (IOError, OSError) as e:
        ex_file, ex_line = get_exception_location()
        logger.error(f"Error occurred while saving configuration to '{path}': {e} (at {ex_file}:{ex_line})")


def main() -> int:
    """
    Main entry point for the SplitToWells GUI application.

    Configures logging, loads settings, initializes the application window,
    and starts the main GUI loop.

    Returns:
        0.
    """
    formatter_stdout = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    formatter_file = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)-7s [%(funcName)-20s] [%(filename)25s:%(lineno)-4d] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter_stdout)

    log_file_path = "SplitToWells.log"
    file_handler = FileHandler(log_file_path, encoding="utf-8", mode="w")
    file_handler.setFormatter(formatter_file)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    config = _create_and_read_cfg(DEFAULT_CONFIG_FILE)

    window = App(cfg=config)
    window.title("Split To Wells")
    # window.iconbitmap("microscope.ico")

    logger.info("Starting SplitToWells")
    window.mainloop()
    return 0


if __name__ == "__main__":
    EXIT_CODE = main()
    sys.exit(EXIT_CODE)
