"""
This module contains the modern GUI application for splitting photos into wells using CustomTkinter.
"""

from __future__ import annotations

import configparser
import logging
import sys
import threading
import tkinter as tk
import webbrowser
from logging import FileHandler, Handler
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk  # type: ignore
from PIL import Image

from photo.utils import Microscope
from photo.wells import WellNameTxt

DEFAULT_CONFIG_FILE = ".config.ini"
APP_NAME = "Split To Wells"
APP_VERSION = "2.0.0"
AUTHOR_NAME = "Nadav Angel"
GITHUB_URL = "https://github.com/nadavangel/photo_reader"

# Configure customtkinter
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

logger = logging.getLogger("mylSplitToWells")


class TextHandler(Handler):
    """
    Custom logging handler to post logs to a CustomTkinter Textbox.
    """

    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.textbox.configure(state="normal")
            self.textbox.insert("end", msg + "\n")
            self.textbox.configure(state="disabled")
            self.textbox.see("end")

        self.textbox.after(0, append)


class FolderSelect(ctk.CTkFrame):
    """
    A CustomTkinter Frame for selecting and displaying a folder path.
    """

    def __init__(self, parent, label_text, path="", **kwargs):
        super().__init__(master=parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=label_text, width=140, anchor="w")
        self.label.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.entry = ctk.CTkEntry(self, placeholder_text="Select a folder...")
        self.entry.insert(0, path)
        self.entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        self.button = ctk.CTkButton(self, text="Browse", width=80, command=self.browse)
        self.button.grid(row=0, column=2, pady=5)

    def browse(self):
        folder = filedialog.askdirectory(initialdir=self.entry.get())
        if folder:
            self.entry.delete(0, "end")
            self.entry.insert(0, folder)

    @property
    def folder_path(self):
        return self.entry.get()


