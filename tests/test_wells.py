import pytest
from photo.wells import WellPos, WellName, WellNameTxt

def test_wellpos_init():
    wp = WellPos(row="A", col=1, site=2, name="test")
    assert wp.row == "A"
    assert wp.col == 1
    assert wp.site == 2
    assert wp.name == "test"

def test_wellpos_create_tuple_2():
    wp = WellPos.create(("B", 2))
    assert wp.row == "B"
    assert wp.col == 2
    assert wp.site == 1

def test_wellpos_create_tuple_3():
    wp = WellPos.create(("C", 3, 4))
    assert wp.row == "C"
    assert wp.col == 3
    assert wp.site == 4

def test_wellpos_create_not_tuple():
    with pytest.raises(TypeError, match="Pos is not tuple"):
        WellPos.create("not a tuple")

def test_wellpos_same_pos():
    wp1 = WellPos(row="A", col=1, site=1)
    wp2 = WellPos(row="A", col=1, site=2)
    wp3 = WellPos(row="B", col=1, site=1)
    assert wp1.same_pos(wp2) is True
    assert wp1.same_pos(wp3) is False

def test_wellpos_hash():
    wp1 = WellPos(row="A", col=1, site=1, name="n1")
    wp2 = WellPos(row="A", col=1, site=1, name="n1")
    assert hash(wp1) == hash(wp2)

def test_wellpos_str():
    wp1 = WellPos(row="A", col=1, site=1)
    assert str(wp1) == "A01"
    wp2 = WellPos(row="B", col=12, site=1, name="sample")
    assert str(wp2) == "B12_sample"

class ConcreteWellName(WellName):
    def _fill(self):
        self["A01"] = "Sample1"

def test_wellname_base():
    wn = ConcreteWellName()
    assert wn["A01"] == "Sample1"
    assert "A01" in wn
    assert "B01" not in wn
    wn["B01"] = "Sample2"
    assert wn["B01"] == "Sample2"

def test_wellnametxt_fill():
    buff = "Header\nA01\tSample1\n\nB02\tSample2\nInvalidLine\nC03\tSample3"
    wn = WellNameTxt(buff)
    assert wn["A01"] == "Sample1"
    assert wn["B02"] == "Sample2"
    assert wn["C03"] == "Sample3"
    assert "INVALIDLINE" not in wn
