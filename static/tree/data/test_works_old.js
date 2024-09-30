data = {
    "start":"id1",
    "persons": {
        "id1": { "id": "id1", "name": "Alex John Malloy", "own_unions": ["u1"], "birthyear":1980, "birthplace":"Greenwich"},
        "id2": { "id": "id2", "name": "Erin Amanda McIntosh", "own_unions": ["u1"], "birthyear":1982, "birthplace":"Kirkcaldy", "partners":"AJM1980", "children":"GVMM2018"},
        "id3": { "id": "id3", "name": "Tallulah McIntosh Malloy", "birthyear":2012, "birthplace":"Croydon"},
        "id4": { "id": "id4", "name": "Genevieve Valerie McIntosh Malloy", "birthyear":2018, "birthplace":"Lewisham"},
    },
    "unions": {
        "u1": { "id": "u1", "partner": ["id1", "id2"], "children": ["id3", "id4"] },
    },
    "links": [
        ["id1", "u1"],
        ["id2", "u1"],
        ["u1", "id3"],
        ["u1", "id4"],
    ]

}