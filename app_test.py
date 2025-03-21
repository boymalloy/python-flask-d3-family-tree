# test_app.py
import app 

def test_get_partners():
    assert app.get_partners(1) == [2]
    assert app.get_partners(1) == [2]

def test_get_children():
    assert app.get_children(1) == [3, 4, 5]
    assert app.get_children(2) == [3, 4, 5]