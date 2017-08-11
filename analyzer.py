import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def set_plot(pitchers, names, column, n, year, title):
    """Takes a dictionary of dataframes as arg1, a list of names as arg2,
    a string as arg3, an integer as arg4, and an int year as arg5. Ranks
    pitchers(arg1) based on column (arg3) in year (arg5) and divides 
    into n quantiles (arg4), then plots the ranked pitchers as a blue
    line, those in list "names" as red x's, and dotted lines and group
    labels to show groups given by report.
    """
    fig = plt.figure(figsize=(16,10)) #big plot
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_ylabel('{} in {}'.format(column, year)) #describe plot
    ax.set_xlabel('Player Rank from Lowest {} to Highest {} in {}'.format(column, column, year))
    length = len(pitchers)
    group_size = length/n # to rank into n groups
    ranked_values = [] #will contain all values for 'column'
    for pitcher in pitchers:
        df = pitchers[pitcher]
        i = df[df['Year']==year].index #gets index for year we need
        ranked_values.append(float(df.loc[i, column])) #gets value from column that year
    ranked_values.sort() #sorts from lowest to highest value, 'ranks'
    plt.plot(ranked_values) #plots in default blue ranked values, lowest to highest
    y_scale = max(ranked_values)/10 #for text placement
    txt_loc = group_size/2 #x coord for first group label
    for i in range(0, n):
        y_val = ranked_values[int(group_size * i)] #min y value for group 
        plt.axhline(y=y_val, color='k', linestyle='dashed') #plots a line for group limit
        ax.text((txt_loc+group_size/4), y_val+(y_scale/n), 'Group {}'.format(i+1), fontsize=11, color='g') #group label
        txt_loc += group_size #reposition x coord for next group label
    rank = 0
    value = 0
    for pitcher in pitchers:
        df = pitchers[pitcher] #get player df
        i = df[df['Year']==year].index #index for this year
        if pitcher in names: #plots red x at player's location along plot
                value = float(df.loc[i, column])
                rank = ranked_values.index(value)
                plt.scatter(x=rank, y=value, marker='x', color='r')
    plt.scatter(x=rank, y=value, marker='x', color='r', label='Player injured in 2016')
    plt.legend(loc='upper left')
                
def report(pitchers, names, column, n, year):
    """Takes a dictionary of dataframes as arg1, a list of names as arg2,
    a string as arg3, an integer as arg4, and an int year as arg5. Ranks
    pitchers(arg1) based on column (arg3) in year (arg5) and divides 
    into n quantiles (arg4), counts the number of names(arg2) that 
    belong in each quantile, and reports back the number in each quantile
    (called groups 1-n) as a percentage of all pitchers.
    """
    group_size = int(len(pitchers)/n) #define quantile size for n quantiles
    ranked_values = []
    for pitcher in pitchers:
        df = pitchers[pitcher]
        j = list(df[df['Year']==year].index)[0]
        ranked_values.append(float(df.loc[j, column]))
    ranked_values.sort() #ranks all values by size 
    lower_bound = 0 #bounds for first group
    upper_bound = group_size
    for i in range(0, n):
        basket = 0 #basket is number in group i+1
        for name in names:
            df = pitchers[name]
            ind = list(df[df['Year']==year].index)[0] #get index for year
            if ranked_values[lower_bound] <= df.loc[ind, column] <= ranked_values[upper_bound-1]:
                basket += 1 #if value within group bounds, add to basket
            if i == n-1 and df.loc[ind, column] == ranked_values[upper_bound-1]:
                basket += 1 #Because above for loop does not count if name is highest value in ranked
        print('Group {}, {}% of all players, represents {}% of the group.'.format((i+1), (100/n), 100*(basket/len(names)))) #reports results
        lower_bound += group_size #iterate group bounds by group size
        upper_bound += group_size
    
