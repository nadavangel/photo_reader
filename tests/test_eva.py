import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from photo.eva import Eva
from photo.wells import WellPos, WellName

def test_eva_init(tmp_path):
    folder = tmp_path / "root"
    folder.mkdir()
    data_dir = folder / "data"
    data_dir.mkdir()
    
    eva = Eva(folder)
    assert eva.path == data_dir

def test_eva_parse_file_name():
    # Valid name: r"(?P<row>[A-Za-z]+)(?P<col>\d+)[-]*W(?P<well>\d+)[-]*P(?P<pos>\d+)[-]*Z(?P<z>\d+)[-]*T(?P<time>\d+)[-]*(?P<channel>\w+).tif"
    name = "A1-W1-P2-Z3-T4-FITC.tif"
    success, pos = Eva._parse_file_name(name)
    assert success is True
    assert pos.row == "A"
    assert pos.col == 1
    assert pos.site == 2
    
    # Invalid name
    success, pos = Eva._parse_file_name("invalid.txt")
    assert success is False
    assert pos is None

def test_eva_parse_file_name_with_pos_names():
    name = "B2-W1-P1-Z1-T1-DAPI.tif"
    pos_names = {"B2": "SampleB"}
    success, pos = Eva._parse_file_name(name, pos_names=pos_names)
    assert success is True
    assert pos.name == "SampleB"

def test_eva_match(tmp_path):
    folder = tmp_path / "root"
    folder.mkdir()
    data_dir = folder / "data"
    data_dir.mkdir()
    
    f1 = data_dir / "A1-W1-P1-Z1-T1-DAPI.tif"
    f1.write_text("data")
    f2 = data_dir / "invalid.tif"
    f2.write_text("data")
    (data_dir / "subdir").mkdir()
    
    eva = Eva(folder)
    skipped = eva._match()
    
    assert len(skipped) == 1  # The subdir
    assert skipped[0].name == "subdir"
    assert len(eva._pos_photo) == 1
    pos = list(eva._pos_photo.keys())[0]
    assert pos.row == "A"
    assert pos.col == 1
    
def test_eva_match_no_skipped(tmp_path):
    folder = tmp_path / "root"
    folder.mkdir()
    data_dir = folder / "data"
    data_dir.mkdir()
    
    f1 = data_dir / "A1-W1-P1-Z1-T1-DAPI.tif"
    f1.write_text("data")
    
    eva = Eva(folder)
    skipped = eva._match()
    assert len(skipped) == 0
