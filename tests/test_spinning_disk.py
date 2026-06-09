from unittest.mock import MagicMock, patch

import pytest

from photo.microscopebase import MicroscopeException
from photo.spinning_disk import SpinningDisk


def test_spinning_disk_init_no_nd(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    with pytest.raises(MicroscopeException, match="There is no nd file"):
        SpinningDisk(folder)


def test_spinning_disk_init_with_nd(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    nd_file = folder / "test.nd"
    nd_file.write_text("data")

    sd = SpinningDisk(folder)
    assert sd._nd_files == [nd_file]
    assert nd_file not in sd._files_list


def test_spinning_disk_parse_line():
    # Valid: Stage1, row:A, column:1, site:1
    line = "Stage1, row:A, column:1, site:1"
    success, stage, pos = SpinningDisk._parse_line(line)
    assert success is True
    assert stage == 1
    assert pos.row == "A"
    assert pos.col == 1
    assert pos.site == 1

    # With pos_names
    pos_names = {"A1": "SampleA"}
    success, stage, pos = SpinningDisk._parse_line(line, pos_names=pos_names)
    assert pos.name == "SampleA"

    # Invalid
    success, stage, pos = SpinningDisk._parse_line("invalid")
    assert success is False


def test_spinning_disk_parse_file_name():
    # Valid: batch_whatever_s1.tif
    name = "BatchA_experiment_s1.tif"
    success, stage, batch = SpinningDisk._parse_file_name(name)
    assert success is True
    assert stage == 1
    assert batch == "BatchA"

    # Invalid stage (not digit) - but regex \d+ ensures it is digit if matched.
    # What if batch is empty? Regex r"^(?P<batch>[\w\s\-\_]*)_.*_s(?P<stage>\d+).*\.(tif|stk)$"
    # If name is "_test_s1.tif", batch is "".
    success, stage, batch = SpinningDisk._parse_file_name("_test_s1.tif")
    assert success is False

    # Invalid name
    success, stage, batch = SpinningDisk._parse_file_name("invalid.txt")
    assert success is False


def test_spinning_disk_match(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    nd_file = folder / "BatchA.nd"
    nd_file.write_text("Stage1, row:A, column:1, site:1\nStage2, row:B, column:2, site:1")

    f1 = folder / "BatchA_exp_s1.tif"
    f1.write_text("img1")
    f2 = folder / "BatchA_exp_s2.tif"
    f2.write_text("img2")
    f3 = folder / "BatchB_exp_s1.tif"  # Missing batch
    f3.write_text("img3")
    f4 = folder / "BatchA_exp_s3.tif"  # Missing stage
    f4.write_text("img4")
    f5 = folder / "invalid_name.tif"
    f5.write_text("img5")
    (folder / "subdir").mkdir()

    sd = SpinningDisk(folder)
    skipped = sd._match()

    assert len(skipped) == 3  # f3, f4, f5. (subdir is skipped in loop because not file)
    skipped_names = [f.name for f in skipped]
    assert "BatchB_exp_s1.tif" in skipped_names
    assert "BatchA_exp_s3.tif" in skipped_names
    assert "invalid_name.tif" in skipped_names


def test_spinning_disk_parse_file_name_redundant_check():
    # To cover line 85 (unreachable via regex), we mock the regex match result
    mock_match = MagicMock()
    mock_match.groupdict.return_value = {"batch": "B", "stage": "not_a_digit"}
    with patch("re.match", return_value=mock_match):
        # The code will set parsed_successfully = False but then crash on int(di["stage"])
        with pytest.raises(ValueError):
            SpinningDisk._parse_file_name("any.tif")


def test_spinning_disk_match_no_skipped(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    nd_file = folder / "BatchA.nd"
    nd_file.write_text("Stage1, row:A, column:1, site:1\nInvalid line")

    f1 = folder / "BatchA_exp_s1.tif"
    f1.write_text("img1")

    sd = SpinningDisk(folder)
    skipped = sd._match()
    assert len(skipped) == 0
