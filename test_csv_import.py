from app import app
from app import db
import csv_import
import pandas as pd
from sqlalchemy.exc import IntegrityError

# FIXTURES AND TESTS FOR IMPORTING FROM A CSV TO THE DATABASE
import pytest
# Turn off debug mode for these tests so that we get the real utputs, not the debug outputs
@pytest.fixture
def force_debug_false(monkeypatch):
    monkeypatch.setattr(app, "debug", False, raising=False)

# Create a fake_db
@pytest.fixture
def fake_db(monkeypatch):
    
    # Make a fake result to use in the faked db calls
    class FakeResult:
        def scalar(self):
            return 1

    # Patch the 'commit' method to do nothing.
    monkeypatch.setattr(db.session, "commit", lambda: None)

    # Patch the 'execute' method so that any call returns a FakeResult.
    monkeypatch.setattr(db.session, "execute", lambda *a, **k: FakeResult())

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



# test the allowable file extensions for the upload form
def test_allowed_file():
    assert csv_import.allowed_file("file.csv") == True
    assert csv_import.allowed_file("file.doc") == False

# Tests tree_name_db_check without touching the real database.
# Uses fake_db fixture (which patches commit/execute globally),
# then monkeypatches execute again to simulate True/False results
def test_tree_name_db_check(fake_db, monkeypatch):
    with app.app_context():
        # Simulate a matching tree found in DB ---
        class FakeResultTrue:
            def scalar(self): return 1

        monkeypatch.setattr(db.session, "execute", lambda *a, **k: FakeResultTrue())
        assert csv_import.tree_name_db_check("Doe") is True

        # Simulate no matching tree found in DB ---
        class FakeResultFalse:
            def scalar(self): return None  

        monkeypatch.setattr(db.session, "execute", lambda *a, **k: FakeResultFalse())
        assert csv_import.tree_name_db_check("afasdfjadflkjaslkfjakjdf") is False

# Uses the fixtures to fake an attempt to write to the person table
# Retrns a fake integrity error to simulate an attempt to import data that is already in the db
def test_write_people_to_person_dupes(fake_db, to_sql_raises_integrity, force_debug_false):
    with app.app_context():
        df = pd.read_csv("static/input/test_data_people_existing_prepped.csv")
        out = csv_import.write_people_to_person(df)
        assert out == "Dupes!"

# Uses the fixtures to fake an attempt to write to the person table
def test_write_people_to_person_unique(fake_db, to_sql_noop):
    with app.app_context():
        df = pd.read_csv("static/input/test_data_people_unique_prepped.csv")
        out = csv_import.write_people_to_person(df)
        assert out == True

# Uses the fixtures to fake an attempt to write to the relationships table
# Retrns a fake integrity error to simulate an attempt to import data that is already in the db
def test_write_relationships_df_to_relationships_db_dupes(fake_db, to_sql_raises_integrity, force_debug_false):
    with app.app_context():
        df = pd.read_csv("static/input/test_data_relationships_existing_prepped.csv")
        out = csv_import.write_relationships_df_to_relationships_db(df)
        assert out == "Dupes!"

# Uses the fixtures to fake an attempt to write to the relationships table
def test_write_relationships_df_to_relationships_db_unique(fake_db, to_sql_noop):
    with app.app_context():
        df = pd.read_csv("static/input/test_data_relationships_unique_prepped.csv")
        out = csv_import.write_relationships_df_to_relationships_db(df)
        assert out == True

# test the fetching of a person's id using the name and dob of someone we know is in the db
def test_fetch_person_id():
    with app.app_context():
        assert csv_import.fetch_person_id("John Doe",1980,5,15) == 1
        assert csv_import.fetch_person_id("Chastity Boonswoggle",1980,5,15) == "Person not found"

# test the prep_relationships function to see whether it returns a dataframe
def test_prep_relationships():
    with app.app_context():
        result = csv_import.prep_relationships("static/input/test_data_relationships.csv")
        assert isinstance(result, pd.DataFrame)

# test the prep_people function to see whether it returns a dataframe
def test_prep_people(fake_db):
    with app.app_context():
        result, tree_id = csv_import.prep_people("static/input/test_data_people.csv")
        assert isinstance(result, pd.DataFrame)
        assert isinstance(tree_id, int)