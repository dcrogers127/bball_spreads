#############################################
# Program: SRS.py
#
# Notes: v2 - add ability to specify game look back
#        v3 - standardizes input file
#
#        Specifying 0 data lookback uses the whole season.
#
# Date:
#
#############################################

import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import os as os
from datetime import datetime

year = '2016'
start_date = datetime(int(year)-1, 11, 5)

all_games = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
all_games['Date'] = pd.to_datetime(all_games['Date'])
DateAsOf = max(all_games['Date'].loc[(all_games['Home_PTS']!=' ')])
print ("Date As Of: " + str(DateAsOf.date()))
all_games['Home_PTS'] = pd.to_numeric(all_games['Home_PTS'], errors='coerce')
all_games['Away_PTS'] = pd.to_numeric(all_games['Away_PTS'], errors='coerce')
all_games = all_games.loc[all_games['Away_PTS'].isnull()==False]
all_games = all_games.rename(columns={'Home': 'HOME', 'Home_PTS': 'HOME_PTS', 'Away': 'AWAY', 'Away_PTS': 'AWAY_PTS'})

teams = list(all_games['HOME'].value_counts().keys())
teams.sort()

dates = Series(all_games['Date'].value_counts().keys())
dates = list(dates[dates>start_date])
dates.sort()

def calc_sos(team_df, MOV_df, BaseRate):
    teams = list(MOV_df['Team'])
    SOS = [0 for team in teams]

    init_rate = MOV_df[BaseRate]
    MOV_df = MOV_df.rename(columns={'Team':'VS_Team', BaseRate: 'VS_' + BaseRate})
    for (i, team) in enumerate(teams):
        team_mov = pd.merge(team_df[i], MOV_df[['VS_Team', 'VS_' + BaseRate]], how='left', on='VS_Team')
        SOS[i] = np.mean(team_mov['VS_' + BaseRate])

    MOV_df = MOV_df.rename(columns={'VS_Team':'Team', 'VS_' + BaseRate:BaseRate})
    MOV_df['SOS'] = SOS - np.mean(SOS)
    MOV_df['SRS'] = MOV_df['MOV'] + MOV_df['SOS']
    delta = np.mean(np.absolute(MOV_df['SRS']-init_rate))
    return(MOV_df, delta)

def create_srs_csv(n_games_lookback, dates, data_date, n_iter=25):
    MOV_df = []
    for (d, date) in enumerate(dates):
        #d=0
        #date=dates[100]
        print date
        games = all_games.loc[all_games.Date<date]
        team_df = []
        MOV = [0 for team in teams]
        N_HOME = [0 for team in teams]
        N_AWAY = [0 for team in teams]
        WIN = [0 for team in teams]
        LOSS = [0 for team in teams]

        for (i, team) in enumerate(teams):
            #i = 0
            #team = teams[0]
            team_df.append( games[['Date', 'HOME', 'AWAY', 'HOME_PTS', 'AWAY_PTS']].loc[games['HOME']==team] )
            team_df[i]['Spread'] = team_df[i].HOME_PTS - team_df[i].AWAY_PTS
            team_df[i] = team_df[i].rename(columns={'HOME':'Team', 'AWAY':'VS_Team', 'HOME_PTS':'Team_PTS', 'AWAY_PTS':'VS_PTS',})
            team_df[i]['Home_Game'] = True
            away_games = games[['Date', 'HOME', 'AWAY', 'HOME_PTS', 'AWAY_PTS']].loc[games['AWAY']==team]
            away_games['Spread'] = away_games.AWAY_PTS - away_games.HOME_PTS
            away_games = away_games.rename(columns={'HOME':'VS_Team', 'AWAY':'Team', 'HOME_PTS':'VS_PTS', 'AWAY_PTS':'Team_PTS',})
            away_games['Home_Game'] = False
            team_df[i] = team_df[i].append(away_games)
            team_df[i] = team_df[i].sort_values(by='Date', ascending=False)
            if (n_games_lookback>0):
                team_df[i] = team_df[i][:n_games_lookback]

            N_HOME[i] = sum(team_df[i]['Home_Game'])
            N_AWAY[i] = sum(team_df[i]['Home_Game']==False)
            WIN[i] += sum(team_df[i].Team_PTS > team_df[i].VS_PTS)
            LOSS[i] += sum(team_df[i].Team_PTS < team_df[i].VS_PTS)
            MOV[i] = np.mean(team_df[i]['Spread'])

        MOV_df.append( DataFrame(teams, columns=['Team']) )
        MOV_df[d]['MOV'] = MOV

        MOV_df[d], delta = calc_sos(team_df, MOV_df[d], 'MOV')
        for i in range(n_iter):
            MOV_df[d], delta = calc_sos(team_df, MOV_df[d], 'SRS')

        MOV_df[d]['N_HOME'] = N_HOME
        MOV_df[d]['N_AWAY'] = N_AWAY
        MOV_df[d]['N_GAME'] = MOV_df[d]['N_HOME'] + MOV_df[d]['N_AWAY']
        MOV_df[d]['WIN'] = WIN
        MOV_df[d]['LOSS'] = LOSS
        MOV_df[d]['DateAsOf'] = date
        MOV_df[d]['delta'] = delta

    All_MOV_df = pd.concat(MOV_df)
    All_MOV_df.to_csv('Data/All_SRS_Calc_' + year + '_LB' + str(n_games_lookback) + '_' + data_date + '.csv', index=False)

create_srs_csv(n_games_lookback=0, dates=dates, data_date=str(DateAsOf.date()), n_iter=25)
#create_srs_csv(n_games_lookback=5, dates=dates, data_date=str(DateAsOf.date()), n_iter=25)
#create_srs_csv(n_games_lookback=10, dates=dates, data_date=str(DateAsOf.date()), n_iter=25)
#create_srs_csv(n_games_lookback=15, dates=dates, data_date=str(DateAsOf.date()), n_iter=25)
#create_srs_csv(n_games_lookback=20, dates=dates, data_date=str(DateAsOf.date()), n_iter=25)
