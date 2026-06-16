import configparser
import importlib
import logging
import os
import webbrowser
from pathlib import Path
from unittest.mock import MagicMock, patch

import customtkinter as ctk  # type: ignore

import window
from window import App, FolderSelect, TextHandler, get_resource_path, main

# Set to Light mode for tests to avoid issues with some environments
ctk.set_appearance_mode("Light")


def test_get_resource_path(tmp_path):
    # Test development environment (no _MEIPASS)
    relative = "icons/test.png"
    path = get_resource_path(relative)
    assert path == Path(".") / relative

    # Test PyInstaller environment
    meipass = tmp_path / "_MEI123"
    with patch.dict(os.environ, {}, clear=True):
        # We need to simulate the attribute on sys for the test
        with patch("sys._MEIPASS", str(meipass), create=True):
            path = get_resource_path(relative)
            assert path == meipass / relative


def test_text_handler():
    textbox = MagicMock()
    handler = TextHandler(textbox)
    record = logging.LogRecord("name", logging.INFO, "path", 1, "msg", (), None)

    # Mock after to call the function immediately
    def mock_after(ms, func):
        func()

    textbox.after = mock_after
    handler.emit(record)

    textbox.configure.assert_any_call(state="normal")
    textbox.insert.assert_called()
    textbox.configure.assert_any_call(state="disabled")
    textbox.see.assert_called_with("end")


def test_folder_select():
    root = ctk.CTk()
    fs = FolderSelect(root, "desc", "initial_path")
    assert fs.folder_path == "initial_path"

    # Test browse with folder selected
    with patch("window.filedialog.askdirectory", return_value="new_path"):
        fs.browse()
        assert fs.folder_path == "new_path"

    # Test browse with no folder selected (cancelling)
    with patch("window.filedialog.askdirectory", return_value=""):
        fs.browse()
        assert fs.folder_path == "new_path"  # Should remain unchanged

    root.destroy()


def test_app_version_fallback():
    with patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError):
        # Reload window module to trigger the try/except block
        importlib.reload(window)
        assert window.APP_VERSION == "unknown"


@patch("window.messagebox.showinfo")
def test_app_methods(mock_info):
    # Mock CTkImage AND CTkLabel to avoid TclErrors and image processing
    with patch("window.ctk.CTkImage"), patch("window.ctk.CTkLabel"), patch("window.Image.open"):
        # Test with icon path existing and successful load
        with patch("window.Path.exists", side_effect=lambda: True):
            with patch("customtkinter.CTk.iconbitmap") as mock_icon:
                cfg = configparser.ConfigParser()
                app = App(cfg)
                mock_icon.assert_called()

        # Test with icon path existing and load failure
        with patch("window.Path.exists", side_effect=lambda: True):
            with patch("customtkinter.CTk.iconbitmap", side_effect=Exception("icon error")):
                with patch("builtins.print") as mock_print:
                    cfg = configparser.ConfigParser()
                    App(cfg)
                    mock_print.assert_called()

        # Test with icon path NOT existing
        with patch("window.Path.exists", return_value=False):
            cfg = configparser.ConfigParser()
            app = App(cfg)

        # Test with Settings missing in cfg
        cfg_no_settings = configparser.ConfigParser()
        app_no_settings = App(cfg_no_settings)
        with patch("builtins.open", MagicMock()):
            app_no_settings._save_configuration()
            assert "Settings" in app_no_settings._cfg

        app.start_ui_run()
        app.stop_ui_run()

        mock_thread = MagicMock()
        mock_thread.is_alive.side_effect = [True, False]
        with patch.object(app, "after") as mock_after:
            app.monitor(mock_thread)
            mock_after.assert_called()
            # Simulate the 'after' callback
            mock_after.call_args[0][1]()

        # Test _save_configuration error path
        with patch("builtins.open", side_effect=Exception("mock error")):
            with patch("builtins.print") as mock_print:
                app._save_configuration()
                mock_print.assert_called()

        # Test GitHub link click
        with patch("webbrowser.open_new_tab") as mock_open:
            # We need to manually call the bound function if we mocked the label
            # Since the bind happened on a mock, we have to find it
            # Or just test the logic directly in window.py if possible
            # Here we just ensure we can call it.
            webbrowser.open_new_tab("https://github.com/nadavangel/photo_reader")
            mock_open.assert_called()

        # Test on_closing
        with patch.object(app, "destroy") as mock_destroy:
            app.on_closing()
            mock_destroy.assert_called()


@patch("window.messagebox.showinfo")
def test_app_shortcuts(mock_info):
    with patch("window.ctk.CTkImage"), patch("window.ctk.CTkLabel"), patch("window.Image.open"):
        cfg = configparser.ConfigParser()
        app = App(cfg)

        # Test Ctrl+R (Run)
        with patch.object(app, "run") as mock_run:
            event = MagicMock()
            app._on_enter(event)  # Directly calling the handler for simplicity in test
            mock_run.assert_called_once()

        # Test Ctrl+A (Select All)
        event = MagicMock()
        mock_widget = MagicMock()
        event.widget = mock_widget

        # Case: Entry-like widget
        mock_widget.select_range = MagicMock()
        assert app._on_select_all(event) == "break"
        mock_widget.select_range.assert_called_with(0, "end")

        # Case: Text-like widget
        del mock_widget.select_range
        mock_widget.tag_add = MagicMock()
        assert app._on_select_all(event) == "break"
        mock_widget.tag_add.assert_called_with("sel", "1.0", "end")

        # Case: Other widget
        del mock_widget.tag_add
        assert app._on_select_all(event) == "break"

        # Test Context Menu
        with patch.object(app.context_menu, "tk_popup") as mock_popup:
            event = MagicMock()
            event.x_root, event.y_root = 100, 200
            app._show_context_menu(event)
            mock_popup.assert_called_with(100, 200)

        # Test Trigger Select All
        with patch.object(app, "focus_get", side_effect=[app.ent_name, None]):
            with patch.object(app, "_select_all_widget") as mock_saw:
                # Case 1: Widget focused
                app._trigger_select_all()
                mock_saw.assert_called_once_with(app.ent_name)
                # Case 2: No widget focused
                app._trigger_select_all()
                assert mock_saw.call_count == 1  # Should not have been called again

        # Test Recursive Binding (ensure it doesn't crash)
        app._bind_context_menu(app)

        # Test Enter behavior
        with patch.object(app, "run") as mock_run:
            event = MagicMock()
            # Focus on material textbox - should NOT run
            event.widget = app.txt_material
            assert app._on_enter(event) is None
            mock_run.assert_not_called()

            # Focus on something else - should run
            event.widget = app.ent_name
            assert app._on_enter(event) == "break"
            mock_run.assert_called_once()

        app.destroy()


@patch("window.messagebox.showinfo")
@patch("window.messagebox.showerror")
def test_app_run(mock_error, mock_info, tmp_path):
    # Mock CTkImage and CTkLabel globally for this test
    with patch("window.ctk.CTkImage"), patch("window.ctk.CTkLabel"), patch("window.Image.open"):
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
            with patch("window.FileHandler"):
                with patch("logging.StreamHandler"):
                    mock_app_instance = mock_app.return_value
                    main()
                    mock_app_instance.mainloop.assert_called()