class App(ctk.CTk):
    """
    Modernized main application window using CustomTkinter.
    """

    def __init__(self, cfg: configparser.ConfigParser):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("800x880")
        self.minsize(700, 850)

        # Set icon if it exists
        icon_path = Path("icons/microscope.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception as e:
                print(f"Could not load icon: {e}")

        self._cfg = cfg
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Console row

        # 1. Path Configuration Frame
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.path_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.path_frame, text="Path Configuration", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.src_folder = FolderSelect(
            self.path_frame,
            "Source Folder",
            path=cfg.get("Settings", "src_folder", fallback=""),
        )
        self.src_folder.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.dest_folder = FolderSelect(
            self.path_frame,
            "Destination Folder",
            path=cfg.get("Settings", "dest_folder", fallback=""),
        )
        self.dest_folder.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # 2. Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(self.settings_frame, text="Execution Settings", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        # Row 1
        ctk.CTkLabel(self.settings_frame, text="Output Name").grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        self.ent_name = ctk.CTkEntry(self.settings_frame, placeholder_text="e.g. Experiment_01")
        self.ent_name.insert(0, cfg.get("Settings", "name", fallback=""))
        self.ent_name.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="ew")

        ctk.CTkLabel(self.settings_frame, text="File Prefix").grid(row=1, column=2, padx=(10, 5), pady=5, sticky="w")
        self.ent_file_prefix = ctk.CTkEntry(self.settings_frame, placeholder_text="e.g. img_")
        self.ent_file_prefix.insert(0, cfg.get("Settings", "file_prefix", fallback=""))
        self.ent_file_prefix.grid(row=1, column=3, padx=(0, 10), pady=5, sticky="ew")

        # Row 2
        ctk.CTkLabel(self.settings_frame, text="Threads").grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        self.ent_threads = ctk.CTkEntry(self.settings_frame, width=80)
        self.ent_threads.insert(0, cfg.get("Settings", "threads", fallback="4"))
        self.ent_threads.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="w")

        self.create_subdir_var = tk.BooleanVar(value=cfg.getboolean("Settings", "create_subdir", fallback=True))
        self.check_subdir = ctk.CTkCheckBox(self.settings_frame, text="Create Well Subdirectories", variable=self.create_subdir_var)
        self.check_subdir.grid(row=2, column=2, columnspan=2, padx=10, pady=5, sticky="w")

        # 3. Material Info Frame
        self.material_frame = ctk.CTkFrame(self)
        self.material_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.material_frame.grid_columnconfigure(1, weight=1)
        self.material_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.material_frame, text="Material Mapping (Optional)", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        ctk.CTkLabel(self.material_frame, text="Format: Position [TAB] Name", font=ctk.CTkFont(size=11, slant="italic")).grid(
            row=0, column=1, padx=10, pady=10, sticky="e"
        )

        self.txt_material = ctk.CTkTextbox(self.material_frame, height=120)
        self.txt_material.insert("1.0", cfg.get("Settings", "well_name", fallback=""))
        self.txt_material.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        # 4. Console Frame
        self.console_frame = ctk.CTkFrame(self)
        self.console_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.console_frame, text="Status Console", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.console = ctk.CTkTextbox(self.console_frame, state="disabled", fg_color="#1a1a1a", text_color="#2ecc71", font=("Consolas", 12))
        self.console.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # 5. Control Frame
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.control_frame.grid_columnconfigure(0, weight=1)

        self.progressbar = ctk.CTkProgressBar(self.control_frame, mode="indeterminate", height=15)
        self.progressbar.grid(row=0, column=0, padx=(0, 20), sticky="ew")
        self.progressbar.set(0)

        self.btn_run = ctk.CTkButton(
            self.control_frame,
            text="START PROCESSING",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run,
        )
        self.btn_run.grid(row=0, column=1)

        # 6. Footer Frame
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self.footer_frame.grid_columnconfigure(1, weight=0)

        footer_text = f"Version {APP_VERSION} | Developed by {AUTHOR_NAME} "
        self.lbl_footer = ctk.CTkLabel(
            self.footer_frame,
            text=footer_text,
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color="gray",
            anchor="w",
        )
        self.lbl_footer.grid(row=0, column=0, sticky="ew", padx=(0, 20))

        # GitHub Icon Link
        github_dark = Path("icons/github-mark-dark.png")
        github_light = Path("icons/github-mark-light.png")

        if github_dark.exists() and github_light.exists():
            github_image = ctk.CTkImage(light_image=Image.open(github_dark), dark_image=Image.open(github_light), size=(20, 20))
            self.lbl_github = ctk.CTkLabel(self.footer_frame, image=github_image, text="", cursor="hand2")
        else:
            # Fallback to text if icons are missing
            self.lbl_github = ctk.CTkLabel(
                self.footer_frame,
                text="GitHub",
                font=ctk.CTkFont(size=10, underline=True),
                text_color="#3498db",
                cursor="hand2",
            )

        self.lbl_github.grid(row=0, column=1, sticky="e")
        self.lbl_github.bind("<Button-1>", lambda e: webbrowser.open_new_tab(GITHUB_URL))

        # Setup Logging to Console
        self.text_handler = TextHandler(self.console)
        self.text_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
        logger.addHandler(self.text_handler)

    def run(self):
        src = self.src_folder.folder_path
        dst = self.dest_folder.folder_path
        name = self.ent_name.get()
        file_prefix = self.ent_file_prefix.get()

        if not src:
            messagebox.showerror("Error", "Please select a source folder.")
            return
        if not dst:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        well_name_txt = self.txt_material.get("1.0", "end-1c").strip()
        well_name = WellNameTxt(buff=well_name_txt) if well_name_txt else None

        try:
            mic = Microscope(folder=src)
        except Exception as e:
            logger.error(f"Failed to initialize microscope: {e}")
            messagebox.showerror("Error", f"Failed to initialize: {e}")
            return

        try:
            threads = int(self.ent_threads.get())
        except ValueError:
            threads = 1
            logger.warning("Invalid thread count, defaulting to 1")

        self.start_ui_run()

        run_thread = threading.Thread(
            target=mic.move,
            kwargs={
                "dest": dst,
                "prefix": name,
                "create_dubdir": self.create_subdir_var.get(),
                "pos_names": well_name,
                "file_prefix": file_prefix,
                "threads": threads,
            },
            daemon=True,
        )
        run_thread.start()
        self.monitor(run_thread)

    def start_ui_run(self):
        self.btn_run.configure(state="disabled", text="PROCESSING...")
        self.progressbar.start()
        logger.info("Starting file processing operation...")

    def stop_ui_run(self):
        self.progressbar.stop()
        self.progressbar.set(1.0)
        self.btn_run.configure(state="normal", text="START PROCESSING")
        logger.info("Operation completed.")
        messagebox.showinfo("Success", "Files have been successfully split into wells!")

    def monitor(self, run_thread):
        if run_thread.is_alive():
            self.after(100, lambda: self.monitor(run_thread))
        else:
            self.stop_ui_run()

    def on_closing(self):
        self._save_configuration()
        self.destroy()

    def _save_configuration(self):
        if "Settings" not in self._cfg:
            self._cfg["Settings"] = {}

        self._cfg["Settings"]["src_folder"] = self.src_folder.folder_path
        self._cfg["Settings"]["dest_folder"] = self.dest_folder.folder_path
        self._cfg["Settings"]["name"] = self.ent_name.get()
        self._cfg["Settings"]["file_prefix"] = self.ent_file_prefix.get()
        self._cfg["Settings"]["threads"] = self.ent_threads.get()
        self._cfg["Settings"]["create_subdir"] = str(self.create_subdir_var.get())
        self._cfg["Settings"]["well_name"] = self.txt_material.get("1.0", "end-1c")

        try:
            with open(DEFAULT_CONFIG_FILE, "w", encoding="utf-8") as f:
                self._cfg.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")


def main():
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Configure file logging
    file_handler = FileHandler("SplitToWells.log", encoding="utf-8", mode="w")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root_logger.addHandler(file_handler)

    # Standard out logging
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    stdout_handler.setLevel(logging.INFO)
    root_logger.addHandler(stdout_handler)

    # Load Config
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_FILE)

    app = App(config)
    app.mainloop()


if __name__ == "__main__":
    main()
