import app 
import pandas as pd

def test_fetch_partners_from_db():
    assert app.fetch_partners_from_db(1) == [2]
    assert app.fetch_partners_from_db(1) == [2]

def test_fetch_children_from_db():
    assert app.fetch_children_from_db(1) == [3, 4, 5]
    assert app.fetch_children_from_db(2) == [3, 4, 5]

def test_fetch_tree():
    assert app.fetch_tree() == "Tree fetched successfully"

def test_get_children_together_from_df():
    
    test_data = {
                'children': [[3,4,5],[3,4,5],[6,7],[6,7],[8]]
            }
            
    test_df = pd.DataFrame(test_data)
    test_df.index = range(1, len(test_df) + 1)
    
    assert app.get_children_together_from_df(1, 2, test_df) == [3, 4, 5]
    assert app.get_children_together_from_df(1, 3, test_df) == []
    assert app.get_children_together_from_df(1, 1, test_df) == "same person"

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

def test_check_for_existing_union_in_df():
    test_union_1 = [1,2]
    test_union_2 = [2,1]
    test_union_3 = [1,3]
    
    test_data = pd.DataFrame({'partner': [[1,2],[3,4],[6,7]]})
    
    
    assert app.check_for_existing_union_in_df(test_union_1,test_data) == True
    assert app.check_for_existing_union_in_df(test_union_2,test_data) == True
    assert app.check_for_existing_union_in_df(test_union_3,test_data) == False

def test_tree_name_db_check():
    assert app.tree_name_db_check("Doe Family Tree") == True
    assert app.tree_name_db_check("Pinkle Family Tree") == False