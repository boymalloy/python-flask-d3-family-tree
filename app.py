from flask import Flask, render_template, session, request, redirect, url_for, abort
from flask_bootstrap import Bootstrap
import pandas as pd
import os
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import numpy as np
from sqlalchemy.types import Date, Integer, String
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid

# Create the Flask app and configure it
app = Flask(__name__, static_url_path='/static')
bootstrap = Bootstrap(app)
app.secret_key = "dCQXgn0uryXJIaD6MhREV5XOfzQ7Qu"

# ---- Config ----
BASE_DIR = Path(app.root_path)
UPLOAD_DIR = BASE_DIR / "static" / "uploads"   # put under /static so you can also link to files
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"csv"}
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB per request; tweak as needed

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Route: Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Fetch tree from db
@app.route('/fetch')
def fetch():
    # Pick up the tree_id from the query string
    tree_id = request.args.get('tree_id')

    # if there is no tre_id, redirect to the choose a tree page
    if not tree_id:
        return redirect(url_for("trees_page"))
    else:
        # else if there is a tree_id, fetch that tree
        return render_template('run.html', header="Tree from db", payload=fetch_tree(tree_id))

# Route: Import from CSV
@app.route('/csv')
def csv():
    return render_template('run.html', header="Write to db from csv", payload=import_csv("static/input/grr_people.csv","static/input/grr_relationships.csv"))

# Route: Sandbox
@app.route('/sandbox')
def sandbox_page():
    return render_template('run.html', header="Sandbox", payload=prep_relationships("static/input/grr_relationships.csv"))

# fetch the id of the first person in the person table who has a given tree id
# this is used as the starting point when rendering the json
def fetch_first_person(given_tree_id):
    # query
    with app.app_context():
        try:
            query = text("""
                SELECT id
                FROM person 
                WHERE tree_id = :given
            """)
            
            # Execute the query as a parameter
            result = db.session.execute(query, {"given": given_tree_id})
            
            # get the id from the results and return it
            rows = result.fetchall()
            row = rows[0]
            id = row[0]
            return id
       
       # return an error message if no entry in the db is found
        except IndexError as e:
            return "Person not found"
    return output

def fetch_all_trees():
    with app.app_context():
        query = text("""
            SELECT *
            FROM tree """)
        
        # Execute the query as a parameter
        result = db.session.execute(query)
        
         # Return all rows
        return result.fetchall()

# Route: List of family trees
@app.route('/trees')
def trees_page():
    return render_template('trees.html', header="Choose a tree", trees=fetch_all_trees())


# checks to see if a tree of a given name exists in the tree table
def tree_name_db_check(tree_name):
    with app.app_context():
        sql = text("SELECT 1 FROM tree WHERE name = :name LIMIT 1")
        
        # execute the query, use scalar to return the first col of the first row (the tree id). "is not None" turns a number into True and a None (name not found) into False
        return db.session.execute(sql, {'name': tree_name}).scalar() is not None

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
            SELECT DISTINCT person2_id FROM relationships WHERE person1_id = :subject AND relationship = 'parent'
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

# prepares csvs for import: Makes csvs into dfs and adds tree id to people
def prep_people(p):
    with app.app_context():
        
        # Turn the people csv into a people dataframe
        people = pd.read_csv(p)

        # Add a col for the tree id
        people["tree_id"] = None

        # for each row in the people df...
        for index, row in people.iterrows():
            # get the name of the tree in that row
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

        # Remove the tree_name column
        people = people.drop("tree_name", axis=1)
        
        return people

def write_people_to_person(prepped_people):
    with app.app_context():
        try:
            # write the people from the prepped_people df to the person table using .to_sql
            prepped_people.to_sql(
                name="person",
                con=db.engine,
                if_exists="append",
                index=False,
                method="multi"
            )

            # returns the length of the df
            # TO DO: return something more meaningful, e.g. the number of rows added
            return len(prepped_people)
        except IntegrityError as e:
            app.logger.exception("Insert failed with IntegrityError")

            # - in debug, surface the real cause so tests show it
            if app.debug:
                orig = getattr(e, "orig", e)   # psycopg2 error if present
                return f"IntegrityError[{type(orig).__name__}]: {orig}"

            # - in non-debug, return the error msg for the user
            return "Dupes!"
        
