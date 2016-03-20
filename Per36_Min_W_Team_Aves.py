#############################################
# Program: Per36_Min_W_Team_Aves.py
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

year = '2016'
regulation_minutes = 240
num_stats = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
bs_stats = ['FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
ag_stats = ['mean']

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
team_list = team_nm.values()
team_list.sort()
team_i = dict(zip(team_list, [i for i in range(len(team_list))]))

def parse_box_scores(game_list, year, num_stats):
    box_scores = []
    for g, BS_filename in enumerate(game_list['BS_filename']):
        box_scores.append( pd.read_csv('Data/Box_Scores/' + year + '/Box/' + BS_filename) )
        box_scores[g]['Date'] = game_list['Date'][g]
    box_scores = pd.concat(box_scores)

    box_scores['MP'] = box_scores['MP'].replace({'Did Not Play':'00:00', 'Player Suspended':'00:00'})
    box_scores['MP'].loc[box_scores['MP'].str.len()==4] = '0' + box_scores['MP'].loc[box_scores['MP'].str.len()==4]
    box_scores['MP'].loc[box_scores['MP'].str.len()==3] = box_scores['MP'].loc[box_scores['MP'].str.len()==3] + ':00'
    box_scores['MP'] = '00:' + box_scores['MP']
    box_scores['MP'] = pd.to_timedelta(box_scores['MP'])
    box_scores['MP'] = box_scores['MP'].dt.seconds/60.0

    box_scores['GP'] = np.array(box_scores['MP']>0, dtype=int)

    for num_stat in num_stats:
        box_scores[num_stat] = pd.to_numeric(box_scores[num_stat], errors='coerce')

    box_scores_p36 = box_scores.copy()
    for num_stat in num_stats:
        if num_stat!='MP':
            box_scores_p36[num_stat] = (box_scores_p36[num_stat] / box_scores_p36['MP']) * 36

    return box_scores, box_scores_p36

def get_last_game(team_list, game_list):
    last_game_date = [0 for i in range(len(team_list))]
    last_games = [[] for i in range(len(team_list))]

    sides = ('Home', 'Away')
    for g in range(game_list.shape[0]):
        game = game_list.loc[g]
        for side in sides:
            ti = team_i[game[side+'_Tm']]
            if last_game_date[ti]!=0:
                last_games[ti].append( [game[side+'_Tm'], game['Date'], last_game_date[ti]] )
            last_game_date[ti] = game['Date']

    for ti in range(len(team_list)):
        last_games[ti] = DataFrame(last_games[ti], columns=['Tm', 'Date', 'LastGameDate'])
    return pd.concat(last_games)

game_list = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
game_list['Date'] = pd.to_datetime(game_list['Date'])
DateAsOf = max(game_list['Date'].loc[(game_list['Home_PTS']!=' ')])
print ("Date As Of: " + str(DateAsOf.date()))

game_list['Away_Tm'] =game_list['Away'].replace(team_nm)
game_list['Home_Tm'] =game_list['Home'].replace(team_nm)
game_list['BS_filename'] = 'BS_' + game_list['Date'].dt.strftime('%Y-%m-%d') + '_' + game_list['Away_Tm'] + '_' + game_list['Home_Tm'] + '.csv'
game_list = game_list.loc[game_list['Home_PTS']!=' ']

last_games = get_last_game(team_list, game_list)
box_scores, box_scores_p36 = parse_box_scores(game_list, year, num_stats)
player_stats = pd.read_csv('Data/Input_Files/Per_36_' + year + '_Rolling_Ave_' + str(DateAsOf.date()) + '.csv')
player_stats['Date'] = pd.to_datetime(player_stats['Date'])
player_stats = player_stats.rename(columns={'Date': 'LastGameDate'})

games_w_hist = pd.merge(box_scores[['Players', 'Date', 'Tm', 'MP']], last_games, how='left', on=['Tm', 'Date'])
games_w_hist = pd.merge(games_w_hist, player_stats[['Players', 'LastGameDate'] + [bs_stat+'_'+ag_stat for bs_stat in bs_stats for ag_stat in ag_stats]], how='left', on=['Players', 'LastGameDate'])

tot_game_min = games_w_hist[['Date', 'Tm', 'MP']].loc[games_w_hist['Players']=='Team Totals'].copy()
tot_game_min['MP_Adj'] = regulation_minutes / tot_game_min['MP']

games_w_hist = pd.merge(games_w_hist.loc[games_w_hist['Players']!='Team Totals'].copy(), tot_game_min[['Date', 'Tm', 'MP_Adj']], how='left', on=['Date', 'Tm'])

for bs_stat in bs_stats: 
    for ag_stat in ag_stats:
        games_w_hist[bs_stat+'_'+ag_stat] = games_w_hist['MP']*games_w_hist['MP_Adj']*games_w_hist[bs_stat+'_'+ag_stat]/36

games_w_hist_gb = games_w_hist.groupby(by=['Date','Tm'])
games_w_hist = games_w_hist_gb[['MP'] + [bs_stat+'_'+ag_stat for bs_stat in bs_stats for ag_stat in ag_stats]].sum()
games_w_hist.to_csv('Data/Input_Files/min_wghted_hist_' + year + '_' + str(DateAsOf.date()) + '.csv')

