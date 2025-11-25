from app import app
from flask import render_template, request, redirect, url_for, session
import fetchers
import display_tree
import writers
import utilities
import csv_import
from werkzeug.utils import secure_filename
import uuid
from pathlib import Path
BASE_DIR = Path(app.root_path)
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 

import pandas as pd
# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# Route: Home page
@app.route('/')
def index():
    return render_template('index.html')

# Route: Fetch tree from db
@app.route('/fetch')
def fetch():
    # Pick up the tree_id from the query string
    tree_id = request.args.get('tree_id')

    # if there is no tree_id, redirect to the choose a tree page
    if not tree_id:
        return redirect(url_for("trees_page"))
    else:
        # else if there is a tree_id, fetch that tree
        return render_template('run.html', header="Tree from db", payload=display_tree.fetch_tree(tree_id))

# Page to create a tree
@app.route("/make_tree", methods=["GET", "POST"])
def make_tree_page():
    # if the page is called with the POST method (the form has been submitted)
    if request.method == "POST":
        # Get the desired tree name from the form
        desired_tree_name = request.form["desired_tree_name"]
        
        # Write a new tree to the tree table using the desired name
        new_tree_id = writers.write_tree(desired_tree_name)

        # if the write_tree function returns "duplicate, render the error page with an explanation"
        if new_tree_id == "duplicate":
            return render_template("make_tree_error.html", error="Tree already exists")
        else:
            # otherwise proceed
            return render_template("make_tree_process.html", desired_tree_name=desired_tree_name, new_tree_id=new_tree_id)
    # if the page is called without the POST method (the form hasn't been submitted), show the form
    return render_template("make_tree.html")
    
# Page to add a person
@app.route("/add_person", methods=["GET", "POST"])
def add_person_page():
    
    # If the form has been submitted
    if request.method == "POST":
            # Pick up all the variables from the form
            received_tree_id = request.form["tree_id"]
            name = request.form["name"]
            birth_year = request.form["birth_year"]
            birth_month = request.form["birth_month"]
            birth_day = request.form["birth_day"]
            birth_place = request.form["birth_place"]
            death_year = request.form["death_year"]
            death_month = request.form["death_month"]
            death_day = request.form["death_day"]
            parent1 = request.form["parent1"]
            parent2 = request.form["parent2"]
            partner1 = request.form["partner1"]
            child1 = request.form["child1"]

            # Assemble the dates
            birth_date = utilities.assemble_date(birth_year, birth_month, birth_day)
            death_date = utilities.assemble_date(death_year, death_month, death_day)

            # Write it all to the person table and return the person id
            result = writers.write_person(received_tree_id, name, birth_date, birth_place, death_date)

            # if an integer is returned...
            if isinstance(result, int):
                
                # If parent1 was supplied, set the relationship id
                if parent1:
                    parent1_rel_id = writers.set_relationship(parent1,result,"parent")
                else:
                    parent1_rel_id = None

                # If If parent2 was supplied, set the relationship id
                if parent2:
                    parent2_rel_id = writers.set_relationship(parent2,result,"parent")
                else:
                    parent2_rel_id = None

                # If supplied, set the first union
                if partner1:
                    union1_rel_id = writers.set_relationship(result,partner1,"union")
                else:
                    union1_rel_id = None

                # If supplied, set the first child
                if child1:
                    child1_rel_id = writers.set_relationship(result,child1,"parent")
                else:
                    child1_rel_id = None
                
                selected_tree_name = fetchers.fetch_tree_name(received_tree_id)
                
                return render_template('add_person_process.html', tree_name=selected_tree_name, name=name, result=result, parent1=parent1, parent2=parent2, partner1=partner1, child1=child1, parent1_rel_id=parent1_rel_id, parent2_rel_id=parent2_rel_id, union1_rel_id=union1_rel_id, child1_rel_id=child1_rel_id)
            
            # if, instead of an integer we get the duplicate msg, display that
            if result == "duplicate":
                return render_template('generic.html', header="Processing Result", payload="Person not added. A person with the same name and date of birth is already in the database.")
    
    # But if the form hasn't been submitted yet...

    # Pick up the tree_id from the query string
    tree_id = request.args.get('tree_id')

    # if there is no tree_id...
    if not tree_id:
        # Redirect to choose a tree
        return render_template('add_person_tree_selector.html', trees=fetchers.fetch_all_trees())
    # else a tree id has been provided so show the add person form
    else:
        # Get the name of the tree
        tree_name = fetchers.fetch_tree_name(tree_id)
        
        # Return the form
        return render_template('add_person_form.html', tree_id=tree_id, tree_name=tree_name, people=fetchers.fetch_all_people())
    
