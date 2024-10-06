{
    "start": "AJM1980",
    "persons": {
      "AJM1980": {
        "name": "Alex John Malloy",
        "own_unions": ["u1"],
        "birthyear": 1980,
        "birthplace": "Greenwich",
        "partners": "EAM1982",
        "children": ["GVMM2018", "TTMM2012 "]
      },
      "EAM1982": {
        "name": "Erin Amanda McIntosh",
        "own_unions": ["u1"],
        "birthyear": 1982,
        "birthplace": "Kirkcaldy",
        "partners": "AJM1980",
        "children": ["GVMM2018", "TTMM2012 "]
      },
      "GVMM2018": {
        "name": "Genevieve Valerie McIntosh Malloy",
        "own_unions": [null],
        "birthyear": 2018,
        "birthplace": "Lewisham",
        "partners": null,
        "children": []
      },
      "TTMM2012": {
        "name": "Tailless Tallulah McMalloy",
        "own_unions": [null],
        "birthyear": 2012,
        "birthplace": "Croydon",
        "partners": null,
        "children": []
      }
    },
    "unions": {
      "u1": {
        "id": "u1",
        "partner": ["AJM1980", "EAM1982"],
        "children": ["GVMM2018", "TTMM2012 "]
      }
    },
    "links": [
      ["AJM1980", "u1"],
      ["EAM1982", "u1"],
      ["u1", "GVMM2018"],
      ["u1", "TTMM2012"]
    ]
  }