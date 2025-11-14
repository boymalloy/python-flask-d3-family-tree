from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from app import db
import pandas as pd
# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# Create a new family tree by adding it to the tree table and return the id of the new tree
def write_tree(new_tree_name):
    try:
        # Insert a new tree record using the desired name from the form submission
        sql = text("INSERT INTO tree (name) VALUES (:name)")
        db.session.execute(sql, {'name': new_tree_name})
        db.session.commit()

        # Look up the record that has just been created ...
        sql2 = text("SELECT id FROM tree WHERE name = :name LIMIT 1")
            
        # ... by selecting the id of the tree with that name and return the id
        return db.session.execute(sql2, {'name': new_tree_name}).scalar()
    
    # If the sql insert returns an integrity error (meaning a tree with the desired name already exists), return a string "duplicate"
    except IntegrityError as e:
        return "duplicate"
        
# Function to add a person to the person table
def write_person(tree_id, name, birth_date, birth_place, death_date):
    try:
        sql = text("""
            INSERT INTO person (name, tree_id, birth_date, birth_place, death_date)
            VALUES (:name, :tree_id, :birth_date, :birth_place, :death_date)
            RETURNING id
        """)
        result = db.session.execute(sql, {
            "name": name,
            "tree_id": tree_id,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "death_date": death_date
        })
        new_id = result.scalar()
        db.session.commit()
        return new_id
    except IntegrityError:
        db.session.rollback()
        return "duplicate"
    except Exception:
        db.session.rollback()
        raise

def set_relationship(subject,other_person,type):
    try:
        sql = text("""
            INSERT INTO relationships (person1_id, person2_id, relationship)
            VALUES (:p1, :p2, :rel)
            RETURNING relationship_id
        """)
        result = db.session.execute(sql, {
            "p1": subject,
                "p2": other_person,
                "rel": type
        })
        new_id = result.scalar()
        db.session.commit()
        return new_id

    except IntegrityError:
        db.session.rollback()
        return "duplicate"
    
    except Exception:
        db.session.rollback()
        raise