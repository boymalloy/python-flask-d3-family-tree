def pandatest():
    try:
        # Use the app context to access the database session
        with app.app_context():
            query = text("SELECT * FROM person")
            result = db.session.execute(query)

            # Fetch all rows and get column names
            rows = result.fetchall()
            col_names = result.keys()  # Retrieve column names from the result object

            # Make a data frame from the fetched rows and column names
            persons = pd.DataFrame(rows, columns=col_names)
            
            # Add empty columns for partners, children and own unions
            persons["partners"] = None
            persons["children"] = None

            # start the index of the df from 1 to match the ids in the db
            persons.index = range(1, len(persons) + 1)

            # Loop through each person in the data frame, gets the id of each of their partners from the db, writes the partners' id to the partners column
            for index, row in persons.iterrows():
                persons.at[index, 'partners'] = get_partners(index)

            # Loop through each person in the data frame, gets the id of each of their children from the db, writes the childrens' id to the children column
            for index, row in persons.iterrows():
                persons.at[index, 'children'] = get_children(index)

            # build a blank unions table
            unions = pd.DataFrame({'partner' : pd.Series(dtype='object'),
                            'children': pd.Series(dtype='object')})
            
            def getChildrenTogether(person1,person2):
                # get the chidren of each person
                person1offspring = persons.at[person1, 'children']
                person2offspring = persons.at[person2, 'children']

                # make a list of all the children common to both
                offspringtogether = []
                if person1offspring is not None:
                    for kid in person1offspring:
                        if kid in person2offspring:
                                    offspringtogether.append(kid)

                return offspringtogether
            
            def makeUnionRow(person1,person2):
                partnership = [person1, person2]
                childrentogether = getChildrenTogether(person1,person2)
                union_row = {'partner': partnership, 'children': childrentogether}
                return union_row
            
            for index, row in persons.iterrows():
                person1 = index
                boffers = persons.at[person1, 'partners']

                for boffer in boffers:
                    partnership = [person1, boffer]
                    
                    # if the union (in either order) is already in the unions table, do nothing
                    if unions['partner'].apply(lambda x: set(x) == set(partnership)).any():
                        print("nothing")
                    # but if they are not present, proceed to create the union
                    else:
                    
                        new_row = makeUnionRow(person1,boffer)

                        # Add the new union to the DataFrame
                        unions = pd.concat([unions, pd.DataFrame([new_row])])

            # HERE

            persons["own_unions"] = [[] for _ in range(len(persons))]

            # # add all the newly minted unions to each partner's own_unions field
            # loop throough the list of unions
            for index, row in unions.iterrows():
                # loop through all the partners in the partners field
                for item in unions.at[index, 'partner']:
                    # add the union id from the outer look to each partner's record in the persons table
                    persons.at[item, 'own_unions'].append(index)

            
            #build a blank links table
            links = pd.DataFrame({'from': pd.Series(dtype='str'),'to': pd.Series(dtype='str')})

            # and from person to union for each partner
            for index, row in unions.iterrows():
                partnersx = unions.loc[index, 'partner']
                unionx = index
                personx = partnersx[0]
                persony = partnersx[1]
            
                newlinkrow1 = {'from': personx, 'to': unionx}
                newlinkrow2 = {'from': persony, 'to': unionx}
                links.loc[len(links)] = newlinkrow1
                links.loc[len(links)] = newlinkrow2

            for index, row in unions.iterrows():
                childrenx = unions.loc[index, 'children']
                for tidler in childrenx:
                    newchildrenlinkrow = {'from': index, 'to': tidler}
                    links.loc[len(links)] = newchildrenlinkrow
             
            
            persons_json = persons.to_json(orient="index")

            # turn the unions df to json
            unions_json = unions.to_json(orient="index")

            # turn the links df to json
            links_json = links.to_json(orient="values")

            # hard codes the first bit of the tree json
            start = "data = {\"start\":\"1\",\"persons\":"

            bitbetween = ",\"unions\": "

            # hard codes the end bit of the tree json, including unions and links
            links_start = ", \"links\": "

            # tint bit on the end
            ender = "}"

            # combines all of the bits of the tree together
            assembled = start + persons_json + bitbetween + unions_json + links_start + links_json + ender
            
            # writes the json tree to a static file
            with open("static/tree/data/test.js", "w",) as file_Obj:
                file_Obj.write(assembled)

            return assembled
            
    except Exception as e:
        # Handle exceptions and render an error message in the template
        return e