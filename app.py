from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import re

# Set pandas display options to prevent truncation
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

app = Flask(__name__)

# creates a path to all the static files for the tree and the csv inputs
app = Flask(__name__, static_url_path='/static')

bootstrap = Bootstrap(app)

def generator3():
    
    uf = pd.read_csv("static/input/input.csv")

    # build the persons dataframe with data from uf
    persons = pd.DataFrame()
    persons.loc[:, 'id'] = uf.loc[:, 'id']
    persons.loc[:, 'name'] = uf.loc[:, 'name']
    persons["own_unions"] = None
    persons.loc[:, 'birthyear'] = uf.loc[:, 'birthyear']
    persons.loc[:, 'birthplace'] = uf.loc[:, 'birthplace']
    persons.loc[:, 'partners'] = uf.loc[:, 'partners']
    
    #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partner' : pd.Series(dtype='object'),
                    'children': pd.Series(dtype='str')})

    
    # for every row in the user friendly table
    for index, row in persons.iterrows():
        
        # get the union
        partnership = [persons.loc[index, 'id'], str(persons.loc[index, 'partners'])]

        # ... and the same union in reverse order
        reverse = [str(persons.loc[index, 'partners']), persons.loc[index, 'id']]
        
        # if either version of the union is already in the unions table, do nothing
        if unions['partner'].apply(lambda x: x == partnership or x == reverse).any():
            print("nothing")
        # else if the union hasn't been recorded yet...
        else:
            # if the union isn't there, stop
            if pd.isna(persons.loc[index,'partners']):
                print("nothing")
            # but if it is there....
            else:
               # if this is the first union in the dataframe, call it u1
                if unions.empty:
                    NEWunionID = "u1"
                
                else:
                    # else get the last union number and give this union the next number on
                    OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])
                    NEWunionID = "u" + str(int(OLDunionID[1]) + 1)
                
                # write the new union id to the person that the current iteration is on
                persons.loc[index,'own_unions'] = NEWunionID

                # write the union id to the partners row in the persons table
                who = str(persons.loc[index,'partners'])
                persons.loc[persons['id'] == who, 'own_unions'] = NEWunionID

                # create a dictionary with the data to write to the dataframe
                row = {'id': NEWunionID, 'partner': partnership, 'children': "GVMM2018"}
                    
                # Append the dictionary to the DataFrame
                unions.loc[len(unions)] = row
    
    
    # Fixes the children field in the union table by putting it into an array (kind of)
    # for index, row in unions.iterrows():
        # unions.at[index, 'children'] = [unions.at[index, 'children']]
    
    # Sets the index of the unions table to be the custom id but preserves the custom id as it's own field by copying it
    unions['id_copy'] = unions['id']
    unions.set_index('id', inplace=True,)
    unions = unions.rename(columns={'id_copy': 'id'})
    unions = unions.reindex(columns=['id', 'partner', 'children'])

    # Fixes the own_unions field in the persons table by putting it into an array (kind of)
    for index, row in persons.iterrows():
        persons.at[index, 'own_unions'] = [persons.at[index, 'own_unions']]

    # Sets the index of the persons table to be the cuustom id 
    persons.set_index('id', inplace=True)

    # turns the dataframe into the persons fragment of the tree json
    persons_json = persons.to_json(orient="index")

    # turn the unions df to json
    unions_json = unions.to_json(orient="index")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\"AJM1980\",\"persons\":"

    bitbetween = ",\"unions\": "

    # hard codes the end bit of the tree json, including unions and links
    end = ", \"links\": [[\"AJM1980\", \"u1\"], [\"EAM1982\", \"u1\"], [\"u1\", \"GVMM2018\"],[\"u1\", \"TTMM2012\"],]}"

    # combines all of the bits of the tree together
    assembled = start + persons_json + bitbetween + unions_json + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "w",) as file_Obj:
        file_Obj.write(assembled)

    return assembled

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/treegenerator')
def treegenerator():
    return render_template('treegenerator.html', generator=generator)

@app.route('/treegenerator2')
def treegenerator2():
    return render_template('treegenerator2.html', generator2=generator2)

@app.route('/treegenerator3')
def treegenerator3():
    return render_template('treegenerator3.html', generator3=generator3)

@app.route('/general_test')
def peepee():
    return render_template('general_test.html', general_test=general_test)