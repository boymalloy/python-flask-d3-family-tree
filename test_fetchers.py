from app import app
from app import db
import fetchers
import pandas as pd

# Tests for fetching the name of a tree - working and not found
def test_fetch_tree_name():
    assert fetchers.fetch_tree_name(1) == "Doe"
    assert fetchers.fetch_tree_name(10000000000000000000) == "Tree not found"

# Tests for fetch_person
def test_fetch_person_successful():
    person = fetchers.fetch_person(1)
    assert person.name == "John Doe"
    assert person.birth_place == "New York"

# Tests for fetch_person
def test_fetch_person_notfound():
    person = fetchers.fetch_person(10000000000000000000)
    assert person == "Person not found"


def test_fetch_person_details_ob():
    with app.app_context():
        from classes import Person
        row1 = fetchers.fetch_person_details_ob(1)
        assert isinstance(row1, Person)
        assert row1 is not None
        fakerow = fetchers.fetch_person_details_ob(1000000000000000000000)
        assert fakerow == "Person not found" 

def test_fetch_all_people_in_tree():
    tree1 = fetchers.fetch_all_people_in_tree(1)
    notree = fetchers.fetch_all_people_in_tree(100000000000000000000)
    assert isinstance(tree1, list)
    assert isinstance(notree, list)
    assert len(tree1) > 0
    assert len(notree) == 0