# Takes the names and dobs of each row and replaces them with each person's id from the persons table
def prep_relationships(r):
    with app.app_context():
        
        # Turn the relationships csv into a relationships dataframe
        relationships = pd.read_csv(r)
        
        # make a blank dataframe for the preppared version of the relationships, which will have the names and dobs switched to the ids
        output = pd.DataFrame({'person1_id' : pd.Series(dtype='int'),
                            'person2_id': pd.Series(dtype='int'),
                            'relationship': pd.Series(dtype='string')})
        
        # Loop through the imported relationships df, for each row we get the ids from the person table and write them, along with the relationship (e.g. union, parent) to the prepa new df which is then returned
        for index, row in relationships.iterrows():
                
            # Get person 1's date of birth and break it into it's 3 parts
            p1dob = relationships['person_1_birth'][index]
            p1year, p1month, p1day = map(int, p1dob.split('-'))

            # look up the id of person 1 using their name and birth
            p1id = fetch_person_id(relationships['person_1_name'][index],p1year,p1month,p1day)

            # Get person 2's date of birth and break it into it's 3 parts
            p2dob = relationships['person_2_birth'][index]
            p2year, p2month, p2day = map(int, p2dob.split('-'))

            # look up the id of person 2 using their name and birth
            p2id = fetch_person_id(relationships['person_2_name'][index],p2year,p2month,p2day)

            # get p1 and p2's relationship
            rel = relationships['relationship'][index]

            # write ids and relationship to the output df
            new_row = {'person1_id': p1id, 'person2_id': p2id, 'relationship': rel}
            output = pd.concat([output, pd.DataFrame([new_row])], ignore_index=True)

        return output
    
def write_relationships_df_to_relationships_db(input):
    with app.app_context():
        try:
            # write the relationships to the relationships table using .to_sql
            input.to_sql(
                name="relationships",
                con=db.engine,
                if_exists="append",
                index=False,
                method="multi"
            )

            # returns the length of the df
            # TO DO: return something more meaningful, e.g. the number of rows added
            return len(input)
        except IntegrityError as e:
            app.logger.exception("Insert failed with IntegrityError")

            # - in debug, surface the real cause so tests show it
            if app.debug:
                orig = getattr(e, "orig", e)   # psycopg2 error if present
                return f"IntegrityError[{type(orig).__name__}]: {orig}"

            # - in non-debug, return the error msg for the user
            return "Dupes!"


# Fetch the id of a person using their name and birth
def fetch_person_id(name,birth_year, birth_month, birth_day):
    
    # put the 3 parts of the dob together and put it in the correct data type
    from datetime import date
    dob = date(birth_year, birth_month, birth_day)
    
    # query
    with app.app_context():
        try:
            query = text("""
                SELECT id
                FROM person 
                WHERE name = :name AND birth_date = :dob
            """)
            
            # Execute the query as a parameter
            result = db.session.execute(query, {"name": name, "dob": dob})
            
            # get the id from the results and return it
            rows = result.fetchall()
            row = rows[0]
            id = row[0]
            return id
       
       # return an error message if no entry in the db is found
        except IndexError as e:
            return "Person not found"
    
# import
def import_csv(p,r):
    with app.app_context():
        
        prepped_people = prep_people(p)

        people_result = write_people_to_person(prepped_people)

        prepped_relationships = prep_relationships(r)

        relationships_result = write_relationships_df_to_relationships_db(prepped_relationships)

        return_msg = "People added: " + str(people_result) + ". Relationships added: " + str(relationships_result)

        return return_msg

