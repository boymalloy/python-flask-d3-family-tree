# Family Tree Visualisation

A Python and Flask application for creating, managing and visualising family trees.

The application stores family tree data in PostgreSQL, models relationships between people, and generates the graph structure required by an interactive D3.js family tree visualisation.

## Why I Built This

I originally created this project to learn modern Python web development. Over time it evolved into a larger application and became a way to learn:

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Pytest
- Git and GitHub
- AWS deployment
- Test-driven development
- Data modelling and transformation

The project started as a CSV-based prototype and evolved into a database-backed web application with automated tests, data import tools and an interactive user interface.

## Features

- Create and manage multiple family trees
- Create, edit and delete people
- Create parent-child relationships
- Create partner relationships
- Import family tree data from CSV files
- Store all data in PostgreSQL
- Generate D3.js-compatible graph structures
- Interactive Flask web interface
- Automated test suite using Pytest

## Technology Stack

### Backend

- Python
- Flask
- PostgreSQL
- SQLAlchemy

### Frontend

- HTML
- Jinja Templates
- Bootstrap
- D3.js

### Testing

- Pytest
- Monkeypatching and mocking
- Database interaction testing

### Deployment

- WSGI
- AWS Elastic Beanstalk (previously deployed)

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

As the project grew, functionality was progressively separated into modules to improve maintainability, readability and testability.

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

Pytest fixtures, monkeypatching and mocked database interactions are used to validate behaviour without requiring changes to a live database.

## Installation

### Clone the repository

```bash
git clone https://github.com/boymalloy/python-flask-d3-family-tree.git
cd python-flask-d3-family-tree
```

### Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure Flask

```bash
export FLASK_APP=app
export FLASK_DEBUG=1
```

### Configure PostgreSQL

Install PostgreSQL and create a database called `family_tree`.

Create a `.flaskenv` file containing:

```bash
FLASK_APP=app
FLASK_DEBUG=1
DATABASE_URL="postgresql://postgres:<password>@localhost:5432/family_tree"
SECRET_KEY="<your-secret-key>"
```

### Run the application

```bash
flask run
```

Then browse to:

```text
http://127.0.0.1:5000/
```

## Lessons Learned

This project helped me learn:

- Flask application structure
- Relational database design
- Test-driven development using Pytest
- SQLAlchemy modelling
- File upload handling and validation
- Environment-specific configuration
- Data transformation and graph generation
- Deploying Python applications to AWS

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

I did not create the D3 visualisation itself.

The visualisation is based on [BenPortner's js_family_tree](https://github.com/BenPortner/js_family_tree), which in turn is based on the [collapsible d3 tree example](https://gist.github.com/d3noob/43a860bc0024792f8803bba8ca0d5ecd) by d3noob.

The Python application, database design, import tooling, testing and integration work were developed as part of this project.