# Page to add a person
@app.route("/edit_person", methods=["GET", "POST"])
def edit_person_page():
    
    # If the form has been submitted
    if request.method == "POST":
            
        # Pick up all the variables from the form
        name = request.form["name"]
        person_id = request.form["person_id"]
        birth_year = request.form["birth_year"]
        birth_month = request.form["birth_month"]
        birth_day = request.form["birth_day"]
        birth_place = request.form["birth_place"]
        death_year = request.form["death_year"]
        death_month = request.form["death_month"]
        death_day = request.form["death_day"]
        form_parent1 = request.form["parent1"]
        form_parent2 = request.form["parent2"]

        # Assemble the dates
        birth_date = utilities.assemble_date(birth_year, birth_month, birth_day)
        death_date = utilities.assemble_date(death_year, death_month, death_day)

        # update the person's entry in the person table using the onfo submitted through the form
        result = writers.edit_person(person_id, name, birth_date, birth_place, death_date)

        if result == 0:
            msg = "Failed to update"
        if result == 1:
            msg = "Details updated."

            # delete all of the subject's parents regardless of what's in the form
            parent_deletion = writers.remove_parents(person_id)

            # if the parent form fields were not blank, write the parents to the relationship table
            if form_parent1 != "blank":
                parent1_write_result = writers.set_relationship(form_parent1,person_id,"parent")
            else:
                parent1_write_result = "No parent provided"

            if form_parent2 != "blank":
                parent2_write_result = writers.set_relationship(form_parent2,person_id,"parent")
            else:
                parent2_write_result = "No parent provided"

        return render_template('edit_person_result.html', header="Edit a person", payload=msg, parent_deletion=parent_deletion, form_parent1=form_parent1, form_parent2=form_parent2, parent1_write_result=parent1_write_result, parent2_write_result=parent2_write_result, return_id=person_id)

    # From here on, the form hasn't been submitted...      
    # Pick up the person_id from the query string
    person_id = request.args.get('person_id')
    
    # if there is no person_id...
    if not person_id:
        # Redirect to choose a person
        return render_template('edit_person_selector.html', people=fetchers.fetch_all_people())
    
    person = fetchers.fetch_person(person_id)

    relationships = fetchers.fetch_relationships_df(person_id)

    partners = fetchers.fetch_partners(person_id)

    children = fetchers.fetch_children(person_id)

    parents = fetchers.fetch_parents(person_id)

    birth_date = utilities.disassemble_date(person.birth_date)

    death_date = utilities.disassemble_date(person.death_date)

    return render_template('edit_person_form.html', people=fetchers.fetch_all_people(), person=person, birth_date=birth_date, death_date=death_date, relationships=relationships, partners=partners, children=children, parents=parents)

# Remove relationship page
@app.route("/remove_relationship")
def remove_relationship_page():

    # Pick up the person_id from the query string
    rel_id = request.args.get('rel_id')
    return_id = request.args.get('return_id')

    return render_template('remove_relationship.html', operation=writers.remove_relationship(rel_id), return_id=return_id)

@app.route('/sandbox')
def sandbox():

    output = writers.remove_parents(22)

    return render_template('sandbox.html', header="Sandbox", payload=output)
    
# Route: List of family trees
@app.route('/trees')
def trees_page():
    return render_template('trees.html', header="Choose a tree", trees=fetchers.fetch_all_trees())

# Route: CSV upload page
@app.route("/upload", methods=["GET"])
def upload_form():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def handle_upload():
    # Accept the two csvs
    f1 = request.files.get("csv1")
    f2 = request.files.get("csv2")

    # make empty strings if the csvs aren't there
    if not f1 or not f2 or f1.filename == "" or f2.filename == "":
        abort(400, "Please choose both CSV files.")

    
    # If either of the files are not a csv, abort and give msg to user
    if not (csv_import.allowed_file(f1.filename) and csv_import.allowed_file(f2.filename)):
        abort(400, "Only .csv files are allowed.")

    # Function to add unique characters to the file name and return just the name  
    def save_file(f):
        original = secure_filename(f.filename)
        unique = f"{uuid.uuid4().hex}_{original}"
        dest = UPLOAD_DIR / unique
        f.save(dest)
        return unique  

    # create unique file names and store the names as variables
    name1 = save_file(f1)
    name2 = save_file(f2)

    # Move the variables to the session so they can be retrieved on the processing page
    session["uploaded_csv1"] = name1
    session["uploaded_csv2"] = name2

    # Redirect to the processing page
    return redirect(url_for("process_page"))

# Route: Page to process the csvs
@app.route("/process")
def process_page():
    # Get filenames from session 
    name1 = session.get("uploaded_csv1")
    name2 = session.get("uploaded_csv2")
    # If the session variables arn't there, go back to the form
    if not name1 or not name2:
        return redirect(url_for("upload_form"))

    # Build filesystem paths and public URLs
    path1 = UPLOAD_DIR / name1
    path2 = UPLOAD_DIR / name2
    
    # Abort if not found
    if not path1.exists() or not path2.exists():
        abort(410, "Uploaded files are no longer available.")

    # Store the full urls of the files
    url1 = url_for("static", filename=f"uploads/{name1}")
    url2 = url_for("static", filename=f"uploads/{name2}")

    # run the import function to write the contents of the csvs to the database
    # It outputs a string stating how many row were added to the person and relationships tables
    result, tree_id = csv_import.import_csv(path1, path2)

    # Render the process page and output the result of the import_csv function on the page
    return render_template(
        "process.html",
        result=result,
        tree_id=tree_id
    )