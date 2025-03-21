data = {
    "start": "SS1963",
    "persons": {
        "SS1963": {
            "name": "Scott Summers",
            "own_unions": ["u1", "u2", "u3"],
            "birthyear": 1963,
            "birthplace": "Anchorage, Alaska",
            "partners": ["MP1983", "JG1963", "EF1980"],
            "children": ["NCCS1986", "RS2009", "NG1995", "RS1980"]
        },
        "MP1983": {
            "name": "Madelyne Pryor",
            "own_unions": ["u1"],
            "birthyear": 1983,
            "birthplace": "Unknown",
            "partners": ["SS1963"],
            "children": ["NCCS1986"]
        },
        "NCCS1986": {
            "name": "Nathan Christopher Charles Summers",
            "own_unions": [],
            "birthyear": 1986,
            "birthplace": "Unknown",
            "partners": [],
            "children": []
        },
        "JG1963": {
            "name": "Jean Grey",
            "own_unions": ["u2"],
            "birthyear": 1963,
            "birthplace": "Annandale-on-Hudson, New York",
            "partners": ["SS1963"],
            "children": ["NG1995", "RS1980"]
        },
        "EF1980": {
            "name": "Emma Frost",
            "own_unions": ["u3"],
            "birthyear": 1980,
            "birthplace": null,
            "partners": ["SS1963"],
            "children": ["RS2009"]
        },
        "RS2009": {
            "name": "Ruby Summers",
            "own_unions": [],
            "birthyear": 2009,
            "birthplace": null,
            "partners": [],
            "children": []
        },
        "NG1995": {
            "name": "Nate Grey",
            "own_unions": [],
            "birthyear": 1995,
            "birthplace": null,
            "partners": [],
            "children": []
        },
        "RS1980": {
            "name": "Rachel Summers",
            "own_unions": [],
            "birthyear": 1980,
            "birthplace": null,
            "partners": [],
            "children": []
        }
    },
    "unions": {
        "u1": {
            "id": "u1",
            "partner": ["SS1963", "MP1983"],
            "children": ["NCCS1986"]
        },
        "u2": {
            "id": "u2",
            "partner": ["SS1963", "JG1963"],
            "children": ["NG1995", "RS1980"]
        },
        "u3": {
            "id": "u3",
            "partner": ["SS1963", "EF1980"],
            "children": ["RS2009"]
        }
    },
    "links": [
        ["SS1963", "u1"],
        ["MP1983", "u1"],
        ["u1", "NCCS1986"],
        ["SS1963", "u2"],
        ["JG1963", "u2"],
        ["u2", "NG1995"],
        ["u2", "RS1980"],
        ["SS1963", "u3"],
        ["EF1980", "u3"],
        ["u3", "RS2009"]
    ]
}
