#############################################
# Program: Ave_Stats.py
#
# Notes:
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
from datetime import datetime, timedelta

# years = ['2015', '2016']
years = ['2016']
bs_stats = ['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
ag_stats = ['mean']
pred_stats = [bs_stat+'_'+ag_stat for ag_stat in ag_stats for bs_stat in bs_stats]

def build_input(years, pred_stats):
    Playoff_Start_2015 = pd.to_datetime('2015-04-18')
    Playoff_End_2015 = pd.to_datetime('2015-07-18')

    team_nm = {
        'Atlanta Hawks'           :'ATL', 
        'Boston Celtics'          :'BOS',
        'Brooklyn Nets'           :'BRK',
        'Charlotte Hornets'       :'CHO',
        'Chicago Bulls'           :'CHI',
        'Cleveland Cavaliers'     :'CLE',
        'Dallas Mavericks'        :'DAL',
        'Denver Nuggets'          :'DEN',
        'Detroit Pistons'         :'DET',
        'Golden State Warriors'   :'GSW',
        'Houston Rockets'         :'HOU',
        'Indiana Pacers'          :'IND',
        'Los Angeles Clippers'    :'LAC',
        'Los Angeles Lakers'      :'LAL',
        'Memphis Grizzlies'       :'MEM',
        'Miami Heat'              :'MIA',
        'Milwaukee Bucks'         :'MIL',
        'Minnesota Timberwolves'  :'MIN',
        'New Orleans Pelicans'    :'NOP',
        'New York Knicks'         :'NYK',
        'Oklahoma City Thunder'   :'OKC',
        'Orlando Magic'           :'ORL',
        'Philadelphia 76ers'      :'PHI',
        'Phoenix Suns'            :'PHO',
        'Portland Trail Blazers'  :'POR',
        'Sacramento Kings'        :'SAC',
        'San Antonio Spurs'       :'SAS',
        'Toronto Raptors'         :'TOR',
        'Utah Jazz'               :'UTA',
        'Washington Wizards'      :'WAS'}

    InitTime = '1900-1-1'
    Last_DateAsOf = pd.to_datetime(InitTime)
    games_all_years = []

    n_games_lookback = 0
    SRS_Vars = ['Tm', 'MOV', 'SOS', 'SRS', 'N_GAME', 'N_HOME', 'N_AWAY', 'WIN', 'LOSS']
    segababa_Vars = ['Tm', 'gb2b', 'g3i4', 'g4i5']
    houses = ['HOME', 'AWAY']

    for year in years:
        game_list = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
        game_list['Date'] = pd.to_datetime(game_list['Date'])
        DateAsOf = max(game_list['Date'].loc[(game_list['Home_PTS']!=' ')])
        games = game_list.loc[game_list['Home_PTS']!=' '].copy()
        games = games[['Date', 'Away', 'Away_PTS', 'Home', 'Home_PTS']] 
        games['Away_PTS'] = pd.to_numeric(games['Away_PTS'], errors='coerce')
        games['Home_PTS'] = pd.to_numeric(games['Home_PTS'], errors='coerce')
        games = games.rename(columns={'Away_PTS':'GAME_AWAY_PTS', 'Home_PTS':'GAME_HOME_PTS' })
        games['SPREAD'] = games['GAME_AWAY_PTS'] - games['GAME_HOME_PTS']
        games['AWAY_Tm'] = games['Away'].replace(to_replace=team_nm)
        games['HOME_Tm'] = games['Home'].replace(to_replace=team_nm)

        if Last_DateAsOf<DateAsOf: Last_DateAsOf=DateAsOf

        games_w_hist = pd.read_csv('Data/Input_Files/min_wghted_hist_' + year + '_' + str(DateAsOf.date()) + '.csv')
        games_w_hist['Date'] = pd.to_datetime(games_w_hist['Date'])

        # need to recalc %
        pct_stats = ['FG', '3P', 'FT']
        for pct_stat in pct_stats:
            for ag_stat in ag_stats:
                games_w_hist[pct_stat+'%'+'_'+ag_stat] = games_w_hist[pct_stat+'_'+ag_stat] / games_w_hist[pct_stat+'A'+'_'+ag_stat]

        games = pd.merge(games, games_w_hist.rename(columns=dict(zip(['Tm', 'MP'] + pred_stats ,['AWAY_'+ stat for stat in ['Tm', 'MP'] + pred_stats]))), how='left', on=['Date', 'AWAY_Tm'])
        games = pd.merge(games, games_w_hist.rename(columns=dict(zip(['Tm', 'MP'] + pred_stats ,['HOME_'+ stat for stat in ['Tm', 'MP'] + pred_stats]))), how='left', on=['Date', 'HOME_Tm'])

        srs = pd.read_csv('Data/All_SRS_Calc_' + year + '_LB' + str(n_games_lookback) + '_' + str(DateAsOf.date()) + '.csv')
        srs['Tm'] = srs['Team'].replace(team_nm)
        srs = srs[['DateAsOf'] + SRS_Vars].rename(columns={'DateAsOf': 'Date'})
        srs['Date'] = pd.to_datetime(srs['Date'])

        segababa = pd.read_csv('Data/Input_Files/SEGABABA_' + year + '.csv')
        segababa['Tm'] = segababa['Team'].replace(team_nm)
        segababa = segababa [['Date'] + segababa_Vars]
        segababa['Date'] = pd.to_datetime(segababa['Date'])

        for house in houses:
            games = pd.merge(games, srs.rename(columns=dict(zip(SRS_Vars, [house+'_'+SRS_Var for SRS_Var in SRS_Vars]))), how='left', on=['Date', house+'_Tm'])
            games = pd.merge(games, segababa.rename(columns=dict(zip(segababa_Vars, [house+'_'+segababa_Var for segababa_Var in segababa_Vars]))), how='left', on=['Date', house+'_Tm'])

        # drop out playoff games. Gotta think of a better way if I add more years
        games = games.loc[((games['Date']>Playoff_Start_2015) & (games['Date']<Playoff_End_2015))==False]

        games_all_years.append( games )

    games_all_years = pd.concat( games_all_years )

    return games_all_years, Last_DateAsOf

games, DateAsOf = build_input(years, pred_stats)

games.to_csv('Data/Input_Files/mwa_srs_input_' + str(DateAsOf.date()) + '.csv', index=False)

