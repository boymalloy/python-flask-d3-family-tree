from app import app
from app import db
import writers
import utilities


# FIXTURES AND TESTS FOR IMPORTING FROM A CSV TO THE DATABASE
import pytest
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

# Test for creating a new tree. Uses duplicate name and receives an error.
def test_write_tree_duplicate():
    with app.app_context():
        assert writers.write_tree("Doe") == "duplicate"

# Test of creating a new tree. Uses monkeypatch's fake db to return a successful result without writing to the db
def test_write_tree_successful(fake_db):
    with app.app_context():
        result = writers.write_tree("afkjlakflkdsafj")
        assert isinstance(result, int)

# Test for adding a person
def test_write_person(fake_db):
    with app.app_context():
        result = writers.write_person(1, "Uncle Drosselmier", utilities.assemble_date(2021,10,10), "Greenwich", utilities.assemble_date("","",""))
        assert isinstance(result, int)

# Test for adding a person with duplicate data
def test_write_person():
    with app.app_context():
        assert writers.write_person(1, "John Doe", utilities.assemble_date(1980,5,15), "New text", utilities.assemble_date("","","")) == "duplicate"

# Test for setting a relationship
def test_set_relationship_successful(fake_db):
    with app.app_context():
        result =  writers.set_relationship(1,2,"union")
        assert isinstance(result, int)

# Test for setting a relationship with dulicate data
def test_set_relationship_duplicate():
    with app.app_context():
        assert writers.set_relationship(1,2,"union") == "duplicate"