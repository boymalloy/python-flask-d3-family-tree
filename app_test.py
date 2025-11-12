import app 
import pandas as pd
import pytest
from sqlalchemy.exc import IntegrityError
import pytest

# FIXTURES AND TESTS FOR IMPORTING FROM A CSV TO THE DATABASE

# Turn off debug mode for these tests so that we get the real utputs, not the debug outputs
@pytest.fixture
def force_debug_false(monkeypatch):
    monkeypatch.setattr(app.app, "debug", False, raising=False)

# Create a fake_db
@pytest.fixture
def fake_db(monkeypatch):
    
    # Make a fake result to use in the faked db calls
    class FakeResult:
        def scalar(self):
            return 1

    # Patch the 'commit' method to do nothing.
    monkeypatch.setattr(app.db.session, "commit", lambda: None)

    # Patch the 'execute' method so that any call returns a FakeResult.
    monkeypatch.setattr(app.db.session, "execute", lambda *a, **k: FakeResult())

# Make DataFrame.to_sql a no-op so nothing is written to the real DB
@pytest.fixture
def to_sql_noop(monkeypatch):
    def fake_to_sql(self, name, con, if_exists="append", index=False, method="multi", **kwargs):
        return None  # simulates successful insert without touching DB
    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql, raising=True)

# Make DataFrame.to_sql raise IntegrityError to simulate duplicate rows/constraints
@pytest.fixture
def to_sql_raises_integrity(monkeypatch):
    def fake_to_sql(self, name, con, if_exists="append", index=False, method="multi", **kwargs):
        raise IntegrityError("dupe", params=None, orig=Exception("duplicate key"))
    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql, raising=True)


# Tests tree_name_db_check without touching the real database.
# Uses fake_db fixture (which patches commit/execute globally),
# then monkeypatches execute again to simulate True/False results
def test_tree_name_db_check(fake_db, monkeypatch):
    # Simulate a matching tree found in DB ---
    class FakeResultTrue:
        def scalar(self): return 1

    monkeypatch.setattr(app.db.session, "execute", lambda *a, **k: FakeResultTrue())
    assert app.tree_name_db_check("Doe") is True

    # Simulate no matching tree found in DB ---
    class FakeResultFalse:
        def scalar(self): return None  

    monkeypatch.setattr(app.db.session, "execute", lambda *a, **k: FakeResultFalse())
    assert app.tree_name_db_check("afasdfjadflkjaslkfjakjdf") is False

# Uses the fixtures to fake an attempt to write to the person table
# Retrns a fake integrity error to simulate an attempt to import data that is already in the db
def test_write_people_to_person_dupes(fake_db, to_sql_raises_integrity, force_debug_false):
    df = pd.read_csv("static/input/test_data_people_existing_prepped.csv")
    out = app.write_people_to_person(df)
    assert out == "Dupes!"

# Uses the fixtures to fake an attempt to write to the person table
def test_write_people_to_person_unique(fake_db, to_sql_noop):
    df = pd.read_csv("static/input/test_data_people_unique_prepped.csv")
    out = app.write_people_to_person(df)
    assert out == True

# Uses the fixtures to fake an attempt to write to the relationships table
# Retrns a fake integrity error to simulate an attempt to import data that is already in the db
def test_write_relationships_df_to_relationships_db_dupes(fake_db, to_sql_raises_integrity, force_debug_false):
    df = pd.read_csv("static/input/test_data_relationships_existing_prepped.csv")
    out = app.write_relationships_df_to_relationships_db(df)
    assert out == "Dupes!"

# Uses the fixtures to fake an attempt to write to the relationships table
def test_write_relationships_df_to_relationships_db_unique(fake_db, to_sql_noop):
    df = pd.read_csv("static/input/test_data_relationships_unique_prepped.csv")
    out = app.write_relationships_df_to_relationships_db(df)
    assert out == True

# Using data that we know is in the db, check that a subject's partner is fetched
def test_fetch_partners_from_db():
    assert app.fetch_partners_from_db(1) == [2]
    assert app.fetch_partners_from_db(1) == [2]

# Using data that we know is in the db, check that a subject's children are fetched
def test_fetch_children_from_db():
    assert set(app.fetch_children_from_db(1)) == {3, 4, 5}
    assert set(app.fetch_children_from_db(2)) == {3, 4, 5}


