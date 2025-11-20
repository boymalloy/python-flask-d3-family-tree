from datetime import date

# Assemble a date from 3 inputs. 
# Note: returns None if a blank year is given - useful for forms
def assemble_date(birth_year, birth_month, birth_day):
    
    # if nothing has been input, return None
    if birth_year == "":
        return None
    
    try:
        # put the 3 parts of the dob together and put it in the correct data type
        return date(int(birth_year), int(birth_month), int(birth_day))
    
    # Catch and return any exceptions
    except Exception as e:
        return "Invalid date"
    
# Take a date as it comes out of the DB and split it into 3 parts stored in a dict
def disassemble_date(date):
    
    try:
        # If no date has been provided, skip everything and return None
        if not date:
            return None
        
        # Make an empty dict
        date_dict = {
            "year": None,
            "Month": None,
            "day": None,
        }
        
        # converst the date to a string
        date_string = str(date)
       
        # split the string and store the parts in the dict
        date_dict["year"], date_dict["month"], date_dict["day"] = map(int, date_string.split('-'))
        
        # return the dict
        return date_dict
    
    # Catch and return any exceptions
    except Exception as e:
        return "Date dissassembly failure"