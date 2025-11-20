from app import app
from app import db
import fetchers

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

def test_fetch_relationships_df_successful():
    rels = fetchers.fetch_relationships_df(1)
    assert rels.loc[0,"person2_id"] == 2

def test_fetch_relationships_df_none():
    rels = fetchers.fetch_relationships_df(100000000000000000)
    assert rels == "No relationships found"

def test_fetch_partners_no_rels():
    partners = fetchers.fetch_partners(100000000000000000)
    assert partners == "No partners found"

def test_fetch_partners_successful():
    partners = fetchers.fetch_partners(1)
    partner1 = partners[0]
    assert partner1["partner_id"] == 2

def test_fetch_partners_not_self():
    self = 1
    partners = fetchers.fetch_partners(self)
    partner1 = partners[0]
    assert partner1["partner_id"] != self