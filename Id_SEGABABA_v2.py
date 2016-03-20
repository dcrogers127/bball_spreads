#############################################
# Program: Id_SEGABABA.py - Id SEcond GAmes on a BAck to BAck
#
# Notes: v2 - standardize input
#
#
#
#
# Date:
#
#############################################

import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import os as os
from datetime import datetime

def Id_SEGABABA(year):
    games = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
    games['Date'] = pd.to_datetime(games['Date'])

    teams = list(games['Home'].value_counts().keys())
    teams.sort()

    segababa_df = []
    for (i, team) in enumerate(teams):
        segababa_df.append( games[['Date', 'Home']].loc[games['Home']==team] )
        segababa_df[i] = segababa_df[i].rename(columns={'Home':'Team'})
        segababa_df[i]['Home_Game'] = True
        away_games = games[['Date', 'Away']].loc[games['Away']==team]
        away_games = away_games.rename(columns={'Away':'Team'})
        away_games['Home_Game'] = False
        segababa_df[i] = segababa_df[i].append(away_games)
        segababa_df[i] = segababa_df[i].sort_values(by='Date', ascending=False)

        gb2b = np.zeros(segababa_df[i].shape[0], dtype=bool)
        g3i4 = np.zeros(segababa_df[i].shape[0], dtype=bool)
        g4i5 = np.zeros(segababa_df[i].shape[0], dtype=bool)
        for l in range( segababa_df[i].shape[0] ):
            if (l+1)<segababa_df[i].shape[0]:
                gb2b[l] = (segababa_df[i].iloc[l]['Date'] - segababa_df[i].iloc[l+1]['Date']).days==1
            if (l+3)<segababa_df[i].shape[0]:
                g3i4[l] = (segababa_df[i].iloc[l]['Date'] - segababa_df[i].iloc[l+2]['Date']).days==3
            if (l+4)<segababa_df[i].shape[0]:
                g4i5[l] = (segababa_df[i].iloc[l]['Date'] - segababa_df[i].iloc[l+3]['Date']).days==4

        segababa_df[i]['gb2b'] = gb2b
        segababa_df[i]['g3i4'] = g3i4
        segababa_df[i]['g4i5'] = g4i5

    all_segababa_df = pd.concat(segababa_df)
    all_segababa_df.to_csv('Data/Input_Files/SEGABABA_' + year + '.csv', index=False)

Id_SEGABABA('2016')
