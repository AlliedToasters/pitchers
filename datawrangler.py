import numpy as np
import pandas as pd

def players_outs(df_in):
    players = {}
    for row in df_in.index:
        rowdict = dict(df_in.loc[row])
        name = rowdict['playerID']
        if name not in players:
            df = pd.DataFrame(columns=['Year', 'Outs Pitched'], index=[1])
            df['Year'] = rowdict['year']
            df['Outs Pitched'] = rowdict['Outs Pitched']
            players[name] = df
        else:
            df = pd.DataFrame(columns=['Year', 'Outs Pitched'], index=[(list(players[name].index)[-1]+1)])
            df['Year'] = rowdict['year']
            df['Outs Pitched'] = rowdict['Outs Pitched']
            players[name] = pd.concat([players[name], df])
    return players
    
def consol(df):
    count = {}
    for row in df.index:
        count[df.loc[row, 'Year']] = 0
    for row in df.index:
        count[df.loc[row, 'Year']] += df.loc[row, 'Outs Pitched']
    result = pd.DataFrame(index=range(df.index[0], len(count)+df.index[0]))
    result['Year'] = count.keys()
    result['Outs Pitched'] = count.values()
    return result

def fill_gaps(df):
    last_year = int(df.iloc[0]['Year'])
    years_to_add = []
    for row in df.index:
        this_year = int(df.loc[row, 'Year'])
        if (this_year - last_year) != 1:
            gap = this_year - last_year
            for i in range(1, gap):
                years_to_add.append(last_year + 1)
        last_year = this_year
    for year in years_to_add:
        i = list(df[df['Year']==(year - 1)].index)[0]
        new_df = pd.DataFrame(columns = df.columns, index=range(1, (len(df) + 2)))
        years = list(df.loc[1:i, 'Year']) + [year] + list(df.loc[i+1:, 'Year'])
        outs_pitched = list(df.loc[1:i, 'Outs Pitched']) + [0] + list(df.loc[i+1:, 'Outs Pitched'])
        new_df['Year'] = years
        new_df['Outs Pitched'] = outs_pitched
        df = new_df
    if 2015 in list(df['Year']):
        if df.iloc[-1]['Year'] != 2016:
            row2016 = pd.DataFrame(columns=df.columns)
            row2016['Year'] = 2016
            df = pd.concat([df, pd.DataFrame])
    return df
        

def tally_outs(df):
    if len(df) <= 1:
        df.loc[1, 'Outs TD Start'] = 0
        df.loc[1, 'Outs TD Finish'] = df.loc[1, 'Outs Pitched']
    else:
        for i, row in enumerate(df.index):
            if i == 0:
                df.loc[row, 'Outs TD Start'] = 0
            else:
                df.loc[row, 'Outs TD Start'] = df.loc[row-1, 'Outs Pitched'] + df.loc[row-1, 'Outs TD Start']
                df.loc[row-1, 'Outs TD Finish'] = df.loc[row, 'Outs TD Start']
        df.iloc[-1, 3] = df.iloc[-1, 2] + df.iloc[-1, 1]
    return df

def season_load(df):
    if len(df) <= 1:
        df.loc[1, 'Mean Outs/Season'] = df.loc[1, 'Outs Pitched']
        df.loc[1, 'Season Load TD'] = 1
        df.loc[1, 'Season Load'] = 1
    else:
        for row in df.index:
            if row == 1:
                df.loc[1, 'Mean Outs/Season'] = df.loc[1, 'Outs Pitched']
            else:
                df.loc[row, 'Mean Outs/Season'] = df.loc[row, 'Outs TD Start']/(row-1)
            if df.loc[row, 'Mean Outs/Season'] != 0:
                df.loc[row, 'Season Load TD'] = df.loc[row, 'Outs Pitched']/df.loc[row, 'Mean Outs/Season']
            else:
                df.loc[row, 'Season Load TD'] = 1
        total_outs = df.iloc[-1]['Outs TD Finish']
        avg_outs = total_outs/len(df)
        for row in df.index:
            if avg_outs != 0:
                df.loc[row, 'Season Load'] = df.loc[row, 'Outs Pitched'] / avg_outs
            else:
                df.loc[row, 'Season Load'] = 1
    return df

def format_names(name_list):
    for name in name_list:
        index = name_list.index(name)
        name = name.lower()
        names = name.split()
        name1 = names[-1]
        if "'" in name1:
            name1 = name1[0] + name1[2:]
        if len(name1) >= 5:
            name1 = name1[0:5]
        name2 = ''
        if names[0][1] == '.':
            name2 = names[0][0] + names[0][2]
        else:
            name2 = names[0][0:2]
        newname = name1 + name2 + '01'
        name_list[index] = newname
    return name_list

def reconcile_names(name_list, reference_list):
    names_to_reconcile = list(reference_list)
    names_not_found = []
    for i, name in enumerate(name_list):
        while name not in names_to_reconcile:
            name_numeral = int(name[-2:])
            name_numeral += 1
            name_numeral = str(name_numeral)
            if len(name_numeral) == 1:
                name_numeral = '0' + name_numeral
            if len(name_numeral) > 2:
                name_numeral = '01'
                name = name[:-2] + name_numeral
                names_not_found.append(name)
                names_to_reconcile.append(name)
            new_name = name[:-2] + name_numeral
            name_list[i] = new_name
            name = new_name
    return name_list, names_not_found
