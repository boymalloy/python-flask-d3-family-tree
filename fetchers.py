from sqlalchemy.sql import text
from app import app
from app import db

import pandas as pd
# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

def fetch_all_trees():
    with app.app_context():
        query = text("""
            SELECT *
            FROM tree """)
        
        # Execute the query as a parameter
        result = db.session.execute(query)
        
         # Return all rows
        return result.fetchall()

def fetch_all_people():
    with app.app_context():
        select = text("""
            SELECT *
            FROM person """)
        
        # Execute the query as a parameter
        output = db.session.execute(select)
        
         # Return all rows
        return output.fetchall()
    
def fetch_person(person_id):
    try:
        with app.app_context():
            query = text("""
                SELECT *
                FROM person WHERE id = :id """)
            
            # Execute the query as a parameter
            result = db.session.execute(query, {"id": person_id})
            
            # Make the results specific to one row
            rows = result.fetchall()
            row = rows[0]
            return row
    
    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Person not found"

def fetch_person_details_df(person_id):
    try:
        with app.app_context():
            query = text("""
                SELECT *
                FROM person WHERE id = :id """)
            
            # Execute the query as a parameter
            result = db.session.execute(query, {"id": person_id})
            
            # Fetch all rows and get column names
            rows = result.fetchall()
            
            # Get the column names from the result object
            col_names = result.keys()  

            # Return a data frame from the fetched rows and column names
            return pd.DataFrame(rows, columns=col_names)
    
    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Person not found"

# Fetch the name of a tree using the tree id
def fetch_tree_name(tree_id):
    try:
        # Use the app context to access the database session
        with app.app_context():
            
            query = text("SELECT name FROM tree WHERE id = :tree_id")

            # Execute the query as a parameter
            result = db.session.execute(query, {"tree_id": tree_id})
            
            # get the name from the results and return it
            rows = result.fetchall()
            row = rows[0]
            return row[0]
    
    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Tree not found"
    
def fetch_relationships_df(person_id):
    # Use the app context to access the database session
    with app.app_context():
        
        query = text("SELECT * FROM relationships WHERE person1_id = :person_id OR person2_id = :person_id")

        # Execute the query as a parameter
        result = db.session.execute(query, {"person_id": person_id})
        
        # Fetch all rows and get column names
        rows = result.fetchall()

        # Return an error msg if no relationships are found for the person
        if not rows:
            return "No relationships found"
        
        # Get the column names from the result object
        col_names = result.keys()  

        # Return a data frame from the fetched rows and column names
        return pd.DataFrame(rows, columns=col_names)

def fetch_partners(subject):
    
    # Make sure subject is an int
    subject = int(subject)

    # Make a df of the person's relatioships
    relationships = fetch_relationships_df(subject)

    if isinstance(relationships, pd.DataFrame):

        # Make an empty partners list
        partners = []
                
        # loop through the df of the person's relationships
        for index, row in relationships.iterrows():
            # If the relationship is a union
            if row["relationship"]== "union":

                # if the subject is person 1
                if row["person1_id"] == subject:
                    
                    # fetch person2's details from the person table
                    partner_details = fetch_person_details_df(row["person2_id"])
                
                    # put the pertinent info into a dict
                    new_row = {'relationship_id': row["relationship_id"], 'partner_id': partner_details.loc[0, "id"], 'partner_name': partner_details.loc[0, "name"]}

                    # add the dict to the partners df
                    partners.append(new_row)
    
                # if the subject is partner 2
                if subject == row["person2_id"]:
                    
                    # fetch partner1's details from the person table
                    partner_details = fetch_person_details_df(row["person1_id"])
                
                    # put the pertinent info into a dict
                    new_row = {'relationship_id': row["relationship_id"], 'partner_id': partner_details.loc[0, "id"], 'partner_name': partner_details.loc[0, "name"]}

                    # add the dict to the partners df
                    partners.append(new_row)
        
        return partners
    
    if relationships == "No relationships found":
        return "No partners found"
    
def fetch_children(subject):
    
    # Make sure subject is an int
    subject = int(subject)

    # Make a df of the person's relatioships
    relationships = fetch_relationships_df(subject)

    if isinstance(relationships, pd.DataFrame):

        # Make an empty children list
        children = []
                
        # loop through the df of the person's relationships
        for index, row in relationships.iterrows():
            # If the relationship is a union
            if row["relationship"]== "parent":

                # if the subject is person 1
                if row["person1_id"] == subject:
                    
                    # fetch person 2's details from the person table
                    child_details = fetch_person_details_df(row["person2_id"])
                
                    # put the pertinent info into a dict
                    new_row = {'relationship_id': row["relationship_id"], 'child_id': child_details.loc[0, "id"], 'child_name': child_details.loc[0, "name"]}

                    # add the dict to the children df
                    children.append(new_row)
        
        return children
    
    if relationships == "No relationships found":
        return "No children found"
    
def fetch_parents(subject):
    
    # Make sure subject is an int
    subject = int(subject)

    # Make a df of the person's relatioships
    relationships = fetch_relationships_df(subject)

    if isinstance(relationships, pd.DataFrame):

        # Make an empty children list
        parents = []
                
        # loop through the df of the person's relationships
        for index, row in relationships.iterrows():
            # If the relationship is a union
            if row["relationship"]== "parent":

                # if the subject is person 2
                if row["person2_id"] == subject:
                    
                    # fetch person 1's details from the person table
                    parent_details = fetch_person_details_df(row["person1_id"])
                
                    # put the pertinent info into a dict
                    new_row = {'relationship_id': row["relationship_id"], 'parent_id': parent_details.loc[0, "id"], 'parent_name': parent_details.loc[0, "name"]}

                    # add the dict to the children df
                    parents.append(new_row)
        
        if parents == []:
            parents = "No parents set"
        return parents
    
    if relationships == "No relationships found":
        return "No parents found"
    
