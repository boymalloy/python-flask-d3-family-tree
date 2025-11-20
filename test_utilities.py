import utilities
from datetime import date

# Test assemble a date with valid inputs
def test_assemble_date_valid():
    result =  utilities.assemble_date(2025, 11, 11)
    assert isinstance(result, date)

 # Test assemble a date with various rubbish inputs
def test_assemble_date_invalid():
    assert utilities.assemble_date(2025, 11, 31) == "Invalid date"
    assert utilities.assemble_date("text", 11, 11) == "Invalid date"

# Test assemble a date with blank inputs
def test_assemble_date_blank():
    assert utilities.assemble_date("","","") == None

def test_disassemble_date_valid():
    date = utilities.assemble_date(2025, 11, 19)
    result = utilities.disassemble_date(date)
    assert result['year'] == 2025
    assert result['month'] == 11
    assert result ['day'] == 19

def test_disassemble_date_blank():
    result = utilities.disassemble_date(None)
    assert result == None

def test_disassemble_date_invalid():
    result = utilities.disassemble_date("something invalid")
    assert result == "Date dissassembly failure"