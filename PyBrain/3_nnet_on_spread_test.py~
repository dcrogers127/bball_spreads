#############################################
# Program: ls_on_spread.py
#
# Notes: v3 - add 1\-1 indicator for team
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

year = '2016'
DateAsOf = '2016-03-15'
train_date = pd.to_datetime('2016-03-13')
min_games = 8

def norm(t, x):
    return (t - np.mean(x)) / np.std(x)
def renorm(t, x):
    return (t * np.std(x)) + np.mean(x)

if os.path.isdir('Data/Spread_Prediction')==False:
    os.mkdir('Data/Spread_Prediction')

## Pull Input
team_stats = pd.read_csv('Data/Input_Files/mwa_srs_input_' + DateAsOf + '.csv')
team_stats['Date'] = pd.to_datetime(team_stats['Date'])
bs_stats = ['FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', '+/-']
ot_stats = ['MOV', 'SOS', 'SRS', 'gb2b', 'g3i4', 'g4i5']
ag_stats = ['mean']
pred_stats = [bs_stat+'_'+ag_stat for ag_stat in ag_stats for bs_stat in bs_stats] + ot_stats

keys = ['Date', 'AWAY_Tm', 'HOME_Tm']
regressors = ['AWAY_'+stat for stat in pred_stats] + ['HOME_'+stat for stat in pred_stats]
outcome = ['GAME_AWAY_PTS', 'GAME_HOME_PTS', 'SPREAD']

## Neural Net
train_raw = team_stats.loc[(team_stats['AWAY_N_GAME']>min_games) & (team_stats['HOME_N_GAME']>min_games) & (team_stats['Date']<=train_date)].copy()
test_raw = team_stats.loc[(team_stats['Date']>train_date) & (team_stats['GAME_HOME_PTS'].isnull()==False)].copy()

train = train_raw.copy()
test = test_raw.copy()

x = regressors
y = 'SPREAD'

for var in x + [y]:
    train[var] = norm(train[var], train_raw[var])
    test[var] = norm(test[var], train_raw[var])

from pybrain.datasets import SupervisedDataSet
ds = SupervisedDataSet(len(x), 1)
for i in range(train[y].shape[0]):
    ds.addSample(train[x].iloc[i], train[y].iloc[i])

from pybrain.structure import SigmoidLayer, LinearLayer
from pybrain.tools.shortcuts import buildNetwork

net = buildNetwork(len(x),
                   int(np.mean([len(x), 1])), # number of hidden units
                   1,
                   bias = True,
                   hiddenclass = SigmoidLayer,
                   outclass = LinearLayer
                   )

from pybrain.supervised.trainers import BackpropTrainer
trainer = BackpropTrainer(net, ds, verbose = True)
#trainer.trainUntilConvergence(maxEpochs = 7000)
trainer.trainUntilConvergence(maxEpochs = None)

pred = np.empty(test[y].shape)
for i in range(test[y].shape[0]):
    pred[i] = net.activate(test[x].iloc[i])
test_raw['pred'] = renorm(pred, train_raw['SPREAD'])

#pd.set_option('expand_frame_repr', False)
test_raw[['Date', 'Away', 'Home', 'SPREAD', 'pred', 'HOME_SRS', 'AWAY_SRS']].to_csv('Data/Spread_Prediction/wma_pybrain_pred_v4.csv', index=False)
