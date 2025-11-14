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
            mother = request.form["mother"]
            father = request.form["father"]
            partner1 = request.form["partner1"]
            child1 = request.form["child1"]

            # Assemble the dates
            birth_date = utilities.assemble_date(birth_year, birth_month, birth_day)
            death_date = utilities.assemble_date(death_year, death_month, death_day)

            # Write it all to the person table and return the person id
            result = writers.write_person(received_tree_id, name, birth_date, birth_place, death_date)

            # if an integer is returned...
            if isinstance(result, int):
                
                # If supplied, set the first parent
                if mother:
                    mother_rel_id = set_relationship(mother,result,"parent")
                else:
                    mother_rel_id = None

                # If supplied, set the second parent
                if father:
                    father_rel_id = set_relationship(father,result,"parent")
                else:
                    father_rel_id = None

                # If supplied, set the first union
                if partner1:
                    union1_rel_id = set_relationship(result,partner1,"union")
                else:
                    union1_rel_id = None

                # If supplied, set the first child
                if child1:
                    child1_rel_id = set_relationship(result,child1,"parent")
                else:
                    child1_rel_id = None
                
                selected_tree_name = fetchers.fetch_tree_name(received_tree_id)
                
                return render_template('add_person_process.html', tree_name=selected_tree_name, name=name, result=result, mother=mother, father=father, partner1=partner1, child1=child1, mother_rel_id=mother_rel_id, father_rel_id=father_rel_id, union1_rel_id=union1_rel_id, child1_rel_id=child1_rel_id)
            
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