import configparser
from unittest.mock import MagicMock, patch

import customtkinter as ctk  # type: ignore

from window import App, FolderSelect, main

# Set to Light mode for tests to avoid issues with some environments
ctk.set_appearance_mode("Light")


def test_folder_select():
    root = ctk.CTk()
    fs = FolderSelect(root, "desc", "initial_path")
    assert fs.folder_path == "initial_path"

    with patch("window.filedialog.askdirectory", return_value="new_path"):
        fs.browse()
        assert fs.folder_path == "new_path"

    with patch("window.filedialog.askdirectory", return_value=""):
        fs.browse()
        assert fs.folder_path == "new_path"
    root.destroy()


@patch("window.messagebox.showinfo")
def test_app_methods(mock_info):
    cfg = configparser.ConfigParser()
    cfg.add_section("Settings")

    app = App(cfg)

    app.start_ui_run()
    app.stop_ui_run()

    mock_thread = MagicMock()
    mock_thread.is_alive.side_effect = [True, False]
    with patch.object(app, "after") as mock_after:
        app.monitor(mock_thread)
        mock_after.assert_called()
        # Simulate the 'after' callback
        mock_after.call_args[0][1]()

    # Test _save_configuration
    with patch("builtins.open", MagicMock()):
        app._save_configuration()
        assert "Settings" in app._cfg

    app.destroy()


@patch("window.messagebox.showinfo")
@patch("window.messagebox.showerror")
def test_app_run(mock_error, mock_info, tmp_path):
    cfg = configparser.ConfigParser()
    app = App(cfg)

    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    # Case: Missing source/dest
    app.src_folder.entry.delete(0, "end")
    app.run()
    mock_error.assert_called_with("Error", "Please select a source folder.")

    app.src_folder.entry.insert(0, str(src))
    app.dest_folder.entry.delete(0, "end")
    app.run()
    mock_error.assert_called_with("Error", "Please select a destination folder.")

    # Successful run start
    app.dest_folder.entry.insert(0, str(dest))
    with patch("window.Microscope"):
        with patch("threading.Thread") as mock_thread:
            app.run()
            mock_thread.assert_called()

    # Microscope error
    with patch("window.Microscope", side_effect=Exception("error")):
        app.run()
        mock_error.assert_called()

    # Test invalid thread count
    app.ent_threads.delete(0, "end")
    app.ent_threads.insert(0, "invalid")
    with patch("window.Microscope"):
        with patch("window.logger") as mock_log:
            app.run()
            mock_log.warning.assert_called_with("Invalid thread count, defaulting to 1")

    app.destroy()


def test_main():
    with patch("window.App") as mock_app:
        with patch("configparser.ConfigParser.read"):
            mock_app_instance = mock_app.return_value
            assert main() is None or main() == 0
            mock_app_instance.mainloop.assert_called()
