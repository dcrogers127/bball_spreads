#############################################
# Program: Pull_Box_Scores.py
#
# Notes: Parses box scores from basketball reference site.
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
import requests
from bs4 import BeautifulSoup
import time
import os

def Get_Games(year):
    url = 'http://www.basketball-reference.com/leagues/NBA_' + year + '_games.html'
    r = requests.get(url)
    time.sleep(sleep_secs)
    game_page = BeautifulSoup(r.text)
    td = game_page.find_all('td')
    row_elements = 9

    Games = []

    for g in range(len(td)/row_elements):
        i = g*row_elements
        Date = str(td[i].children.next().children.next())
        try: 
            box_url = td[i+2].children.next().attrs['href']
            Away_PTS = str(td[i+4].children.next())
            Home_PTS = str(td[i+6].children.next())
        except:
            box_url = ' '
            Away_PTS = ' '
            Home_PTS = ' '
        Away = str(td[i+3].children.next().children.next())
        Home = str(td[i+5].children.next().children.next())
        Games.append( [ Date, box_url, Away, Away_PTS, Home, Home_PTS ] )
    return (Games)

def parse_score_by_q(box_score_data):
    for b, box_score_datum in enumerate(box_score_data):
        try:
            Score_Head = box_score_datum.th.find_next().children.next()
            TestKey = box_score_datum.attrs["class"]
        except:
            Score_Head = ''

        if (Score_Head=='Scoring') & (b>0):
            q_scores = box_score_datum
            num_col = int(q_scores.th.find_next().attrs["colspan"])
            if (num_col==5):
                scores_col = ['Team', 'Q1', 'Q2', 'Q3', 'Q4', 'TOT']
            elif (num_col>5):
                scores_col = ['Team', 'Q1', 'Q2', 'Q3', 'Q4']
                for i in range(num_col-5):
                    scores_col.append('OT'+str(i))
                scores_col.append('TOT')
            elif (num_col<5):
                print "Wrong num cols: " + str(num_col)

            scores = []
            score = []
            for q, q_score in enumerate(q_scores.find_all('td')):
                if (q % (num_col+1))==0:
                    if (q==0):
                        Away_Tm = q_score.children.next().children.next()
                    else:
                        Home_Tm = q_score.children.next().children.next()
                        scores.append( score )
                        score = []
                    score.append( q_score.children.next().children.next() )
                else:
                    score.append( int(q_score.children.next()) )
            scores.append( score )
            scores = DataFrame(scores, columns=scores_col)
            break

    return(scores, Away_Tm, Home_Tm)

def get_box_score(box_score_data, Home_Tm, Away_Tm):
    basic = []
    advanced = []
    for box_score_datum in box_score_data:
        if "id" in box_score_datum.attrs.keys():
            if box_score_datum.attrs["id"] in (Away_Tm+'_basic', Away_Tm+'_advanced', Home_Tm+'_basic', Home_Tm+'_advanced'):
                colspan = int( box_score_datum.tr.th.find_next().attrs["colspan"] ) + 1

                # extract headers
                headers = box_score_datum.tr.find_next().find_next().find_next()
                headers_th = headers.th
                cols = []
                for c in range(colspan):
                    cols.append( str(headers_th.children.next()) )
                    if cols[c]=='Starters':
                        cols[c] = 'Players'
                    headers_th = headers_th.find_next()

                # extract data
                row = []
                rows = []
                e = 1
                for box_score_datum_td in box_score_datum.find_all('td'):
                    if len(box_score_datum_td.contents)>0:
                        try:
                            element = box_score_datum_td.children.next().children.next()
                        except:
                            element = box_score_datum_td.contents[0]
                    else:
                        element = ''
                    row.append( element )

                    if box_score_datum_td.attrs.has_key('colspan'):
                        for c in range(int(box_score_datum_td.attrs["colspan"])-1):
                            row.append( ' ' )
                            e += 1
                    if (e % colspan)==0:
                        rows.append( row )
                        row = []
                    e += 1

                box_score = DataFrame(rows, columns=cols)
                box_score['Tm'] = box_score_datum.attrs["id"][:3]

                if box_score_datum.attrs["id"][4:]=='basic':
                    basic.append( box_score )
                else:
                    advanced.append( box_score )
    return (pd.concat(basic), pd.concat(advanced))

def set_dir_struct(year):
    if os.path.isdir('Data')==False:
        os.mkdir('Data')

    if os.path.isdir('Data/Box_Scores')==False:
        os.mkdir('Data/Box_Scores')

    if os.path.isdir('Data/Box_Scores/' + year)==False:
        os.mkdir('Data/Box_Scores/' + year)

    if os.path.isdir('Data/Box_Scores/' + year + '/Box')==False:
        os.mkdir('Data/Box_Scores/' + year + '/Box')

    if os.path.isdir('Data/Box_Scores/' + year + '/Scores')==False:
        os.mkdir('Data/Box_Scores/' + year + '/Scores')

def pull_box_scores(year, mod_print, sleep_secs):
    Games = Get_Games(year)
    Games_df = DataFrame(Games, columns=['Date', 'box_url', 'Away', 'Away_PTS', 'Home', 'Home_PTS'])
    Games_df.to_csv('Data/Box_Scores/' + year + '/Game_List_' + year + '.csv', index=False)

    set_dir_struct(year)

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

    print ("Reading " + str(len(Games)) + " games.")
    for g, Game in enumerate(Games):
        if (g % mod_print)==0:
            print ("Starting game " + str(g))

        #Game = Games[1230]
        Date = str(pd.to_datetime(Game[0]).date())
        box_url = Game[1]
        if box_url!=' ':
            Away = Game[2]
            Away_PTS = Game[3]
            Home = Game[4]
            Home_PTS = Game[5]

            Away_Tm = team_nm[Away]
            Home_Tm = team_nm[Home]

            if (os.path.isfile('Data/Box_Scores/' + year + '/Scores/SQ_' + Date + '_' + Away_Tm + '_' + Home_Tm + '.csv')==False):
                url = 'http://www.basketball-reference.com' + box_url
                r = requests.get(url)
                box_score_page = BeautifulSoup(r.text)
                box_score_data = box_score_page.find_all('table')
                time.sleep(sleep_secs)

                scores, Away_Tm, Home_Tm = parse_score_by_q(box_score_data)
                scores.to_csv('Data/Box_Scores/' + year + '/Scores/SQ_' + Date + '_' + Away_Tm + '_' + Home_Tm + '.csv', index=False)

                basic, advanced = get_box_score(box_score_data, Home_Tm, Away_Tm)
                basic.to_csv('Data/Box_Scores/' + year + '/Box/BS_' + Date + '_' + Away_Tm + '_' + Home_Tm + '.csv', index=False)
                advanced.to_csv('Data/Box_Scores/' + year + '/Box/AS_' + Date + '_' + Away_Tm + '_' + Home_Tm + '.csv', index=False)

if __name__=='__main__':

    ## Set Parameters
    year = '2016'  # year to pull box scores
    mod_print = 25 # when to print to which game is being processed
    sleep_secs = 3 # seconds between pull requests

    pull_box_scores(year, mod_print, sleep_secs)


