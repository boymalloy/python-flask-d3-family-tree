# Family Tree Visualisation

A Python and Flask application for creating, managing and visualising family trees.

The application stores family tree data in PostgreSQL, models relationships between people, and generates the graph structure required by an interactive D3.js family tree visualisation.

## Why I Built This

I originally created this project to learn modern Python web development. Over time it evolved into a larger application and became a way to learn:

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Test-driven development using Pytest
- File upload handling and validation
- Git and GitHub
- AWS deployment

## Architecture

The application is organised into separate modules with distinct responsibilities:

| Module | Responsibility |
|----------|----------|
| `routes.py` | Flask routes and request handling |
| `writers.py` | Database write operations |
| `fetchers.py` | Database read operations |
| `classes.py` | SQLAlchemy model definitions |
| `csv_import.py` | CSV import and transformation |
| `display_tree.py` | Family tree graph generation |
| `utilities.py` | Shared helper functions |

## Data Model

The application stores three core entities:

### Trees

A container for a family tree.

### People

Each person record contains:

- Name
- Date of birth
- Place of birth
- Date of death (optional)

### Relationships

Relationships between people, including:

- Parent relationships
- Partner unions

These relationships are transformed into the graph structure required by the D3 visualisation.

## Testing

The project includes automated tests covering:

- Utility functions
- CSV import processing
- Database reads and writes
- Tree rendering logic
- Relationship handling

## Future Improvements

Potential future enhancements include:

- REST API endpoints
- Docker support
- CI/CD with GitHub Actions
- Authentication and authorisation
- Additional test coverage
- Cloud-native deployment options
- Enhanced visualisation features

## Acknowledgements

I did not create the JavaScript D3 visualisation itself. The visualisation is  [BenPortner's js_family_tree](https://github.com/BenPortner/js_family_tree), which is based on the [collapsible d3 tree example](https://gist.github.com/d3noob/43a860bc0024792f8803bba8ca0d5ecd) by d3noob.

## To install and run
To install and run this project locally, follow these steps:
    
1. Clone the repository:
    ```bash
    git clone https://github.com/boymalloy/python-flask-d3-family-tree.git
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure flask:
    ```bash
    cd python-flask-d3-family-tree
    export FLASK_APP=app
    export FLASK_DEBUG=1
    ```

5. Install PostgreSQL
    ```bash
    sudo apt update
    sudo apt install postgresql
    sudo systemctl start postgresql
    sudo systemctl enable postgresql 
    ```

6. Create the database
   ```bash
    sudo -i -u postgres psql
    CREATE DATABASE family_tree;
    \c family_tree
    ```

7. Create the database tables and populate them with test data
    ```bash
    
    -- create tree table
    CREATE TABLE tree (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );

     -- Add a constraint to the tree table unique names only
    ALTER TABLE tree
    ADD CONSTRAINT unique_name
    UNIQUE (name);

    -- Insert a tree 
    INSERT INTO tree (name) VALUES ('Doe');
    
    -- Create person table 
    CREATE TABLE person (
    id SERIAL PRIMARY KEY, 
    name VARCHAR(100) NOT NULL, 
    birth_date DATE NOT NULL, 
    birth_place VARCHAR(255),
    death_date DATE,
    tree_id INT,
    FOREIGN KEY (tree_id) REFERENCES tree(id) ON DELETE CASCADE);

    -- Insert people
    INSERT INTO person (name, birth_date, birth_place, death_date, tree_id)
    VALUES 
    ('John Doe', '1980-05-15', 'New York', NULL, 1),
    ('Jane Smith', '1982-08-20', 'Los Angeles', NULL, 1),
    ('Child One', '2010-01-10', 'San Francisco', NULL, 1), 
    ('Child Two', '2012-03-15', 'San Francisco', NULL, 1), 
    ('Child Three', '2014-06-25', 'San Francisco', NULL, 1);
        
    -- Add a constraint to the person table - only unique combos of name and birth_date allowed
    ALTER TABLE person
    ADD CONSTRAINT unique_person_per_tree
    UNIQUE (name, birth_date, tree_id);

    -- Create a relationship type with several possible answers
    CREATE TYPE relationship_type AS ENUM ('parent', 'child', 'union');

    --- Create relationships table
    CREATE TABLE relationships (
    relationship_id SERIAL PRIMARY KEY,
    person1_id INT NOT NULL, 
    person2_id INT NOT NULL,
    relationship relationship_type NOT NULL,
    FOREIGN KEY (person1_id) REFERENCES Person(id) ON DELETE CASCADE,
    FOREIGN KEY (person2_id) REFERENCES Person(id) ON DELETE CASCADE);

    -- Make relationships unique
    CREATE UNIQUE INDEX unique_pair_relationship
    ON relationships (
    LEAST(person1_id, person2_id),
    GREATEST(person1_id, person2_id),
    relationship
    );

    -- Insert the relationships
    INSERT INTO relationships (person1_id, person2_id, relationship)
    VALUES 
    (1, 2, 'union'),
    (1, 3, 'parent'),
    (1, 4, 'parent'),
    (1, 5, 'parent'),
    (2, 3, 'parent'),
    (2, 4, 'parent'),
    (2, 5, 'parent');

    ```

8. Put your app setup and database url into a flaskenv file so that you don't have to type it every time you go into the virtual env and run flask:
Create a file called .flaskenv in your project directory and add these lines
    ```bash
    export FLASK_APP=app
    export FLASK_DEBUG=1
    export DATABASE_URL="postgresql://postgres:change_to_a_password@localhost:5432/family_tree"
    ```
9. Exclude your venv files from GitHub (so that you don't commit your password to the repo)
Create a file called .gitignore in your project directory and add these lines
    ```bash
    .flaskenv
    .venv/
    ```

10. Start the web server:
    ```bash
    flask run
    ```

11. Go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
