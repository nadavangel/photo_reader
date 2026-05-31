import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from photo.photo import Photo, sanitize_path
from photo.wells import WellPos

def test_photo_init(tmp_path):
    f = tmp_path / "test.tif"
    f.write_text("data")
    p = Photo(f)
    assert p.path == f
    
    pos = WellPos(row="A", col=1, site=1)
    p2 = Photo(f, pos=pos)
    assert p2.pos == pos

def test_photo_pos_setter():
    p = Photo(Path("test.tif"))
    pos = WellPos(row="A", col=1, site=1)
    p.pos = pos
    assert p.pos == pos
    
    p.pos = ("B", 2, 3)
    assert p.pos.row == "B"
    assert p.pos.col == 2
    assert p.pos.site == 3
    
    with pytest.raises(TypeError, match="pos is not a WellPos or tuple"):
        p.pos = "invalid"

def test_photo_set_well():
    p = Photo(Path("test.tif"))
    p.set_well("C", 3, 4)
    assert p.pos.row == "C"
    assert p.pos.col == 3
    assert p.pos.site == 4

def test_photo_name_setter():
    p = Photo(Path("test.tif"))
    p.name = "new_name"
    assert p.name == "new_name"

def test_photo_path_setter(tmp_path):
    f1 = tmp_path / "f1.tif"
    f1.write_text("1")
    f2 = tmp_path / "f2.tif"
    f2.write_text("2")
    p = Photo(f1)
    p.path = f2
    assert p.path == f2
    p.path = str(f1)
    assert p.path == f1

def test_photo_copy(tmp_path):
    src = tmp_path / "src.tif"
    src.write_text("data")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    
    p = Photo(src)
    p.copy(dest_dir)
    assert (dest_dir / "src.tif").exists()
    
    p.copy(dest_dir, new_name="new")
    assert (dest_dir / "new.tif").exists()
    
    p.copy(dest_dir, prefix="pre")
    assert (dest_dir / "pre_src.tif").exists()

def test_sanitize_path():
    assert sanitize_path("normal.tif") == "normal.tif"
    assert sanitize_path("invalid<>.tif") == "invalid__.tif"
    assert sanitize_path("trailing . ") == "trailing_"
    assert sanitize_path("CON") == "CON_"
    assert sanitize_path("aux") == "aux_"
    assert sanitize_path("COM1") == "COM1_"
    assert sanitize_path("LPT9") == "LPT9_"
    # No changes path
    assert sanitize_path("valid_path.tif") == "valid_path.tif"
