from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from app import db
import pandas as pd

ALLOWED_EXTENSIONS = {"csv"}

# function to find the file extension of a file, and return True if its in the list of allowed extensions
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# checks to see if a tree of a given name exists in the tree table
def tree_name_db_check(tree_name):
    sql = text("SELECT 1 FROM tree WHERE name = :name LIMIT 1")
    
    # execute the query, use scalar to return the first col of the first row (the tree id). "is not None" turns a number into True and a None (name not found) into False
    return db.session.execute(sql, {'name': tree_name}).scalar() is not None

 # prepares csvs for import: Makes csvs into dfs and adds tree id to people
def prep_people(p):
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

    # Get the tree id to pass through to the page for reference
    imported_tree_id = people["tree_id"].iloc[-1]
    
    return people, imported_tree_id

def write_people_to_person(prepped_people):
    try:
        # write the people from the prepped_people df to the person table using .to_sql
        prepped_people.to_sql(
            name="person",
            con=db.engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        return True
    except IntegrityError as e:
        # return the error msg for the user
        return "Dupes!"
        
# Takes the names and dobs of each row and replaces them with each person's id from the persons table
def prep_relationships(r):
        
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
    try:
        # write the relationships to the relationships table using .to_sql
        input.to_sql(
            name="relationships",
            con=db.engine,
            if_exists="append",
            index=False,
            method="multi"
        )

        return True
    
    except IntegrityError as e:
        return "Dupes!"


# Fetch the id of a person using their name and birth
def fetch_person_id(name,birth_year, birth_month, birth_day):
    
    # put the 3 parts of the dob together and put it in the correct data type
    from datetime import date
    dob = date(birth_year, birth_month, birth_day)
    
    # query
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
        
    prepped_people, tree_id = prep_people(p)

    people_result = write_people_to_person(prepped_people)

    prepped_relationships = prep_relationships(r)

    relationships_result = write_relationships_df_to_relationships_db(prepped_relationships)

    return_msg = "Tree ID: " + str(tree_id) + ". People added: " + str(people_result) + ". Relationships added: " + str(relationships_result)

    return return_msg, tree_id