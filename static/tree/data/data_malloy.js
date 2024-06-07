data = {
    "start": "alex",
    "persons": {
        "alex": { "id": "alex", "name": "Alex John Malloy", "birthyear": 1980, "own_unions": ["u1"], "birthplace":"Greenwich", "parent_union": "u2" },
        "erin": { "id": "erin", "name": "Erin Amanda McIntosh", "birthyear": 1982, "own_unions": ["u1"],  "birthplace":"Kirkcaldy", },
        "evie": { "id": "evie", "name": "Genevieve Valerie McIntosh Malloy", "birthyear": 2018,  "birthplace":"Lewisham",  "parent_union": "u1",  },
        "ann": { "id": "ann", "name": "Ann Lilian Gee", "birthyear": 1953,  "birthplace":"",  "parent_union": "",  },
        "john": { "id": "john", "name": "John Curtis Malloy", "birthyear": 1947,  "birthplace":"",  "parent_union": "",  },
        "will": { "id": "will", "name": "William Dennis Malloy", "birthyear": 1985,  "birthplace":"",  "parent_union": "u2", "own_unions": ["u3"], },
        "helen": { "id": "helen", "name": "Helen Giddings", "own_unions": ["u3"],  },
        "harrison": { "id": "harrison", "name": "Harrison Anthony John Malloy", "birthyear": 2012,  "birthplace":"Woolwich",  "parent_union": "u3",  },
        "max": { "id": "max", "name": "Max Malloy", "birthyear": 2013,  "birthplace":"Kettering",  "parent_union": "u3",  },
        "myla": { "id": "myla", "name": "Myla Rose Malloy", "birthyear": 2018,  "birthplace":"Wellingborough",  "parent_union": "u3",  },
    },
    "unions": {
        "u1": { "id": "u1", "partner": ["alex", "erin"], "children": ["evie"], "unionYear": 2014 },
        "u2": { "id": "u2", "partner": ["ann", "john"], "children": ["alex","will"], },
        "u3": { "id": "u3", "partner": ["will", "helen"], "children": ["harrison","max","myla"], "unionYear":  2016 },
    },
    "links": [
        ["alex", "u1"],
        ["erin", "u1"],
        ["u1", "evie"],
        ["ann", "u2"],
        ["john", "u2"],
        ["u2", "alex"],
        ["u2", "will"],
        ["will", "u3"],
        ["helen", "u3"],
        ["u3", "harrison"],
        ["u3", "max"],
        ["u3", "myla"],
    ]
}