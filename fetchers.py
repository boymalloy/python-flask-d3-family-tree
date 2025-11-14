from sqlalchemy.sql import text
from app import app
from app import db

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