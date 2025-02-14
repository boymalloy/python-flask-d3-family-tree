from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import numpy as np
import pandas as pd
import re
import json
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import text

# Set pandas display options to prevent truncation
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Create the Flask app and configure it
app = Flask(__name__, static_url_path='/static')
bootstrap = Bootstrap(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Route: Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Tree generator
@app.route('/treegenerator3')
def treegenerator3():
    return render_template('treegenerator3.html', generator3=generator3)

# Route: Database connection test
@app.route('/test_db')
def test_db():
    try:
        with app.app_context():
            result = db.session.execute(text('SELECT 1')).fetchone()
            return f"Database connection successful! Result: {result[0]}"
    except Exception as e:
        return f"Database connection failed: {e}", 500

# Route: Fetch data and pass JSON to the Jinja template
@app.route('/json')
def jsontest():
    try:
        # Use the app context to access the database session
        with app.app_context():
            query = text("SELECT * FROM persons")
            result = db.session.execute(query)

            # Fetch all rows and get column names
            rows = result.fetchall()
            col_names = result.keys()  # Retrieve column names from the result object

            # Convert rows to a list of dictionaries
            data = [dict(zip(col_names, row)) for row in rows]

            # Render the Jinja template and pass the data
            return render_template('jsontest.html', data=data)

    except Exception as e:
        # Handle exceptions and render an error message in the template
        return render_template('jsontest.html', error=f"Error fetching data: {e}")

from sqlalchemy.sql import text

def get_partners(subject):
    with app.app_context():
        # Use a parameterized query
        query = text("""
            SELECT person2_id 
            FROM relationships 
            WHERE person1_id = :subject 
              AND (relationship = 'spouse' OR relationship = 'union')
        """)
        
        # Execute the query with the parameter
        result = db.session.execute(query, {"subject": subject})
        
         # Fetch all rows
        rows = result.fetchall()

        # Convert tuples to a list of integers
        partners = [int(row[0]) for row in rows]

        return partners

def get_children(subject):
    with app.app_context():
        # Use a parameterized query
        query = text("""
            SELECT person2_id FROM relationships WHERE person1_id = :subject AND relationship = 'parent'
        """)
        
        # Execute the query with the parameter
        result = db.session.execute(query, {"subject": subject})
        
        # Fetch all rows
        rows = result.fetchall()

        # Convert tuples to a list of integers
        children = [int(row[0]) for row in rows]

        return children


        
            

    
def freshstart():
    return "Hello world"


@app.route('/thing')
def thing():
    return render_template('run.html', header="Tree from db", payload=freshstart())

@app.route('/panda_original')
def originalpanda():
    file_path = "static/input/"
    file_path_and_name = file_path + str("x.csv")
    uf = pd.read_csv(file_path_and_name)
     
     
     # Build the persons dataframe with data from uf
    persons = pd.DataFrame({
        'id': uf['id'].apply(lambda x: x.strip() if isinstance(x, str) else x),  # Remove spaces from 'id'
        'name': uf['name'],  
        'own_unions': [[] for _ in range(len(uf))],  # Initialize as empty lists for each row
        'birthyear': uf['birthyear'],
        'birthplace': uf['birthplace'],
        'partners': uf['partners'].apply(lambda z: [p.strip() for p in z.split(',')] if pd.notna(z) else []),  # Strip each partner
        'children': uf['children'].apply(lambda x: [c.strip() for c in x.split(',')] if pd.notna(x) else [])  # Strip each child
    })

    return render_template('pandatest.html', data=persons)


def pandatest():
    try:
        # Use the app context to access the database session
        with app.app_context():
            query = text("SELECT * FROM person")
            result = db.session.execute(query)

            # Fetch all rows and get column names
            rows = result.fetchall()
            col_names = result.keys()  # Retrieve column names from the result object

            # Make a data frame from the fetched rows and column names
            persons = pd.DataFrame(rows, columns=col_names)
            
            # Add empty columns for partners, children and own unions
            persons["partners"] = None
            persons["children"] = None

            # start the index of the df from 1 to match the ids in the db
            persons.index = range(1, len(persons) + 1)

            # Loop through each person in the data frame, gets the id of each of their partners from the db, writes the partners' id to the partners column
            for index, row in persons.iterrows():
                persons.at[index, 'partners'] = get_partners(index)

            # Loop through each person in the data frame, gets the id of each of their children from the db, writes the childrens' id to the children column
            for index, row in persons.iterrows():
                persons.at[index, 'children'] = get_children(index)

            # build a blank unions table
            unions = pd.DataFrame({'partner' : pd.Series(dtype='object'),
                            'children': pd.Series(dtype='object')})
            
            def getChildrenTogether(person1,person2):
                # get the chidren of each person
                person1offspring = persons.at[person1, 'children']
                person2offspring = persons.at[person2, 'children']

                # make a list of all the children common to both
                offspringtogether = []
                if person1offspring is not None:
                    for kid in person1offspring:
                        if kid in person2offspring:
                                    offspringtogether.append(kid)

                return offspringtogether
            
            def makeUnionRow(person1,person2):
                partnership = [person1, person2]
                childrentogether = getChildrenTogether(person1,person2)
                union_row = {'partner': partnership, 'children': childrentogether}
                return union_row
            
            for index, row in persons.iterrows():
                person1 = index
                boffers = persons.at[person1, 'partners']

                for boffer in boffers:
                    partnership = [person1, boffer]
                    
                    # if the union (in either order) is already in the unions table, do nothing
                    if unions['partner'].apply(lambda x: set(x) == set(partnership)).any():
                        print("nothing")
                    # but if they are not present, proceed to create the union
                    else:
                    
                        new_row = makeUnionRow(person1,boffer)

                        # Add the new union to the DataFrame
                        unions = pd.concat([unions, pd.DataFrame([new_row])])

            # HERE

            persons["own_unions"] = [[] for _ in range(len(persons))]

            # # add all the newly minted unions to each partner's own_unions field
            # loop throough the list of unions
            for index, row in unions.iterrows():
                # loop through all the partners in the partners field
                for item in unions.at[index, 'partner']:
                    # add the union id from the outer look to each partner's record in the persons table
                    persons.at[item, 'own_unions'].append(index)

            
            #build a blank links table
            links = pd.DataFrame({'from': pd.Series(dtype='str'),'to': pd.Series(dtype='str')})

            # and from person to union for each partner
            for index, row in unions.iterrows():
                partnersx = unions.loc[index, 'partner']
                unionx = index
                personx = partnersx[0]
                persony = partnersx[1]
            
                newlinkrow1 = {'from': personx, 'to': unionx}
                newlinkrow2 = {'from': persony, 'to': unionx}
                links.loc[len(links)] = newlinkrow1
                links.loc[len(links)] = newlinkrow2

            for index, row in unions.iterrows():
                childrenx = unions.loc[index, 'children']
                for tidler in childrenx:
                    newchildrenlinkrow = {'from': index, 'to': tidler}
                    links.loc[len(links)] = newchildrenlinkrow
             
            
            persons_json = persons.to_json(orient="index")

            # turn the unions df to json
            unions_json = unions.to_json(orient="index")

            # turn the links df to json
            links_json = links.to_json(orient="values")

            # hard codes the first bit of the tree json
            start = "data = {\"start\":\"1\",\"persons\":"

            bitbetween = ",\"unions\": "

            # hard codes the end bit of the tree json, including unions and links
            links_start = ", \"links\": "

            # tint bit on the end
            ender = "}"

            # combines all of the bits of the tree together
            assembled = start + persons_json + bitbetween + unions_json + links_start + links_json + ender
            
            # writes the json tree to a static file
            with open("static/tree/data/test.js", "w",) as file_Obj:
                file_Obj.write(assembled)

            return assembled
            
    except Exception as e:
        # Handle exceptions and render an error message in the template
        return e

@app.route('/panda')
def woowoo():
    return render_template('run.html', header="Tree from db", payload=pandatest())

def generator3(file_name):
    
    file_path = "static/input/"

    file_path_and_name = file_path + str(file_name)
    
    uf = pd.read_csv(file_path_and_name)

    # Build the persons dataframe with data from uf
    persons = pd.DataFrame({
        'id': uf['id'].apply(lambda x: x.strip() if isinstance(x, str) else x),  # Remove spaces from 'id'
        'name': uf['name'],  
        'own_unions': [[] for _ in range(len(uf))],  # Initialize as empty lists for each row
        'birthyear': uf['birthyear'],
        'birthplace': uf['birthplace'],
        'partners': uf['partners'].apply(lambda z: [p.strip() for p in z.split(',')] if pd.notna(z) else []),  # Strip each partner
        'children': uf['children'].apply(lambda x: [c.strip() for c in x.split(',')] if pd.notna(x) else [])  # Strip each child
    })
    
    #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partner' : pd.Series(dtype='object'),
                    'children': pd.Series(dtype='object')})
    
    #build a blank links table
    links = pd.DataFrame({'from': pd.Series(dtype='str'),
                    'to': pd.Series(dtype='str')})

    
    # for every row in persons
    for index, row in persons.iterrows():
        
        # get the list of partners
        boffers = persons.at[index, 'partners']
        # loop through the list
        for boffer in boffers:

            # state the union
            partnership = [persons.loc[index, 'id'], boffer]

            # if the union (in either order) is already in the unions table, do nothing
            if unions['partner'].apply(lambda x: set(x) == set(partnership)).any():
                print("nothing")
            # but if they are not present, proceed to create the union
            else:
                
                # first set the union id
                # if there are no unions yet, set the NEWunionID to u1
                if unions.empty:
                    NEWunionID = "u1" 
                # else get the last union number and give this union the next number on
                else:
                    OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])
                    NEWunionID = "u" + str(int(OLDunionID[1]) + 1)
                    
                # write the new union id to the person that the current iteration is on
                persons.at[index, 'own_unions'].append(NEWunionID)
                
                # append the union id to the partner's row in the persons table
                # Find the rows where 'id' matches boffer
                matching_rows = persons.loc[persons['id'] == boffer]

                # Check if there are any matching rows
                if not matching_rows.empty:
                    # Get the index of the first matching row
                    boffer_index = matching_rows.index[0]

                    # Ensure 'own_unions' is a list before appending
                    if persons.at[boffer_index, 'own_unions'] is None:
                        persons.at[boffer_index, 'own_unions'] = []  # Initialize as empty list if None
                    
                    # Append the new union ID
                    persons.at[boffer_index, 'own_unions'].append(NEWunionID)
                else:
                    print(f"No matching row found for ID: {boffer}")

                # store the partners in a list to be stored in the unions df
                partnershipAsList = [persons.loc[index, 'id'], boffer]
                
                # get the chidren of each person
                person1offspring = persons.at[index, 'children']
                person2offspring = persons.at[boffer_index, 'children']
                
                # make a list of all the children common to both
                offspringtogether = []
                if person1offspring is not None:
                    for kid in person1offspring:
                        if kid in person2offspring:
                            offspringtogether.append(kid)

                # Create the union row with dynamically included children
                union_row = {'id': NEWunionID, 'partner': partnershipAsList, 'children': offspringtogether}

                # Append the new union to the DataFrame
                unions = pd.concat([unions, pd.DataFrame([union_row])], ignore_index=True)

    # Sets the index of the unions table to be the custom id but preserves the custom id as it's own field by copying it
    unions['id_copy'] = unions['id']
    unions.set_index('id', inplace=True,)
    unions = unions.rename(columns={'id_copy': 'id'})
    unions = unions.reindex(columns=['id', 'partner', 'children'])

    # Links bit
    # for each row in the unions df
    for index, row in unions.iterrows():
        
        # grab the unionID
        unionID = unions.loc[index, 'id']
       
       # grab both partners
        partners = unions.loc[index, 'partner']
        
        # make a temp variable that mimics a row of the links df and store the first partner agains the union ID
        row1 = {'from': partners[0], 'to': unionID}
        
        # Do the same for the second partner
        row2 = {'from': partners[1], 'to': unionID}
        
        # Append the two new rows to the links table
        links.loc[len(links)] = row1
        links.loc[len(links)] = row2

        # grab the list of children from the union and put it in an array
        kidstemp = unions.loc[index, 'children']
        # loop through the cildren in the array...
        for item in kidstemp:
            # create a new array that mimics a row in the links table, using the unionID as the from and the child's ID as the to
            rowk = {'from': unionID, 'to': item}
            # append that mimic row to the links df
            links.loc[len(links)] = rowk

    # Store the ID of the first person in the persons table so that it can be used as the starting point in the json file
    start_id = persons.iloc[0]['id']
    
    # Sets the index of the persons table to be the custom id 
    persons.set_index('id', inplace=True)

    # turns the dataframe into the persons fragment of the tree json
    persons_json = persons.to_json(orient="index")

    # turn the unions df to json
    unions_json = unions.to_json(orient="index")

    # turn the links df to json
    links_json = links.to_json(orient="values")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\""

    bitafterstartid = "\",\"persons\":"

    bitbetween = ",\"unions\": "

    # hard codes the end bit of the tree json, including unions and links
    links_start = ", \"links\": "

     # tint bit on the end
    end = "}"

    # combines all of the bits of the tree together
    assembled = start + start_id + bitafterstartid + persons_json + bitbetween + unions_json + links_start + links_json + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "w",) as file_Obj:
        file_Obj.write(assembled)

    return links

