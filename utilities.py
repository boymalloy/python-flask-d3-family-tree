# Assemble a date from 3 inputs. 
# Note: returns None if a blank year is given - useful for forms
from datetime import date
def assemble_date(birth_year, birth_month, birth_day):
    
    # if nothing has been input, return None
    if birth_year == "":
        return None
    
    try:
        # put the 3 parts of the dob together and put it in the correct data type
        from datetime import date
        return date(int(birth_year), int(birth_month), int(birth_day))
    
    # Catch and return any exceptions
    except Exception as e:
        return "Invalid date"