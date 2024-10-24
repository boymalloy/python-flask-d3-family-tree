# Family tree visualisation

This is a simple python app which takes a csv of family tree data and turns it into a D3 data visualisation 

I built this app to learn:
* Python
* Flask
* Jinja templates
* Git and GitHub

Next I want to learn how to:
* Deploy it to AWS
* Let a user upload a csv (at the moment it only accepts a local csv)
* Learn about the JavaScript for the D3 data visualisation so that I can add some features to is. 

The D3 data visualisation is based on [BenPortner's js_family_tree](https://github.com/BenPortner/js_family_tree)

## Installation
To install and run this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/boymalloy/flask.git
    ```

2. Navigate into the project directory:
    ```bash
    cd flask
    ```

3. Create and activate a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
## To run locally

1. Use these commands:
    ```bash
    export FLASK_APP=app
    export FLASK_ENV=development
    ```
2. Start the web server:
    ```bash
    flask run
    ```
## Display the Summers family tree

The default csv file contains the Summers family tree from X-men comics. To make the app process the csv into a D3/JS family tree, do this...

1. Got to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

2. Click on 'Generate a tree'

3. Click on 'See the tree'

## To make your own family tree

1. Navigate to the input directory: flask/static/input

2. Make a copy of x.csv and give it a name, e.g. mytree.csv

3. In the new file, replace the entries with your own entries. Make sure you:
* Have a unique id for each person. I usually use their initials and year of birth
* include all of the persons partners in the partners column using the partners' unique ids separated by a coomma
* Do the same with the childrens ids in the childrens column
* save the csv in text/csv format

4. Navigate to the templates directory: flask/templates

5. Open treegenerator3.html in a text or code editor

6. Go to row 8 and replace x.csv with mytree.csv and save the file

7. Stop the web server:
* Go to the terminal window
* Use Ctrl+c to stop the server

8. Start the web server again with :
    ```bash
    flask run
    ```

8. Got to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

9. Click on 'Generate a tree'

10. Click on 'See the tree'