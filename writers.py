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

def edit_person(person_id, name, birth_date, birth_place, death_date):
    try:
        sql = text("""
            UPDATE person
            SET 
            name = :name,
            birth_date = :birth_date,
            birth_place = :birth_place,
            death_date = :death_date
        WHERE id = :person_id
        RETURNING id, name, birth_date, birth_place, death_date;
        """)
        result = db.session.execute(sql, {
            "person_id": person_id,
            "name": name,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "death_date": death_date,
        })

        db.session.commit()
        row = result.fetchone()
        
        if row:
            return 1
        else:
            return 0

    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Person not found"

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

def remove_relationship(rel_id):
    try:
        sql = text("""
            DELETE FROM relationships WHERE relationship_id = :rel_id RETURNING *;
        """)
        result = db.session.execute(sql, {"rel_id": rel_id})
        deleted_row = result.fetchone()
        db.session.commit()

        if deleted_row is None:
            return "Remove failed. Relationship not found"
        else:
            return "Relationship removed successfully"

    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Relationship not found"
    
def remove_parents(subject):
    try:
        sql = text("""
            DELETE FROM relationships WHERE person2_id = :subject and relationship = :relationship RETURNING *;
        """)
        result = db.session.execute(sql, {"subject": subject, "relationship": "parent"})
        deleted_row = result.fetchone()
        db.session.commit()

        if deleted_row is None:
            return "Remove failed. Relationship not found"
        else:
            return "Relationships removed successfully"

    # return an error message if no entry in the db is found
    except IndexError as e:
        return "Person not found"