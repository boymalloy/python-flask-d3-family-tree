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

def test_prep_import(tmp_path, monkeypatch):
    # Create temporary CSV files
    people_file = tmp_path / "people.csv"
    relationships_file = tmp_path / "relationships.csv"

    people_data = """name,birth_date,tree_name
John Doe,1980-05-15,Doe Family Tree
Jane Doe,1982-07-20,Doe Family Tree
"""
    relationships_data = """person1_id,person2_id,relationship
1,2,spouse
1,3,parent
2,3,parent
"""

    people_file.write_text(people_data)
    relationships_file.write_text(relationships_data)

    # Mock the DB check so we don't hit a real DB
    monkeypatch.setattr(app, "tree_name_db_check", lambda name: False)
    monkeypatch.setattr(app.db.session, "commit", lambda: None)

    class FakeResult:
        def scalar(self):
            return 1

    monkeypatch.setattr(app.db.session, "execute", lambda *a, **k: FakeResult())

    # Call prep_import with our temp files
    result = app.prep_import(str(people_file), str(relationships_file))

    # Assert: result is a DataFrame with expected columns and tree_id filled
    assert isinstance(result, pd.DataFrame)
    assert "tree_id" in result.columns
    assert len(result) == 2  # two people from the CSV