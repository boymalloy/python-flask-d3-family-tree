data = {
    "start":"0",
    "persons": {
        "0": {
            "id": "0",
            "name": "Alex John Malloy",
            "own_unions": ["u1"],
            "birthyear": 1980,
            "birthplace": "Greenwich",
            "partners": "EAM1982"
        },
        "1": {
            "id": "1",
            "name": "Erin Amanda McIntosh",
            "own_unions": ["u1"],
            "birthyear": 1982,
            "birthplace": "Kirkcaldy",
            "partners": "AJM1980"
        },
        "2": {
            "id": "2",
            "name": "Genevieve Valerie McIntosh Malloy",
            "own_unions": "",
            "birthyear": 2018,
            "birthplace": "Lewisham",
            "partners": None
        }
        "3": {
            "id": "3",
            "name": "Genevieve Valerie McIntosh Malloy",
            "own_unions": "",
            "birthyear": 2018,
            "birthplace": "Lewisham",
            "partners": None
        }
    },
    "unions": {
        "0": { "id": "u1", "partner": ["0", "1"], "children": ["2","3"] },
    },
    "links": [
        ["0", "u1"],
        ["1", "u1"],
        ["u1", "2"],
        ["u1", "3"],
    ]

}