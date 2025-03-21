def generator3(file_name):
    
    file_path = "static/input/"

    file_path_and_name = file_path + str(file_name)
    
    uf = pd.read_csv(file_path_and_name)

    # Build the persons dataframe with data from uf
    persons = pd.DataFrame({
        'id': uf['id'].apply(lambda x: x.strip() if isinstance(x, str) else x),  # Remove spaces from 'id'
        'name': uf['name'],  
        'own_unions': [[] for _ in range(len(uf))],  # Initialize as empty lists for each row
        'birthyear': uf['birthyear'],
        'birthplace': uf['birthplace'],
        'partners': uf['partners'].apply(lambda z: [p.strip() for p in z.split(',')] if pd.notna(z) else []),  # Strip each partner
        'children': uf['children'].apply(lambda x: [c.strip() for c in x.split(',')] if pd.notna(x) else [])  # Strip each child
    })
    
    #build a blank unions table
    unions = pd.DataFrame({'id': pd.Series(dtype='str'),
                    'partner' : pd.Series(dtype='object'),
                    'children': pd.Series(dtype='object')})
    
    #build a blank links table
    links = pd.DataFrame({'from': pd.Series(dtype='str'),
                    'to': pd.Series(dtype='str')})

    
    # for every row in persons
    for index, row in persons.iterrows():
        
        # get the list of partners
        boffers = persons.at[index, 'partners']
        # loop through the list
        for boffer in boffers:

            # state the union
            partnership = [persons.loc[index, 'id'], boffer]

            # if the union (in either order) is already in the unions table, do nothing
            if unions['partner'].apply(lambda x: set(x) == set(partnership)).any():
                print("nothing")
            # but if they are not present, proceed to create the union
            else:
                
                # first set the union id
                # if there are no unions yet, set the NEWunionID to u1
                if unions.empty:
                    NEWunionID = "u1" 
                # else get the last union number and give this union the next number on
                else:
                    OLDunionID = re.findall(r'\d+|\D+', unions['id'].iloc[-1])
                    NEWunionID = "u" + str(int(OLDunionID[1]) + 1)
                    
                # write the new union id to the person that the current iteration is on
                persons.at[index, 'own_unions'].append(NEWunionID)
                
                # append the union id to the partner's row in the persons table
                # Find the rows where 'id' matches boffer
                matching_rows = persons.loc[persons['id'] == boffer]

                # Check if there are any matching rows
                if not matching_rows.empty:
                    # Get the index of the first matching row
                    boffer_index = matching_rows.index[0]

                    # Ensure 'own_unions' is a list before appending
                    if persons.at[boffer_index, 'own_unions'] is None:
                        persons.at[boffer_index, 'own_unions'] = []  # Initialize as empty list if None
                    
                    # Append the new union ID
                    persons.at[boffer_index, 'own_unions'].append(NEWunionID)
                else:
                    print(f"No matching row found for ID: {boffer}")

                # store the partners in a list to be stored in the unions df
                partnershipAsList = [persons.loc[index, 'id'], boffer]
                
                # get the chidren of each person
                person1offspring = persons.at[index, 'children']
                person2offspring = persons.at[boffer_index, 'children']
                
                # make a list of all the children common to both
                offspringtogether = []
                if person1offspring is not None:
                    for kid in person1offspring:
                        if kid in person2offspring:
                            offspringtogether.append(kid)

                # Create the union row with dynamically included children
                union_row = {'id': NEWunionID, 'partner': partnershipAsList, 'children': offspringtogether}

                # Append the new union to the DataFrame
                unions = pd.concat([unions, pd.DataFrame([union_row])], ignore_index=True)

    # Sets the index of the unions table to be the custom id but preserves the custom id as it's own field by copying it
    unions['id_copy'] = unions['id']
    unions.set_index('id', inplace=True,)
    unions = unions.rename(columns={'id_copy': 'id'})
    unions = unions.reindex(columns=['id', 'partner', 'children'])

    # Links bit
    # for each row in the unions df
    for index, row in unions.iterrows():
        
        # grab the unionID
        unionID = unions.loc[index, 'id']
       
       # grab both partners
        partners = unions.loc[index, 'partner']
        
        # make a temp variable that mimics a row of the links df and store the first partner agains the union ID
        row1 = {'from': partners[0], 'to': unionID}
        
        # Do the same for the second partner
        row2 = {'from': partners[1], 'to': unionID}
        
        # Append the two new rows to the links table
        links.loc[len(links)] = row1
        links.loc[len(links)] = row2

        # grab the list of children from the union and put it in an array
        kidstemp = unions.loc[index, 'children']
        # loop through the cildren in the array...
        for item in kidstemp:
            # create a new array that mimics a row in the links table, using the unionID as the from and the child's ID as the to
            rowk = {'from': unionID, 'to': item}
            # append that mimic row to the links df
            links.loc[len(links)] = rowk

    # Store the ID of the first person in the persons table so that it can be used as the starting point in the json file
    start_id = persons.iloc[0]['id']
    
    # Sets the index of the persons table to be the custom id 
    persons.set_index('id', inplace=True)

    # turns the dataframe into the persons fragment of the tree json
    persons_json = persons.to_json(orient="index")

    # turn the unions df to json
    unions_json = unions.to_json(orient="index")

    # turn the links df to json
    links_json = links.to_json(orient="values")

    # hard codes the first bit of the tree json
    start = "data = {\"start\":\""

    bitafterstartid = "\",\"persons\":"

    bitbetween = ",\"unions\": "

    # hard codes the end bit of the tree json, including unions and links
    links_start = ", \"links\": "

     # tint bit on the end
    end = "}"

    # combines all of the bits of the tree together
    assembled = start + start_id + bitafterstartid + persons_json + bitbetween + unions_json + links_start + links_json + end

    # writes the json tree to a static file
    with open("static/tree/data/test.js", "w",) as file_Obj:
        file_Obj.write(assembled)

    return links