# finds from the persons dataframe all the children of two people 
def test_get_children_together_from_df():
    
    test_data = {
                'children': [[3,4,5],[3,4,5],[6,7],[6,7],[8]]
            }
            
    test_df = pd.DataFrame(test_data)
    test_df.index = range(1, len(test_df) + 1)
    
    assert app.get_children_together_from_df(1, 2, test_df) == [3, 4, 5] # rows 1 and 2 have 3 children in common
    assert app.get_children_together_from_df(1, 3, test_df) == [] # rows 1 and 3 have no children in common
    assert app.get_children_together_from_df(1, 1, test_df) == "same person" # looking at row 1 twices gives an error


# adds data to a a row in the unions dataframe - the 2 people in the union and any children
def test_make_union_row():
    test_data = {
        1: [[3, 4, 5]],  
        2: [[3, 4, 5]],
        3: [[6, 7]],
        4: [[6, 7]],
        5: [[8]]
    }

    test_df = pd.DataFrame.from_dict(test_data, orient='index', columns=['children'])

    result = app.make_union_row(1, 2, test_df)
    expected = {'partner': [1, 2], 'children': [3, 4, 5]}

    assert set(result['partner']) == set(expected['partner'])
    assert set(result['children']) == set(expected['children'])

# checks the union df for a union (two person ids in any order)
def test_check_for_existing_union_in_df():
    test_union_1 = [1,2]
    test_union_2 = [2,1]
    test_union_3 = [1,3]
    test_data = pd.DataFrame({'partner': [[1,2],[3,4],[6,7]]})
    
    
    assert app.check_for_existing_union_in_df(test_union_1,test_data) == True
    assert app.check_for_existing_union_in_df(test_union_2,test_data) == True
    assert app.check_for_existing_union_in_df(test_union_3,test_data) == False

# test the fetching of a person's id using the name and dob of someone we know is in the db
def test_fetch_person_id():
    assert app.fetch_person_id("John Doe",1980,5,15) == 1
    assert app.fetch_person_id("Chastity Boonswoggle",1980,5,15) == "Person not found"

# test the prep_relationships function to see whether it returns a dataframe
def test_prep_relationships():
    result = app.prep_relationships("static/input/test_data_relationships.csv")
    assert isinstance(result, pd.DataFrame)

# test the prep_people function to see whether it returns a dataframe
def test_prep_people(fake_db):
    result, tree_id = app.prep_people("static/input/test_data_people.csv")
    assert isinstance(result, pd.DataFrame)
    assert isinstance(tree_id, int)

# test the allowable file extensions for the upload form
def test_allowed_file():
    assert app.allowed_file("file.csv") == True
    assert app.allowed_file("file.doc") == False

# when building the tree you need to start from a particular person. This funtion searches for the first person listed with a given tree id and uses that as the start of the tree
def test_fetch_first_person():
    # Searches for a known person in a known tree
    assert app.fetch_first_person(1) == 1
    # searches for a tree id that doesn't exist
    assert app.fetch_first_person(1000000000000) == "Person not found"

# Test for creating a new tree. Uses duplicate name and receives an error.
def test_write_tree_duplicate():
    assert app.write_tree("Doe") == "duplicate"

# Test of creating a new tree. Uses monkeypatch's fake db to return a successful result without writing to the db
def test_write_tree_successful(fake_db):
    result = app.write_tree("afkjlakflkdsafj")
    assert isinstance(result, int)

# Tests for fetching the name of a tree - working and not found
def test_fetch_tree_name():
    assert app.fetch_tree_name(1) == "Doe"
    assert app.fetch_tree_name(10000000000000000000) == "Tree not found"

# Test assemble a date with valid inputs
def test_assemble_date_valid():
    from datetime import date
    result =  app.assemble_date(2025, 11, 11)
    assert isinstance(result, date)

 # Test assemble a date with various rubbish inputs
def test_assemble_date_invalid():
    assert app.assemble_date(2025, 11, 31) == "Invalid date"
    assert app.assemble_date("text", 11, 11) == "Invalid date"

# Test assemble a date with blank inputs
def test_assemble_date_blank():
    assert app.assemble_date("","","") == None

# Test for adding a person
def test_write_person(fake_db):
    result = app.write_person(1, "Uncle Drosselmier", app.assemble_date(2021,10,10), "Greenwich", app.assemble_date("","",""))
    assert isinstance(result, int)

# Test for adding a person with duplicate data
def test_write_person():
    assert app.write_person(1, "John Doe", app.assemble_date(1980,5,15), "New text", app.assemble_date("","","")) == "duplicate"

# Test for setting a relationship
def test_set_relationship_successful(fake_db):
    result =  app.set_relationship(1,2,"union")
    assert isinstance(result, int)

# Test for setting a relationship with dulicate data
def test_set_relationship_duplicate():
    assert app.set_relationship(1,2,"union") == "duplicate"