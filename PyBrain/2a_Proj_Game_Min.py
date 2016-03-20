#############################################
# Program: 2a_Proj_Game_Min.py
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

days_ahead = 1
look_back_day = 14
year = '2016'
regulation_minutes = 240

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

if os.path.isdir('Data/ProjMin')==False:
    os.mkdir('Data/ProjMin')

game_list = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
game_list['Date'] = pd.to_datetime(game_list['Date'])
DateAsOf = max(game_list['Date'].loc[(game_list['Home_PTS']!=' ')])
print "DateAsOf is " + str(DateAsOf.date())
game_list['DateDiff'] = game_list['Date'] - DateAsOf

game_list = game_list.loc[(game_list['DateDiff']>timedelta(0)) & (game_list['DateDiff']<=timedelta(days_ahead))].copy()

pred_games = []
houses = ['Home', 'Away']
for house in houses:
    games = game_list[['Date', house]].copy()
    games = games.rename(columns={house: 'Tm'})
    games['Tm'] = games['Tm'].replace(to_replace=team_nm)
    games['house'] = house
    pred_games.append( games )
pred_games = pd.concat(pred_games)

player_min_ave = pd.read_csv('Data/Input_Files/' + 'Ave_Min_' + year + '_' + str(DateAsOf.date()) + '.csv')
player_min_ave = pd.merge(player_min_ave[['Tm', 'Players', 'MP_Ave_LB'+str(look_back_day)]], pred_games, how='inner', on='Tm')

# groupby team date and norm min by 240
player_min_ave_gb = player_min_ave.groupby(by=['Date', 'Tm'])
adj_player_min = []
for key, data in player_min_ave_gb:
    gb_data = data.copy()
    gb_data['MP_Ave_LB'+str(look_back_day)] = gb_data['MP_Ave_LB'+str(look_back_day)]*(regulation_minutes/sum(gb_data['MP_Ave_LB'+str(look_back_day)]))
    adj_player_min.append( gb_data )
adj_player_min =pd.concat( adj_player_min )

adj_player_min.to_csv('Data/ProjMin/proj_min_for_' + str(days_ahead) + 'days_' + str(DateAsOf.date()) + '.csv', index=False)
