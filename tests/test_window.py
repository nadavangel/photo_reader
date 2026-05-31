import tkinter as tk
from unittest.mock import MagicMock, patch, PropertyMock
import configparser
from window import FolderSelect, Multitext, Input, AppUI, App, _create_and_read_cfg, _save_cfg, main
from photo.microscopebase import MicroscopeException


def test_folder_select():
    root = tk.Tk()
    fs = FolderSelect(root, "desc", "initial_path")
    assert fs.folder_path == "initial_path"

    with patch("window.filedialog.askdirectory", return_value="new_path"):
        fs.set_folder_path()
        assert fs.folder_path == "new_path"

    with patch("window.filedialog.askdirectory", return_value=""):
        fs.set_folder_path()
        assert fs.folder_path == "new_path"
    root.destroy()


def test_multitext():
    root = tk.Tk()
    mt = Multitext(root, "title")
    mt.text.insert("1.0", "hello")
    assert mt.value == "hello\n"

    # Test select_all_operation
    event = MagicMock()
    # ScrolledText case
    Multitext.select_all_operation(event, mt.text)

    # Non-ScrolledText case
    event.widget = MagicMock()
    Multitext.select_all_operation(event, MagicMock())
    event.widget.event_generate.assert_called_with("<<SelectAll>>")

    root.destroy()


def test_input():
    root = tk.Tk()
    inp = Input(root, "desc")
    inp.ent_path.insert(0, "val")
    assert inp.value == "val"
    root.destroy()


def test_create_and_read_cfg(tmp_path):
    cfg_file = tmp_path / "test.ini"
    cfg = _create_and_read_cfg(str(cfg_file))
    assert isinstance(cfg, configparser.ConfigParser)

    cfg_file.write_text("[Settings]\nkey=val")
    cfg = _create_and_read_cfg(str(cfg_file))
    assert cfg.get("Settings", "key") == "val"


def test_save_cfg(tmp_path):
    cfg = configparser.ConfigParser()
    path = tmp_path / "save.ini"
    _save_cfg(str(path), cfg)
    assert path.exists()

    with patch("builtins.open", side_effect=IOError("perm error")):
        _save_cfg(str(path), cfg)


def test_app_ui():
    root = tk.Tk()
    cfg = configparser.ConfigParser()
    cfg.add_section("Settings")
    cfg.set("Settings", "src_folder", "src")
    cfg.set("Settings", "create_subdir", "False")

    ui = AppUI(root, cfg)
    assert ui.src_folder.folder_path == "src"

    # Case create_subdir True
    cfg.set("Settings", "create_subdir", "True")
    ui2 = AppUI(root, cfg)
    assert ui2.create_subdir_value.get() is True

    root.destroy()


@patch("window.messagebox.showinfo")
def test_app_methods(mock_info):
    tk.Tk()
    cfg = configparser.ConfigParser()
    cfg.add_section("Settings")  # Ensure Settings exists for branch coverage
    app = App(cfg)

    event = MagicMock()
    event.state = 0x4  # Ctrl

    # Ctrl+X
    event.keycode = 88
    event.keysym = "a"
    assert app._on_key_release(event) == "break"

    # Ctrl+V
    event.keycode = 86
    event.keysym = "a"
    assert app._on_key_release(event) == "break"

    # Ctrl+C
    event.keycode = 67
    event.keysym = "a"
    assert app._on_key_release(event) == "break"

    # Ctrl+A
    event.keycode = 65
    with patch("window.Multitext.select_all_operation") as mock_sa:
        assert app._on_key_release(event) == "break"
        mock_sa.assert_called()

    # Other key
    event.keycode = 99
    assert app._on_key_release(event) is None

    app.start_run()
    app.stop_run()

    mock_thread = MagicMock()
    mock_thread.is_alive.side_effect = [True, False]
    with patch.object(app, "after") as mock_after:
        app.monitor(mock_thread)
        mock_after.assert_called()
        mock_after.call_args[0][1]()

    # Test _save_configuration and on_closing
    with patch("window._save_cfg") as mock_save:
        # Case 0: cfg is None
        app._cfg = None
        app._save_configuration()
        mock_save.assert_not_called()

        # Case 1: Settings already exists (covered by initial cfg)
        app._cfg = cfg
        app._save_configuration()

        # Case 2: Settings missing
        del app._cfg["Settings"]
        app.on_closing()  # This calls _save_configuration and then destroy()
        mock_save.assert_called()


@patch("window.messagebox.showinfo")
def test_app_run(mock_info, tmp_path):
    tk.Tk()
    cfg = configparser.ConfigParser()
    app = App(cfg)

    src = tmp_path / "src"
    src.mkdir()
    dest = tmp_path / "dest"
    dest.mkdir()

    # Branch: material value empty
    with patch.object(Multitext, "value", new_callable=PropertyMock) as mock_val:
        mock_val.return_value = ""
        with patch("window.Microscope"):
            with patch("threading.Thread") as mock_thread:
                app.ui.src_folder.folder_path_var.set(str(src))
                app.ui.dest_folder.folder_path_var.set(str(dest))
                app.run()
                mock_thread.assert_called()

    # Branch: src/dst is None
    with patch.object(FolderSelect, "folder_path", new_callable=PropertyMock) as mock_fs_path:
        mock_fs_path.side_effect = [None, str(dest), str(src), None]
        with patch("window.filedialog.askdirectory", side_effect=[str(src), str(dest)]) as mock_ask:
            app.run()  # src is None
            app.run()  # dst is None
            assert mock_ask.call_count == 2

    # Case no folder selected
    app.ui.src_folder.folder_path_var.set("")
    with patch("window.filedialog.askdirectory", return_value=""):
        app.run()

    app.ui.src_folder.folder_path_var.set(str(src))
    app.ui.dest_folder.folder_path_var.set("")
    with patch("window.filedialog.askdirectory", return_value=""):
        app.run()

    # Microscope error
    app.ui.dest_folder.folder_path_var.set(str(dest))
    with patch("window.Microscope", side_effect=MicroscopeException("error")):
        app.run()

    with patch("window.Microscope", side_effect=TypeError("error")):
        app.run()

    app.destroy()


def test_main():
    with patch("window.App") as mock_app:
        with patch("window._create_and_read_cfg"):
            mock_app_instance = mock_app.return_value
            assert main() == 0
            mock_app_instance.mainloop.assert_called()