# fetches the tree data from the db and builds the json file to be read by the D3 family tree app
def fetch_tree(tree):
    try:
        
        # Use the app context to access the database session
        with app.app_context():
            
            query = text("SELECT * FROM person WHERE tree_id = :tree")

            # Execute the query as a parameter
            result = db.session.execute(query, {"tree": tree})

            # Fetch all rows and get column names
            rows = result.fetchall()
            col_names = result.keys()  # Retrieve column names from the result object

            # Make a data frame from the fetched rows and column names
            persons = pd.DataFrame(rows, columns=col_names)

            # make sure id is int and use it as the index
            persons["id"] = persons["id"].astype(int)
            persons.set_index("id", inplace=True) 
            
            # Add empty columns for partners, children and own unions
            persons["partners"] = None
            persons["children"] = None
            persons["own_unions"] = [[] for _ in range(len(persons))]
            
            # Convert dates to epoch ms for pandas compatibility 
            persons["birth_date"] = pd.to_datetime(persons["birth_date"]).astype("int64")

            # Loop through each person in the data frame, gets the id of each of their children from the db, write the childrens' id to the children column
            for index, row in persons.iterrows():
                persons.at[index, 'children'] = fetch_children_from_db(index)
            
            # Loop through the persons df 
            for pid in persons.index:
                
                # Fetch each person's partners and add them to the partners column
                persons.at[pid, "partners"] = fetch_partners_from_db(pid)

            # a temp list for housing the unions
            unions_rows = []
            
            # Loop through persons
            for pid in persons.index:
                
                # when in the loop for a person, loop through each of their partners
                for partner_id in persons.at[pid, "partners"] or []:
                    
                    # build a row for the union
                    new_row = make_union_row(pid, partner_id, persons)
                    
                    # add the union's row to the unions_rows temp list
                    unions_rows.append(new_row)

            # make the temp list into a df
            unions = pd.DataFrame(unions_rows, columns=["partner", "children"])

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

            # Put the id back in
            persons.index = persons.index.astype(int)     # ensure int
            persons["id"] = persons.index

            # move it to the front
            cols = ["id"] + [c for c in persons.columns if c != "id"]
            persons = persons[cols]

            # Convert dates back from epoch ms to date format
            persons["birth_date"] = pd.to_datetime(persons["birth_date"], unit="ns", utc=True).dt.date
            # And then convert it again into a string for compatibility with json
            persons["birth_date"] = persons["birth_date"].astype(str)
            
            # Convert DataFrames to native Python dicts and list
            persons_dict = persons.to_dict(orient="index")
            unions_dict = unions.to_dict(orient="index")
            links_list = links.values.tolist()

            # Select the first person listed in the person table to have the tree id assigned to them and store their id to use as the person from which to start the d3 tree
            start = fetch_first_person(tree)

            # assemble it into one dict
            assembled = {
                "start": start,
                "persons": persons_dict,
                "unions": unions_dict,
                "links": links_list
            }

            # Turn the dict into a json string
            json_string = "data = " + json.dumps(assembled, indent=2, separators=(",", ":"))

            # Write the json string to a file for d3 to read
            with open("static/tree/data/tree_data.js", "w") as file_Obj:
                file_Obj.write(json_string)

            return "It worked"
            
    # Catch and return any exceptions
    except Exception as e:
        return e

# === START 1 ===

@app.route("/upload", methods=["GET"])
def upload_form():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def handle_upload():
    # Expect two file inputs named csv1 and csv2
    f1 = request.files.get("csv1")
    f2 = request.files.get("csv2")

    if not f1 or not f2 or f1.filename == "" or f2.filename == "":
        abort(400, "Please choose both CSV files.")

    if not (allowed_file(f1.filename) and allowed_file(f2.filename)):
        abort(400, "Only .csv files are allowed.")

    # Safe, unique filenames (avoid collisions)
    def save_file(f):
        original = secure_filename(f.filename)
        unique = f"{uuid.uuid4().hex}_{original}"
        dest = UPLOAD_DIR / unique
        f.save(dest)
        return unique  # store just the name in session

    name1 = save_file(f1)
    name2 = save_file(f2)

    # Persist for the next page; you could also pass via query params
    session["uploaded_csv1"] = name1
    session["uploaded_csv2"] = name2

    # Optionally remember permanently for the browser session
    session.permanent = True

    # Redirect to the processing page
    return redirect(url_for("process_page"))

# ---- Your processing function (called on page 2) ----
def process_two_csvs(csv1_path: Path, csv2_path: Path):
    """
    Example: read both CSVs and return something useful.
    Replace this with your real logic.
    """
    df1 = pd.read_csv(csv1_path)
    df2 = pd.read_csv(csv2_path)
    # Example: just return row counts
    return {
        "csv1_rows": len(df1),
        "csv2_rows": len(df2),
    }

@app.route("/process")
def process_page():
    # Grab filenames from session (set by /upload POST)
    name1 = session.get("uploaded_csv1")
    name2 = session.get("uploaded_csv2")
    if not name1 or not name2:
        # nothing in session; send user to upload
        return redirect(url_for("upload_form"))

    # Build filesystem paths and public URLs
    path1 = UPLOAD_DIR / name1
    path2 = UPLOAD_DIR / name2
    if not path1.exists() or not path2.exists():
        abort(410, "Uploaded files are no longer available.")

    url1 = url_for("static", filename=f"uploads/{name1}")
    url2 = url_for("static", filename=f"uploads/{name2}")

    # Call your real processing function using filesystem paths
    result = import_csv(path1, path2)
    # result = 1

    return render_template(
        "process.html",
        file1_url=url1,
        file2_url=url2,
        result=result
    )


# if the script is executed directly, run the app
if __name__ == '__main__':
    app.run(debug=True)