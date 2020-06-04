import pytest
from read_excel import SheetParser


def test_working():
    parser = SheetParser()
    assert not parser.errors


def test_working_parser():
    parser = SheetParser()
    parser.parse("rechner.xlsx")
    assert not parser.errors

def test_working_invalid_filename():
    parser = SheetParser()
    with pytest.raises(IOError):
        parser.parse("nosuchfile.xlsx")
