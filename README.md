# Family tree visualisation

This is a simple python app which reads family tree data from a PostgreSQL database and converts it to the correct format for a D3 data visualisation 

I built this app to learn:
* Python
* Flask
* Jinja templates
* Git and GitHub
* PostgreSQL

Next I plan to:
* Write new data to the database from a csv or a form
* Try doing it in an object oriented way (it's currently done using panda dataframes)
* Deploy it somewhere
* Learn about the JavaScript for the D3 data visualisation so that I can add some features to it 

I didn't make the JavaScript data visualisation. It is taken (with thanks and gratitude) from [BenPortner's js_family_tree](https://github.com/BenPortner/js_family_tree), which in turn is based on [collapsible d3 tree example](https://gist.github.com/d3noob/43a860bc0024792f8803bba8ca0d5ecd) by d3noob.

## To install and run
To install and run this project locally, follow these steps:
    
1. Clone the repository:
    ```bash
    git clone https://github.com/boymalloy/python-flask-d3-family-tree.git
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure flask:
    ```bash
    cd python-flask-d3-family-tree
    export FLASK_APP=app
    export FLASK_ENV=development
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
    CREATE TABLE person (
    id SERIAL PRIMARY KEY, 
    name VARCHAR(100) NOT NULL, 
    birth_date DATE NOT NULL, 
    birth_place VARCHAR(255),
    death_date DATE);

    INSERT INTO person (name, birth_date, birth_place, death_date)
    VALUES 
    ('John Doe', '1980-05-15', 'New York', NULL),
    ('Jane Smith', '1982-08-20', 'Los Angeles', NULL),
    ('Child One', '2010-01-10', 'San Francisco', NULL), 
    ('Child Two', '2012-03-15', 'San Francisco', NULL), 
    ('Child Three', '2014-06-25', 'San Francisco', NULL);
        
    CREATE TYPE relationship_type AS ENUM ('parent', 'child', 'spouse', 'union');

    CREATE TABLE Relationships (
        relationship_id SERIAL PRIMARY KEY,
        person1_id INT NOT NULL, 
        person2_id INT NOT NULL,
        relationship relationship_type NOT NULL,
        FOREIGN KEY (person1_id) REFERENCES Person(id) ON DELETE CASCADE,
        FOREIGN KEY (person2_id) REFERENCES Person(id) ON DELETE CASCADE);

    -- the union
    INSERT INTO relationships (person1_id, person2_id, relationship)
    VALUES 
    (1, 2, 'union');

    -- Parent-child relationships for John Doe
    INSERT INTO relationships (person1_id, person2_id, relationship)
    VALUES 
    (1, 3, 'parent'),
    (1, 4, 'parent'),
    (1, 5, 'parent');

    -- Parent-child relationships for Jane Smith
    INSERT INTO relationships (person1_id, person2_id, relationship)
    VALUES 
    (2, 3, 'parent'),
    (2, 4, 'parent'),
    (2, 5, 'parent'),
    (2, 5, 'parent');

    -- tree table
    CREATE TABLE tree (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );

    -- Insert a default tree 
    INSERT INTO tree (name) VALUES ('Doe Family Tree');

    -- Add tree_id to the person table
    ALTER TABLE person
    ADD COLUMN tree_id INT REFERENCES tree(id) ON DELETE CASCADE;

    -- Assign existing people to the default tree (id = 1)
    UPDATE person SET tree_id = 1;

    ```

8. Change the database password and set the environment variable
    ```bash
        ALTER USER postgres PASSWORD 'change_to_a_password';
    \q
    export DATABASE_URL="postgresql://postgres:change_to_a_password@localhost:5432/family_tree"
    source ~/.bashrc
    ```

9. Start the web server:
    ```bash
    flask run
    ```

10. Got to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

11. Click on 'Fetch tree from database'.

12. Click on 'See the tree'.
