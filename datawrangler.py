import numpy as np
import pandas as pd
from collections import OrderedDict

def players_outs(df_in):
    """Takes a dataframe as argument and returns a dictionary,
    keys are player names, values are dataframes with columns
    'Year' and 'Outs Pitched'
    """
    players = {} #This will be returned at the end of the function.
    for row in df_in.index:
        rowdict = dict(df_in.loc[row]) #Dummy dict, keys are column names, values in corresponding row
        name = rowdict['playerID'] 
        if name not in players: #Checks to see if players already has this player
            df = pd.DataFrame(columns=['Year', 'Outs Pitched'], index=[1])
            # df will be value, playerID will be key in dict players
            df['Year'] = rowdict['year'] #df has 'Year' column
            df['Outs Pitched'] = rowdict['Outs Pitched'] #df has 'Outs Pitched' column
            players[name] = df #assign df to key name
        else: #in case playerID already in players
            df = pd.DataFrame(columns=['Year', 'Outs Pitched'], index=[(list(players[name].index)[-1]+1)])
            #creates a new dataframe with extra row
            df['Year'] = rowdict['year'] #populate new row
            df['Outs Pitched'] = rowdict['Outs Pitched']
            players[name] = pd.concat([players[name], df]) #concat old df with new row 
    return players 

def fill_gaps(df):
    """Takes a dataframe argument. If df has a gap between years (like
    2014, 2016), adds a row for the missing year with 0 outs pitched.
    """
    last_year = int(df.iloc[0]['Year']) #start w/ first year
    years_to_add = [] #this will track years we need to add
    for row in df.index:
        this_year = int(df.loc[row, 'Year'])
        gap = this_year - last_year
        for i in range(1, gap): #if gap is 0 or 1, no iteration
            years_to_add.append(last_year + i) #adds necessary year
        last_year = this_year #advances cycle
    for year in years_to_add: #to add year:
        i = list(df[df['Year']==(year - 1)].index)[0] #gets index for year-1
        new_df = pd.DataFrame(columns = df.columns, index=range(1, (len(df) + 2))) #new df w/ proper len
        years = list(df.loc[1:i, 'Year']) + [year] + list(df.loc[i+1:, 'Year']) #insert necessary year
        outs_pitched = list(df.loc[1:i, 'Outs Pitched']) + [0] + list(df.loc[i+1:, 'Outs Pitched']) #0 for outs pitched
        new_df['Year'] = years #insert into new df
        new_df['Outs Pitched'] = outs_pitched
        df = new_df
    return df
        

def season_load(df):
    """Takes dataframe as argument. Calculates average outs pitched to date
    for a given season and average outs pitched for total career including
    future seasons, creates new columns 'Season Load' and 'Season Load TD'.
    Season load is outs pitched/average outs pitched per season, season load
    TD is outs pitched/ average outs pitched to date. Returns a dataframe with
    two new columns.
    """
    if len(df) <= 1: #if one season, load is 1
        df.loc[1, 'Mean Outs/Season'] = df.loc[1, 'Outs Pitched']
        df.loc[1, 'Season Load TD'] = 1
        df.loc[1, 'Season Load'] = 1
    else:
        for row in df.index:
            if row == 1: #first season, mean outs == outs pitched
                df.loc[1, 'Mean Outs/Season'] = df.loc[1, 'Outs Pitched'] #
            else: #is mean outs per season before starting season
                df.loc[row, 'Mean Outs/Season'] = df.loc[row, 'Outs TD Start']/(row-1)
            if df.loc[row, 'Mean Outs/Season'] != 0: #avoid divide by zero error
                df.loc[row, 'Season Load TD'] = df.loc[row, 'Outs Pitched']/df.loc[row, 'Mean Outs/Season']
            #season load TD is outs pitched/mean outs/season that year
            else:
                df.loc[row, 'Season Load TD'] = 1 #default to 1
        total_outs = df.iloc[-1]['Outs TD Finish']
        avg_outs = total_outs/len(df)
        for row in df.index:
            if avg_outs != 0: #season load is outs pitched over career average outs pitched/season
                df.loc[row, 'Season Load'] = df.loc[row, 'Outs Pitched'] / avg_outs
            else:
                df.loc[row, 'Season Load'] = 1
    return df

def format_names(name_list):
    """takes a list of names of format "First Middle Lastname" and formats
    them into format "lastnfi01' (first five of last name, first two of first, 01.)
    returns a list of formatted names.
    """
    for name in name_list:
        index = name_list.index(name) #so we can reference name in list
        name = name.lower()
        names = name.split()
        name1 = names[-1] #last name
        if "'" in name1: #checks for names like o'leary
            name1 = name1[0] + name1[2:] #removes second character, "'"
        if len(name1) >= 5:
            name1 = name1[0:5] #first five of last name
        name2 = ''
        if names[0][1] == '.': #checks for names like a.j.
            name2 = names[0][0] + names[0][2] #change to aj
        else:
            name2 = names[0][0:2] #first two of first name
        newname = name1 + name2 + '01' #numeral 01 at end
        name_list[index] = newname #replace original name
    return name_list

def reconcile_names(name_list, reference_list):
    """Takes two lists of names of specific format. Finds corresponding name in
    second list and matches its two digit numeral ending. If not found, adds
    name not found to names_not_found. Returns a list of matched names and
    a list of names not found.
    """
    names_to_reconcile = list(reference_list)
    names_not_found = [] #this will be the list of names that don't match reference
    for i, name in enumerate(name_list):
        while name not in names_to_reconcile: #only if name not in list
            name_numeral = int(name[-2:])
            name_numeral += 1 #cycle through numeral
            name_numeral = str(name_numeral)
            if len(name_numeral) == 1: #add 0 to string so like 02
                name_numeral = '0' + name_numeral
            if len(name_numeral) > 2: #if too long, gives up
                name_numeral = '01'
                name = name[:-2] + name_numeral
                names_not_found.append(name) #records name not in ref list
                names_to_reconcile.append(name) #adds to this list to break loop
            new_name = name[:-2] + name_numeral #builds new name in our format
            name_list[i] = new_name #replaces name in list
            name = new_name #will break while loop if correct
    return name_list, names_not_found
