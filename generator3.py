def generator3():
    
    uf = pd.read_csv("static/input/input.csv")

    # build the persons dataframe with data from uf
    persons = pd.DataFrame()
    persons.loc[:, 'id'] = uf.loc[:, 'id']
    persons.loc[:, 'name'] = uf.loc[:, 'name']
    persons["own_unions"] = ""
    persons.loc[:, 'birthyear'] = uf.loc[:, 'birthyear']
    persons.loc[:, 'birthplace'] = uf.loc[:, 'birthplace']
    persons.loc[:, 'partners'] = uf.loc[:, 'partners']
    
    #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partners' : pd.Series(dtype='str'),
                    'children': pd.Series(dtype='str')})

    
    # for every row in the user friendly table
    for index, row in persons.iterrows():
        
        # get the union
        partnership = persons.loc[index,'id'] + "," +  str(persons.loc[index,'partners'])
        # ... and the same union in reverse order
        reverse = str(persons.loc[index,'partners']) + "," +  persons.loc[index,'id']
        
        # if either version of the union is already in the unions table, do nothing
        if unions.isin([partnership,reverse]).any().any():
            print("nothing")
        # else if the union hasn't been recorded yet...
        else:
            # if the union isn't there, stop
            if pd.isna(persons.loc[index,'partners']):
                print("nothing")
            # but if it is there....
            else:
               # if this is the first union in the dataframe, call it u1
                if unions.empty:
                    NEWunionID = "u1"
                
                else:
                    # else get the last union number and give this union the next number on
                    OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])
                    NEWunionID = "u" + str(int(OLDunionID[1]) + 1)
                
                # write the new union id to the person that the current iteration is on
                persons.loc[index,'own_unions'] = NEWunionID

                # write the union id to the partner's row in the persons table
                who = str(persons.loc[index,'partners'])
                persons.loc[persons['id'] == who, 'own_unions'] = NEWunionID

                # create a dictionary with the data to write to the dataframe
                row = {'id': NEWunionID, 'partners': partnership, 'children': "child"}
                    
                # Append the dictionary to the DataFrame
                unions.loc[len(unions)] = row
                

    # fixes the union ids in the dataframe
    persons.at[0, 'own_unions'] = ['u1']
    persons.at[1, 'own_unions'] = ['u1']

    # turns the dataframe into the persons fragment of the tree json
    fragment = persons.to_json(orient="index")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\"0\",\"persons\":"

    # hard codes the end bit of the tree json, including unions and links
    end = ",\"unions\": {\"u1\": { \"id\": \"u1\", \"partner\": [\"0\", \"1\"], \"children\": [\"2\"] }, }, \"links\": [[\"0\", \"u1\"], [\"1\", \"u1\"], [\"u1\", \"2\"],]}"

    # combines all of the bits of the tree together
    assembled = start + fragment + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "w",) as file_Obj:
        file_Obj.write(assembled)

    return "Try again!"