expected_json_x = '''data = {"start":"SS1963","persons":{"SS1963":{"name":"Scott Summers","own_unions":["u1","u2","u3"],"birthyear":1963,"birthplace":"Anchorage, Alaska","partners":["MP1983","JG1963","EF1980"],"children":["NCCS1986","RS2009","NG1995","RS1980"]},"MP1983":{"name":"Madelyne Pryor","own_unions":["u1"],"birthyear":1983,"birthplace":"Unknown","partners":["SS1963"],"children":["NCCS1986"]},"NCCS1986":{"name":"Nathan Christopher Charles Summers","own_unions":[],"birthyear":1986,"birthplace":"Unknown","partners":[],"children":[]},"JG1963":{"name":"Jean Grey","own_unions":["u2"],"birthyear":1963,"birthplace":"Annandale-on-Hudson, New York","partners":["SS1963"],"children":["NG1995","RS1980"]},"EF1980":{"name":"Emma Frost","own_unions":["u3"],"birthyear":1980,"birthplace":null,"partners":["SS1963"],"children":["RS2009"]},"RS2009":{"name":"Ruby Summers","own_unions":[],"birthyear":2009,"birthplace":null,"partners":[],"children":[]},"NG1995":{"name":"Nate Grey","own_unions":[],"birthyear":1995,"birthplace":null,"partners":[],"children":[]},"RS1980":{"name":"Rachel Summers","own_unions":[],"birthyear":1980,"birthplace":null,"partners":[],"children":[]}},"unions": {"u1":{"id":"u1","partner":["SS1963","MP1983"],"children":["NCCS1986"]},"u2":{"id":"u2","partner":["SS1963","JG1963"],"children":["NG1995","RS1980"]},"u3":{"id":"u3","partner":["SS1963","EF1980"],"children":["RS2009"]}}, "links": [["SS1963","u1"],["MP1983","u1"],["u1","NCCS1986"],["SS1963","u2"],["JG1963","u2"],["u2","NG1995"],["u2","RS1980"],["SS1963","u3"],["EF1980","u3"],["u3","RS2009"]]}'''

def test_generator3():
    assert generator3("x.csv") == expected_json_x

if __name__ == '__main__':
    app.run(debug=True)