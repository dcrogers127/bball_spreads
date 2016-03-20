#############################################
# Program: Rolling_Player_Aves.py
#
# Notes: This does not handle cases where player 
#           has 0 MP and positive stats.  Adjusted 
#           the following to have 1 MP.
#        Salah Mejri, DAL, 2015-11-11
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

if os.path.isdir('Data/Input_Files')==False:
    os.mkdir('Data/Input_Files')

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
            box_scores_p36[num_stat].loc[box_scores_p36['MP']==0] = 0

    return box_scores, box_scores_p36


def rolling_ave(year, Per, DateAsOf, box_score_stats, num_stats, output_file=True, return_df=False, days_lb=0):
    dates = box_score_stats['Date'].unique()
    dates.sort()
    ave_stats = []
    for d, date in enumerate(dates):
        if days_lb==0: lb_logic = True
        else: lb_logic = (date-box_score_stats['Date'])<=timedelta(days_lb)
        box_scores_gb = box_score_stats.loc[(box_score_stats['Date']<=date) & lb_logic].groupby(by='Players')

        mean_stats = box_scores_gb[num_stats].mean().rename(columns=dict(zip(num_stats, [stat+'_mean' for stat in num_stats])))
        std_stats = box_scores_gb[num_stats].std().rename(columns=dict(zip(num_stats, [stat+'_std' for stat in num_stats])))
        med_stats = box_scores_gb[num_stats].median().rename(columns=dict(zip(num_stats, [stat+'_med' for stat in num_stats])))

        summ_stats = pd.merge(DataFrame(box_scores_gb['GP'].sum()), mean_stats, left_index=True, right_index=True)
        summ_stats = pd.merge(summ_stats, std_stats, left_index=True, right_index=True)
        summ_stats = pd.merge(summ_stats, med_stats, left_index=True, right_index=True)

        ave_stats.append( summ_stats )
        ave_stats[d]['Date'] = date

    ave_stats = pd.concat(ave_stats)

    if output_file:
        if days_lb==0: lb_str = ''
        else: lb_str = '_dayslb'+str(days_lb)
        ave_stats.to_csv('Data/Input_Files/Per_' + Per + '_' + year + '_Rolling_Ave' + lb_str + '_' + str(DateAsOf.date()) + '.csv')

    if return_df:
        return ave_stats

game_list = pd.read_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', dtype={'Away_PTS': np.object, 'Home_PTS': np.object})
game_list['Date'] = pd.to_datetime(game_list['Date'])
DateAsOf = max(game_list['Date'].loc[(game_list['Home_PTS']!=' ')])
print ("Date As Of: " + str(DateAsOf.date()))

game_list['Away_Tm'] =game_list['Away'].replace(team_nm)
game_list['Home_Tm'] =game_list['Home'].replace(team_nm)
game_list['BS_filename'] = 'BS_' + game_list['Date'].dt.strftime('%Y-%m-%d') + '_' + game_list['Away_Tm'] + '_' + game_list['Home_Tm'] + '.csv'
game_list = game_list.loc[game_list['Home_PTS']!=' ']

box_scores, box_scores_p36 = parse_box_scores(game_list, year, num_stats)

rolling_ave(year, 'Game', DateAsOf, box_scores, num_stats)
rolling_ave(year, '36', DateAsOf, box_scores_p36, num_stats)
rolling_ave(year, 'Game', DateAsOf, box_scores, num_stats, days_lb=7)
rolling_ave(year, '36', DateAsOf, box_scores_p36, num_stats, days_lb=7)
rolling_ave(year, 'Game', DateAsOf, box_scores, num_stats, days_lb=14)
rolling_ave(year, '36', DateAsOf, box_scores_p36, num_stats, days_lb=14)
rolling_ave(year, 'Game', DateAsOf, box_scores, num_stats, days_lb=30)
rolling_ave(year, '36', DateAsOf, box_scores_p36, num_stats, days_lb=30)
