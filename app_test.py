import app 
import pandas as pd

def test_get_partners():
    assert app.get_partners(1) == [2]
    assert app.get_partners(1) == [2]

def test_get_children():
    assert app.get_children(1) == [3, 4, 5]
    assert app.get_children(2) == [3, 4, 5]

def test_fetch_tree():
    assert app.fetch_tree() == "Tree fetched successfully"

def test_get_children_together():
    
    test_data = {
                'children': [[3,4,5],[3,4,5],[6,7],[6,7],[8]]
            }
            
    test_df = pd.DataFrame(test_data)
    test_df.index = range(1, len(test_df) + 1)
    
    assert app.get_children_together(1, 2, test_df) == [3, 4, 5]
    assert app.get_children_together(1, 3, test_df) == []
    assert app.get_children_together(1, 1, test_df) == "same person"

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
