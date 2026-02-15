import os
from flask import Flask, render_template, session, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv

import pandas as pd
# Show all columns and rows of panda dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# from sqlalchemy.types import Date, Integer, String

# Create the Flask app
app = Flask(__name__, static_url_path='/static')

if os.getenv("FLASK_ENV") != "production":
    load_dotenv(".flaskenv")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///:memory:")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "dev-only-fallback")

# Build extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

import routes

# if the script is executed directly, run the app
if __name__ == '__main__':
    app.run(debug=True)