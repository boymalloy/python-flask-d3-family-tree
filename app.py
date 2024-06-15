from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import re

app = Flask(__name__)

# creates a path to all the static files for the tree and the csv inputs
app = Flask(__name__, static_url_path='/static')

bootstrap = Bootstrap(app)

def generator():
    # imports 3 people from a csv to a dataframe
    data = pd.read_csv("static/input/ids.csv", dtype=str)

    # fixes the union ids in the dataframe
    data.at[0, 'own_unions'] = ['u1']
    data.at[1, 'own_unions'] = ['u1']

    # turns the dataframe into the persons fragment of the tree json
    fragment = data.to_json(orient="index")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\"0\",\"persons\":"

    # hard codes the end bit of the tree json, including unions and links
    end = ",\"unions\": {\"u1\": { \"id\": \"u1\", \"partner\": [\"0\", \"1\"], \"children\": [\"2\"] }, }, \"links\": [[\"0\", \"u1\"], [\"1\", \"u1\"], [\"u1\", \"2\"],]}"

    # combines all of the bits of the tree together
    assembled = start + fragment + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "x",) as file_Obj:
        file_Obj.write(assembled)

    return "complete"

def test_generator():
    assert generator() == "complete"

def generator2():

    uf = pd.read_csv("static/input/input.csv")

    # build the persons dataframe with data from uf
    persons = pd.DataFrame()
    persons.loc[:, 'id'] = uf.loc[:, 'id']
    persons.loc[:, 'name'] = uf.loc[:, 'name']
    persons["own_unions"] = ""
    persons.loc[:, 'birthyear'] = uf.loc[:, 'birthyear']
    persons.loc[:, 'birthplace'] = uf.loc[:, 'birthplace']
    
    #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partners' : pd.Series(dtype='str'),
                    'children': pd.Series(dtype='str')})

    
    for index, row in uf.iterrows():
        
        partnership = uf.loc[index,'id'] + "," +  str(uf.loc[index,'partners'])
        reverse = str(uf.loc[index,'partners']) + "," +  uf.loc[index,'id']
        
        if unions.isin([partnership,reverse]).any().any():
            print("nothing")
        else:
            
            if unions.empty:
                NEWunionID = "u1"
            else:
                OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])
                NEWunionID = "u" + str(int(OLDunionID[1]) + 1)
            
            row = {'id': NEWunionID, 'partners': partnership, 'children': "child"}
                
            # Append the dictionary to the DataFrame
            unions.loc[len(unions)] = row
        
            
    return unions

def test_generator2():
    assert generator2() == "complete"

def general_test():
     #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partners' : pd.Series(dtype='str'),
                    'children': pd.Series(dtype='str')})
    
    row = {'id': "u1", 'partners': "mock data", 'children': "child"}
                
    # Append the dictionary to the DataFrame
    unions.loc[len(unions)] = row

    row2 = {'id': "u2", 'partners': "words", 'children': "kids"}
                
    # Append the dictionary to the DataFrame
    unions.loc[len(unions)] = row2

    OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])

    NEWunionID = "u" + str(int(OLDunionID[1]) + 1)

    if not unions.empty:
        return "data ahoy"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/treegenerator')
def treegenerator():
    return render_template('treegenerator.html', generator=generator)

@app.route('/treegenerator2')
def treegenerator2():
    return render_template('treegenerator2.html', generator2=generator2)

@app.route('/general_test')
def peepee():
    return render_template('general_test.html', general_test=general_test)
# hello