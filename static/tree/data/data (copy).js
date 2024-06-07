data = {
    "start":"0",
    "persons": {
        "0": { "id": "0", "name": "Alex John Malloy", "own_unions": ["u1"], "birthyear":1980, "birthplace":"Greenwich"},
        "1": { "id": "1", "name": "Erin Amanda McIntosh", "own_unions": ["u1"], "birthyear":1982, "birthplace":"Kirkcaldy", "partners":"AJM1980", "children":"GVMM2018"},
        "2": { "id": "2", "name": "Genevieve Valerie McIntosh Malloy", "birthyear":2018, "birthplace":"Lewisham"}
    },
    "unions": {
        "u1": { "id": "u1", "partner": ["0", "1"], "children": ["2"] },
    },
    "links": [
        ["0", "u1"],
        ["1", "u1"],
        ["u1", "2"],
    ]

}