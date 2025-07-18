# hello
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import pandas as pd
import os
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


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

# Route: Tree from db
@app.route('/fetch')
def fetch():
    return render_template('run.html', header="Tree from db", payload=fetch_tree())

# Route: Tree from db
@app.route('/csv')
def csv():
    return render_template('run.html', header="Write to db from csv", payload=import_csv())

# Route: Tree from db
@app.route('/sandbox')
def sandbox_page():
    return render_template('run.html', header="Sandbox", payload=sandbox())

def tree_name_db_check(tree_name):
    with app.app_context():
        sql = text("SELECT 1 FROM tree WHERE name = :name LIMIT 1")
        return db.session.execute(sql, {'name': tree_name}).scalar() is not None

def sandbox():
    return tree_name_db_check("Doe Family Tree")


# get subject's partners from the db
def fetch_partners_from_db(subject):
    with app.app_context():
        # selects the id of people listed as in a relationship or union with a given person
        query = text("""
            SELECT person2_id 
            FROM relationships 
            WHERE person1_id = :subject 
              AND (relationship = 'spouse' OR relationship = 'union')
        """)
        
        # Execute the query as a parameter
        result = db.session.execute(query, {"subject": subject})
        
         # Fetch all rows
        rows = result.fetchall()

        # Convert tuples to a list of integers
        partners = [int(row[0]) for row in rows]

        return partners

# get subject's children from the db
def fetch_children_from_db(subject):
    with app.app_context():
        # selects the id of anyone who has the subject listed as a parent
        query = text("""
            SELECT person2_id FROM relationships WHERE person1_id = :subject AND relationship = 'parent'
        """)
        
        # Execute the query as a parameter
        result = db.session.execute(query, {"subject": subject})
        
        # Fetch all rows
        rows = result.fetchall()

        # Convert tuples to a list of integers
        children = [int(row[0]) for row in rows]

        return children

# finds from the persons dataframe all the children of two people 
def get_children_together_from_df(person1,person2,persons):
    # Check it's not the same person twice
    if person1 == person2:
        return "same person"
    
    # get the chidren of each person
    person1_children = persons.at[person1, 'children']
    person2_children = persons.at[person2, 'children']

    # make a list of all the children common to both
    shared_children = []
    if person1_children is not None:
        for child in person1_children:
            if child in person2_children:
                        shared_children.append(child)

    return shared_children


# checks the union df for a union (two person ids in any order)
def check_for_existing_union_in_df(couple,dataframe):
    for index, row in dataframe.iterrows():
        if set(couple) == set(row['partner']):
            return True
    return False

# adds data to a a row in the unions dataframe - the 2 people in the union and any children
def make_union_row(person1,person2,persons):
    partnership = [person1, person2]
    childrentogether = get_children_together_from_df(person1,person2,persons)
    union_row = {'partner': partnership, 'children': childrentogether}
    return union_row

def tree_name_db_check(tree_name):
    with app.app_context():
        sql = text("SELECT 1 FROM tree WHERE name = :name LIMIT 1")
        return db.session.execute(sql, {'name': tree_name}).scalar() is not None

# Import csv files into the trees
def import_csv():
    try:
        # Turn the people csv into a people dataframe
        people = pd.read_csv("static/input/x_people.csv")

        # start the index of the people dataframe from 1 coz (I think) this is expected later
        people.index = range(1, len(people) + 1)

        # Add a col for the tree id
        people["tree_id"] = None
        
        # Turn the relationships csv into a relationships dataframe
        relationships = pd.read_csv("static/input/x_relationships.csv")

        for index, row in people.iterrows():
            family_tree_name = people.loc[index,'tree_name']

            # if the name of the tree is not already in the db...
            if tree_name_db_check(family_tree_name) == False:
                
                # add the family tree name to the tree table in the db
                sql = text("INSERT INTO tree (name) VALUES (:name)")
                db.session.execute(sql, {'name': family_tree_name})
                db.session.commit()

            # query to select the id of the tree name row
            query = text("""
            SELECT id 
            FROM tree 
            WHERE name = :family_tree_name 
            """)
            
            # Execute the query as a parameter
            result = db.session.execute(query, {"family_tree_name": family_tree_name})

            # put the id into a variable
            family_tree_id = result.scalar()

           # add the family tree id to each person's row in the people df
            people.loc[index,'tree_id'] = family_tree_id
    
        return people
            
            
    # Catch and return any exceptions
    except Exception as e:
        return e 

