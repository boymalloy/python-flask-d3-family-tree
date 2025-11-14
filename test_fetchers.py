from app import app
from app import db
import fetchers

# Tests for fetching the name of a tree - working and not found
def test_fetch_tree_name():
    assert fetchers.fetch_tree_name(1) == "Doe"
    assert fetchers.fetch_tree_name(10000000000000000000) == "Tree not found"