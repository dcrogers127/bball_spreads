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
DateAsOf = '2016-01-17'
train_date = pd.to_datetime('2016-01-11')

pybrain = pd.read_csv('Data/Spread_Prediction/wma_pybrain_pred_v4.csv').rename(columns={'Away': 'AWAY', 'Home': 'HOME'})
#lines = pd.read_csv('aggregated_point_spread.csv')
#pybrain = pd.merge(pybrain, lines, how='left', on=['Date', 'AWAY', 'HOME'])
#pybrain['SRS_Spread'] = pybrain['AWAY_SRS'] - pybrain['HOME_SRS']

def rmse(df, y, y_hat):
    rmse = np.mean((df[y_hat] - df[y]) ** 2) ** .5
    print "RMSE of " + y_hat + " is: " + str(rmse)
    return rmse

# preds = ['Home Spread', 'pred', 'SRS_Spread_0', 'SRS_Spread_5', 'SRS_Spread_10', 'SRS_Spread_15']
# preds = ['Home Spread', 'pred', 'SRS_Spread']
preds = ['pred']
for pred in preds: 
    rmse(pybrain, 'SPREAD', pred)

#preds = ['pred', 'SRS_Spread_0', 'SRS_Spread_5', 'SRS_Spread_10', 'SRS_Spread_15']
# preds = ['pred', 'SRS_Spread']
# for pred in preds: 
#     wins = (pybrain['SPREAD']>pybrain['Home Spread'])==(pybrain[pred]>pybrain['Home Spread'])
#     print pred + ' has ' + str(sum(wins)) + ' out of ' + str(len(wins)) + ' for a win pct of ' + str((sum(wins) + 0.0)/len(wins))

#pred = 'SRS_Spread_0'
#pred = 'SRS_Spread'
# pred = 'pred'
# wins = (pybrain['SPREAD']>pybrain['Home Spread'])==(pybrain[pred]>pybrain['Home Spread'])
# pybrain['win'] = wins
# pybrain['win_v2'] = np.array(wins, dtype=int)
# pybrain['win_v2'].loc[pybrain['win_v2']==0] = -1
# pybrain['win_v2'].loc[np.abs(pybrain['Home Spread']-pybrain[pred])<2.5] = 0
# pybrain[['SPREAD', 'Home Spread', pred, 'win', 'win_v2']]
# pybrain['win_v2'].value_counts()
# 
# # .679 from v3
# (sum(pybrain['win_v2']==1)  + 0.0) / sum((pybrain['win_v2']==1) | (pybrain['win_v2']==-1))
# 
