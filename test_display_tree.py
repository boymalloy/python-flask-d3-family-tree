import display_tree
from app import app
import pandas as pd

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

    result = display_tree.make_union_row(1, 2, test_df)
    expected = {'partner': [1, 2], 'children': [3, 4, 5]}

    assert set(result['partner']) == set(expected['partner'])
    assert set(result['children']) == set(expected['children'])
    
# Using data that we know is in the db, check that a subject's partner is fetched
def test_fetch_partners_from_db():
    with app.app_context():
        assert display_tree.fetch_partners_from_db(1) == [2]
        assert display_tree.fetch_partners_from_db(1) == [2]

# Using data that we know is in the db, check that a subject's children are fetched
def test_fetch_children_from_db():
    with app.app_context():
        assert set(display_tree.fetch_children_from_db(1)) == {3, 4, 5}
        assert set(display_tree.fetch_children_from_db(2)) == {3, 4, 5}

# when building the tree you need to start from a particular person. This funtion searches for the first person listed with a given tree id and uses that as the start of the tree
def test_fetch_first_person():
    with app.app_context():
        # Searches for a known person in a known tree
        assert display_tree.fetch_first_person(1) == 1
        # searches for a tree id that doesn't exist
        assert display_tree.fetch_first_person(1000000000000) == "Person not found"

# finds from the persons dataframe all the children of two people 
def test_get_children_together_from_df():
    
    test_data = {
                'children': [[3,4,5],[3,4,5],[6,7],[6,7],[8]]
            }
            
    test_df = pd.DataFrame(test_data)
    test_df.index = range(1, len(test_df) + 1)
    
    assert display_tree.get_children_together_from_df(1, 2, test_df) == [3, 4, 5] # rows 1 and 2 have 3 children in common
    assert display_tree.get_children_together_from_df(1, 3, test_df) == [] # rows 1 and 3 have no children in common
    assert display_tree.get_children_together_from_df(1, 1, test_df) == "same person" # looking at row 1 twices gives an error