# fetches the tree data from the db and builds the json file to be read by the D3 family tree app
def fetch_tree():
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
            
            # Convert dates to milliseconds since epoch
            persons["birth_date"] = pd.to_datetime(persons["birth_date"]).astype("int64") // 10**6
            persons["death_date"] = pd.to_datetime(persons["death_date"]).astype("int64") // 10**6
            
            # Add empty columns for partners, children and own unions
            persons["partners"] = None
            persons["children"] = None
            persons["own_unions"] = [[] for _ in range(len(persons))]

            # start the index of the df from 1 to match the ids in the db
            persons.index = range(1, len(persons) + 1)

            # Loop through each person in the data frame, gets the id of each of their partners from the db and wrrite the partners' id to the partners column
            for index, row in persons.iterrows():
                persons.at[index, 'partners'] = fetch_partners_from_db(index)

            # Loop through each person in the data frame, gets the id of each of their children from the db, writes the childrens' id to the children column
            for index, row in persons.iterrows():
                persons.at[index, 'children'] = fetch_children_from_db(index)

            # build a blank unions table
            unions = pd.DataFrame({'partner' : pd.Series(dtype='object'),
                            'children': pd.Series(dtype='object')})
            
            
            # loop through the people in the persons dataframe and get list of each one's partners
            for index, row in persons.iterrows():
                person1 = index
                partner_ids = persons.at[person1, 'partners']

                # create a parnership of ids for each instance of the person and one of their partners
                for partner_id in partner_ids:
                    partnership = [person1, partner_id]

                    # check whether the partnership (listed in either order) is already in the unions dataframe
                    if check_for_existing_union_in_df(partnership,unions) == False:
                        
                        # make a temporary dictionary to hold this union's data
                        new_row = make_union_row(person1,partner_id,persons)

                        # Add the new union to the DataFrame
                        unions = pd.concat([unions, pd.DataFrame([new_row])])
                        

            # add all the newly minted unions to each partner's own_unions field
            # loop through the list of unions
            for index, row in unions.iterrows():
                # loop through all the partners in the partners field
                for item in unions.at[index, 'partner']:
                    # add the union id from the outer look to each partner's record in the persons table
                    persons.at[item, 'own_unions'].append(index)

            
            #build a blank links dataframe
            links = pd.DataFrame({'from': pd.Series(dtype='str'),'to': pd.Series(dtype='str')})

            # add the person to the union for each partner
            for index, row in unions.iterrows():
                partnersx = unions.loc[index, 'partner']
                unionx = index
                personx = partnersx[0]
                persony = partnersx[1]
            
                link_row_1 = {'from': personx, 'to': unionx}
                link_row_2 = {'from': persony, 'to': unionx}
                links.loc[len(links)] = link_row_1
                links.loc[len(links)] = link_row_2

            for index, row in unions.iterrows():
                childrenx = unions.loc[index, 'children']
                for child in childrenx:
                    link_row_children = {'from': index, 'to': child}
                    links.loc[len(links)] = link_row_children
             

            # Convert DataFrames to native Python dicts and list
            persons_dict = persons.to_dict(orient="index")
            unions_dict = unions.to_dict(orient="index")
            links_list = links.values.tolist()  # gives you [[1, 0], [2, 0], ...]

            # assemble it into one dict
            assembled = {
                "start": "1",
                "persons": persons_dict,
                "unions": unions_dict,
                "links": links_list
            }

            # Turn the dict into a json string
            json_string = "data = " + json.dumps(assembled, indent=2, separators=(",", ":"))

            # Write the json string to a file for d3 to read
            with open("static/tree/data/tree_data.js", "w") as file_Obj:
                file_Obj.write(json_string)

            return "Tree fetched successfully"
            
    # Catch and return any exceptions
    except Exception as e:
        return e

# if the script is executed directly, run the app
if __name__ == '__main__':
    app.run(debug=True)