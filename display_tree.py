
from sqlalchemy.sql import text
from app import db
import pandas as pd
# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import fetchers

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

# adds data to a a row in the unions dataframe - the 2 people in the union and any children
def make_union_row(person1,person2,persons):
    partnership = [person1, person2]
    childrentogether = get_children_together_from_df(person1,person2,persons)
    union_row = {'partner': partnership, 'children': childrentogether}
    return union_row

# fetch the id of the first person in the person table who has a given tree id
# this is used as the starting point when rendering the json
def fetch_first_person(given_tree_id):
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

# fetches the tree data from the db and builds the json file to be read by the D3 family tree app
def fetch_tree(tree):
    try:   
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
        persons["death_date"] = pd.to_datetime(persons["death_date"]).astype("int64")

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

        # increase the starting union ID to something higher than the highest person id
        people_check = fetchers.fetch_all_people_in_tree(tree)

        max_person_id = max(row.id for row in people_check)

        unions.index = unions.index + max_person_id + 1

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
        persons["death_date"] = pd.to_datetime(persons["death_date"], unit="ns", utc=True).dt.date
        # And then convert it again into a string for compatibility with json
        persons["birth_date"] = persons["birth_date"].astype(str)
        persons["death_date"] = persons["death_date"].astype(str)
        
        # change the names of the date columns to the names expected by D3
        persons = persons.rename(columns={'birth_date': 'birthyear'})
        persons = persons.rename(columns={'death_date': 'deathyear'})

        # Replace the date with just the year (makes more sense in the D3 tree)
        persons["birthyear"] = persons["birthyear"].str.extract(r"^(\d{4})")

        # Change any deathyears recorded as "NaT" to "Living"
        persons["deathyear"] = persons["deathyear"].replace({"NaT": "Living"})
        
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
        import json
        json_string = "data = " + json.dumps(assembled, indent=2, separators=(",", ":"))

        # Write the json string to a file for d3 to read
        with open("static/tree/data/tree_data.js", "w") as file_Obj:
            file_Obj.write(json_string)

        return "Tree fetched successfully"
            
    # Catch and return any exceptions
    except Exception as e:
        return e
    
# get subject's partners from the db
def fetch_partners_from_db(subject):
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
    # selects the id of anyone who has the subject listed as a parent
    query = text("""
        SELECT DISTINCT person2_id FROM relationships WHERE person1_id = :subject AND relationship = 'parent'
    """)
    
    # Execute the query as a parameter
    result = db.session.execute(query, {"subject": subject})
    
    # Fetch all rowsapp
    rows = result.fetchall()

    # Convert tuples to a list of integers
    children = [int(row[0]) for row in rows]

    return children

