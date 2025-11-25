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

def test_fetch_children_no_rels():
    children = fetchers.fetch_children(100000000000000000)
    assert children == "No children found"

def test_fetch_children_successful():
    children = fetchers.fetch_children(1)
    child1 = children[0]
    assert child1["child_id"] == 3

def test_fetch_parents_no_rels():
    parents = fetchers.fetch_parents(100000000000000000)
    assert parents == "No parents found"

def test_fetch_parents_successful():
    parents = fetchers.fetch_parents(3)
    parent1 = parents[0]
    assert parent1["parent_id"] == 1 or 2