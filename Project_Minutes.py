#############################################
# Program: Project_Minutes.py
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
num_stats = ['MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
look_back_days = [0, 7, 14, 30]

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

game_list = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
game_list['Date'] = pd.to_datetime(game_list['Date'])
DateAsOf = max(game_list['Date'].loc[(game_list['Home_PTS']!=' ')])
print ("Date As Of: " + str(DateAsOf.date()))

game_list['Away_Tm'] =game_list['Away'].replace(team_nm)
game_list['Home_Tm'] =game_list['Home'].replace(team_nm)
game_list['BS_filename'] = 'BS_' + game_list['Date'].dt.strftime('%Y-%m-%d') + '_' + game_list['Away_Tm'] + '_' + game_list['Home_Tm'] + '.csv'
game_list = game_list.loc[game_list['Home_PTS']!=' ']

box_scores, box_scores_p36 = parse_box_scores(game_list, year, num_stats)

player_min = box_scores[['Date', 'Tm', 'Players', 'MP']].loc[box_scores['Players']!='Team Totals'].copy()
player_min['day_diff'] = DateAsOf - player_min['Date']

for l, look_back_day in enumerate(look_back_days):
    if look_back_day==0: lb_logic = [True for i in range(player_min.shape[0])]
    else: lb_logic = lb_logic = player_min['day_diff']<=timedelta(look_back_day)
    mp_aves = DataFrame(player_min.loc[lb_logic].groupby(by=['Tm', 'Players'])['MP'].mean()).rename(columns={'MP':'MP_Ave_LB'+str(look_back_day)})
    if l==0: player_min_ave = mp_aves
    else: player_min_ave = pd.merge(player_min_ave, mp_aves, how='outer', left_index=True, right_index=True)

for l, look_back_day in enumerate(look_back_days):
    player_min_ave['MP_Ave_LB'+str(look_back_day)].loc[player_min_ave['MP_Ave_LB'+str(look_back_day)].isnull()] = 0

player_min_ave.to_csv('Data/Input_Files/' + 'Ave_Min_' + year + '_' + str(DateAsOf.date()) + '.csv')

