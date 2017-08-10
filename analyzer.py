import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def set_plot(pitchers, names, column, n, year):
    """Takes a dictionary of dataframes as arg1, a list of names as arg2,
    a string as arg3, an integer as arg4, and an int year as arg5. Ranks
    pitchers(arg1) based on column (arg3) in year (arg5) and divides 
    into n quantiles (arg4), then plots the ranked pitchers as a blue
    line, those in list "names" as red x's, and dotted lines and group
    labels to show groups given by report.
    """
    fig = plt.figure(figsize=(16,10))
    ax = fig.add_subplot(111)
    ax.set_title('2016 Injuries')
    ax.set_ylabel('{} in {}'.format(column, year))
    ax.set_xlabel('Player Rank from Lowest {} to Highest {} in {}'.format(column, column, year))
    length = len(pitchers)
    group_size = length/n
    ranked_values = []
    for pitcher in pitchers:
        df = pitchers[pitcher]
        i = list(df[df['Year']==year].index)[0]
        ranked_values.append(float(df.loc[i, column]))
    ranked_values.sort()
    plt.plot(ranked_values)
    y_scale = max(ranked_values)/10
    txt_loc = group_size/2
    for i in range(0, n):
        y_val = ranked_values[int(group_size * i)]
        plt.axhline(y=y_val, color='k', linestyle='dashed')
        ax.text((txt_loc+group_size/4), y_val+(y_scale/n), 'Group {}'.format(i+1), fontsize=11, color='g')
        txt_loc += group_size
    rank_iter = 1
    for pitcher in pitchers:
        df = pitchers[pitcher]
        i = df[df['Year']==year].index
        if pitcher in names:
                value = float(df.loc[i, column])
                rank = ranked_values.index(value)
                plt.scatter(x=rank, y=value, marker='x', color='r')

                
def report(pitchers, names, column, n, year):
    """Takes a dictionary of dataframes as arg1, a list of names as arg2,
    a string as arg3, an integer as arg4, and an int year as arg5. Ranks
    pitchers(arg1) based on column (arg3) in year (arg5) and divides 
    into n quantiles (arg4), counts the number of names(arg2) that 
    belong in each quantile, and reports back the number in each quantile
    (called groups 1-n) as a percentage of all pitchers.
    """
    group_size = int(len(pitchers)/n)
    ranked_values = []
    for pitcher in pitchers:
        df = pitchers[pitcher]
        i = list(df[df['Year']==year].index)[0]
        ranked_values.append(float(df.loc[i, column]))
    ranked_values.sort()
    lower_bound = 0
    upper_bound = group_size
    for i in range(0, n):
        basket = 0
        for name in names:
            df = pitchers[name]
            ind = list(df[df['Year']==year].index)[0]
            if ranked_values[lower_bound] <= (float(df.loc[ind, column])) < ranked_values[upper_bound-1]:
                basket += 1
        if i == (n-1):
            basket += 1 #Because above for loop does not count last item
        print('Group {}, {}% of all players, represents {}% of the group.'.format((i+1), (100/n), 
100*(basket/len(names))))
        lower_bound += group_size
        upper_bound += group_size
    
