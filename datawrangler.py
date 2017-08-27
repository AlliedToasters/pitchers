import numpy as np
import pandas as pd
from collections import OrderedDict

def build_frame(df_in, year=2015):
    """Builds the dataframe we will use for this study of pitchers.
    Takes Lahman's database and gets out volume for pitcher. Row index
    is playerID, columns: Prior Seasons Out Volume(PSOV), 
    # Prior Seasons(NoPS), Mean Out Volume/Season(OV/S), 
    {year} Out Volume (OV{year}), {year} Normalized Out Volume (NOV{year}),
    Injured in 2016 (I2016) (Bool, default False)
    """
    pitchers = set() #will take all pitchers appearing in 2015
    for row in df_in.index:
        if df_in.loc[row]['yearID'] == year:
            pitchers.add(df_in.loc[row]['playerID'])
    col = [   #these will be columns for df_out
      'PSOV',
      'NoPS',
      'OV/S',
      'OV{}'.format(str(year)),
      'NOV{}'.format(str(year)),
      'Inj2016'
    ]
    df_out = pd.DataFrame(index=pitchers, columns=col) #build frame
    for player in df_out.index: #iterate over players and calculate needed values
        window = df_in[df_in['playerID'] == player] #just this player's rows
        seasons_prior = set() #use set to avoid counting duplicate years
        psov = 0
        ovyr = 0
        for row in window.index: #iterate through window to extract info
            if window.loc[row]['yearID'] < year:
                seasons_prior.add(window.loc[row]['yearID'])
                psov += window.loc[row]['IPouts']
            if window.loc[row]['yearID'] == year:
                ovyr += window.loc[row]['IPouts']
            if window.loc[row]['yearID'] > year:
                pass
        df_out.loc[player]['PSOV'] = psov #assign values
        df_out.loc[player]['OV{}'.format(str(year))] = ovyr
        df_out.loc[player]['NoPS'] = len(seasons_prior)
        if len(seasons_prior) == 0: 
            df_out.loc[player]['NOV{}'.format(str(year))] = 1 #if first season, normalized out vol = 1
        elif len(seasons_prior) == 1:
            df_out.loc[player]['OV/S'] = psov
            df_out.loc[player]['NOV{}'.format(str(year))] = ovyr/psov
        elif len(seasons_prior) > 1:
            mean_out_volume = psov/len(seasons_prior) #calculate prior mean outs/season
            df_out.loc[player]['OV/S'] = mean_out_volume
            df_out.loc[player]['NOV{}'.format(str(year))] = ovyr/mean_out_volume
        df_out.loc[player]['Inj2016'] = False #default not injured in 2016
    return df_out
        

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
    print('{} names were not found.'.format(len(names_not_found)))
    return name_list, names_not_found

