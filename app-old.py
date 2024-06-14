from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

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

    return "Squeeeeee"

def test_generator():
    assert generator() == "Squeeeeee"

def generator2():
    # import the user friendly csv into a dataframe
    uf = pd.read_csv("static/input/input.csv")

    # build the persons dataframe with data from uf
    persons = pd.DataFrame()
    persons.loc[:, 'id'] = uf.loc[:, 'id']
    persons.loc[:, 'name'] = uf.loc[:, 'name']
    persons["own_unions"] = ""
    persons.loc[:, 'birthyear'] = uf.loc[:, 'birthyear']
    persons.loc[:, 'birthplace'] = uf.loc[:, 'birthplace']
    return persons


def establish_dataframes():
    # import the user friendly csv into a dataframe
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
    
    return uf

def build_union(uf_iteration):
    
    # a function to check a row of the unions table to see whether it contains a union for 2 given people
    def checkRowForUnion(person1,person2,unionToCheck):
        x = unionToCheck.split(",")
        personA = x[0]
        personB = x[1]

        if (person1 == personA and person2 == personB) or (person1 == personB and person2 == personA) :
            result = "match"
        else:
            result = "no match"
        return(result)

    # a function to check ALL rows of the unions table to see whether it contains a union for 2 given people
    def checkAllRowsForUnion(A,B):
        condition = 0
        for index, row in unions.iterrows():
            if checkRowForUnion(A,B,unions.loc[index,'partners']) == "match":
                condition = condition + 1
        return(condition)

    # uses person and partner from the row number of uf passed to the function
    person = uf.loc[uf_iteration,'id']
    partner = uf.loc[uf_iteration,'partners']
   

    # test data 
    # person = "bbb"
    # partner ="ccc"
    
    unionCheck = checkAllRowsForUnion(person,partner)
    
    if unionCheck > 0:
        return "not done"
        
    if unionCheck == 0:
        # TO DO: proper union number
        row_id = "uX"
        row_partners = str(person + "," + partner)
        # TO DO add the children
        row_children = ""
        
        # Create a dictionary with the data for the new row
        row = {'id': row_id, 'partners': row_partners, 'children': row_children}

        # Append the dictionary to the DataFrame
        unions.loc[len(unions)] = row
        
        return unions



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/treegenerator')
def treegenerator():
    return render_template('treegenerator.html', generator=generator)

@app.route('/treegenerator2')
def treegenerator2():
    return render_template('treegenerator2.html', generator2=generator2)

@app.route('/uniontester')
def uniontester():
    return render_template('uniontester.html', build_union=build_union, establish_dataframes=establish_dataframes)