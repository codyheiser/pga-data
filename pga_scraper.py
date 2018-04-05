# Scrape historical data from the PGA Tour website

import numpy as np
import pandas as pd
import json
import requests

def tourney(tourn_ID, year):
	'''
	Pull scores from all players of a tournament
	tourn_ID = tournament number as designated by PGA
	year = year of tournament to grab data from
	'''
	tourn = json.loads(requests.get('http://www.pgatour.com/data/R/{}/{}/tournsum.json'.format(tourn_ID, year))) # load JSON for tournament and year specified
	data = tourn['years'][0]['tours'][0]['trns'][0] # ignore extraneous metadata for now, get straight to the meat

	out = {'RoundNum':[], 'CourseID':[], 'RoundPos':[], 'RoundScore':[], 'PlayerID':[], 'Year':[], 'PlayerName':[]} # initialize dictionary for dumping info into

	for player in concisedata['plrs']:
    # save some stuff for later
    playername = player['name']['first'] + ' ' + player['name']['last']
    playerID = player['plrNum']
    for rnd in player['rnds']:
        out['Year'].append(year)
        out['PlayerName'].append(playername)
        out['PlayerID'].append(playerID)
        out['RoundNum'].append(rnd['rndNum'])
        out['CourseID'].append(rnd['courseNum'])
        out['RoundPos'].append(rnd['rndPos'])
        out['RoundScore'].append(rnd['rndScr'])

    return pd.DataFrame(out)
