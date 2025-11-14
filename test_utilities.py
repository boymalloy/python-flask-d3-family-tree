import utilities

# Test assemble a date with valid inputs
def test_assemble_date_valid():
    from datetime import date
    result =  utilities.assemble_date(2025, 11, 11)
    assert isinstance(result, date)

 # Test assemble a date with various rubbish inputs
def test_assemble_date_invalid():
    assert utilities.assemble_date(2025, 11, 31) == "Invalid date"
    assert utilities.assemble_date("text", 11, 11) == "Invalid date"

# Test assemble a date with blank inputs
def test_assemble_date_blank():
    assert utilities.assemble_date("","","") == None