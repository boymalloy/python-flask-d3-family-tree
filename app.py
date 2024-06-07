from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# creates a path to all the static files for the tree and the csv inputs
app = Flask(__name__, static_url_path='/static')

bootstrap = Bootstrap(app)

import pandas as pd


def generator():
    # imports 3 people from a csv to a dataframe
    data = pd.read_csv("static/input/ids.csv", dtype=str)

    # fixes the union ids in the dataframe
    data.at[0, 'own_unions'] = ['u1']
    data.at[1, 'own_unions'] = ['u1']

    # turns the dataframe into the persons fragment of the tree json
    fragment = data.to_json(orient="index")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\"0\",\"persons\":"

    # hard codes the end bit of the tree json, including unions and links
    end = ",\"unions\": {\"u1\": { \"id\": \"u1\", \"partner\": [\"0\", \"1\"], \"children\": [\"2\"] }, }, \"links\": [[\"0\", \"u1\"], [\"1\", \"u1\"], [\"u1\", \"2\"],]}"

    # combines all of the bits of the tree together
    assembled = start + fragment + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "x",) as file_Obj:
        file_Obj.write(assembled)

    return "Squeeeeee"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/treegenerator')
def treegenerator():
    return render_template('treegenerator.html', generator=generator)
