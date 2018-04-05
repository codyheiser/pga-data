# Scrape historical data from the PGA Tour website

import numpy as np
import pandas as pd
import json
import requests

def tourney(course_ID, year):
	'''
	Pull scores from all players of a tournament
	course_ID = course number as designated by PGA
	year = year of tournament to grab data from
	'''
	tourn = requests.get('http://www.pgatour.com/data/R/{}/{}/tournsum.json'.format(course_ID, year)).json() # load JSON for tournament and year specified
	data = tourn['years'][0]['tours'][0]['trns'][0] # ignore extraneous metadata for now, get straight to the meat

	out = {'RoundNum':[], 'CourseID':[], 'RoundPos':[], 'RoundScore':[], 'PlayerID':[], 'Year':[], 'PlayerName':[]} # initialize dictionary for dumping info into

	for player in data['plrs']:
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

def course_info(year):
    '''
    Pull course information into DataFrame
    year = year to grab data from
    '''
    out = {'CourseName':[], 'CourseID':[], 'TournName':[]} # initialize dictionary for dumping info into
    
    # check all possible course numbers, given that they are 3-digit numbers
    for course in ['%03d' % (x,) for x in range(101)]:
        try:
            tourn = requests.get('http://www.pgatour.com/data/R/{}/{}/tournsum.json'.format(course, year)).json() # load JSON for course and year specified
            data = tourn['years'][0]['tours'][0]['trns'][0] # ignore extraneous metadata for now, get straight to the meat
            out['CourseName'].append(data['courses'][0]['courseName'])
            out['CourseID'].append(data['courses'][0]['courseNum'])
            out['TournName'].append(data['fullName'])
            print('loading data from course #' + course)
            
        except:
            print(course + ' is not a valid course ID')
        
    return pd.DataFrame(out)

def player(PlayerName, year):
    '''
    Pull scores from all tournaments for a single player
    PlayerName = first and last name of player
    year = year of to grab data from
    '''
    out = {'RoundNum':[], 'CourseID':[], 'RoundPos':[], 'RoundScore':[], 'PlayerID':[], 'Year':[], 'PlayerName':[]} # initialize dictionary for dumping info into
    
    for CourseID in course_info(year)['CourseID']: # get course IDs for all tournaments in given year
        tourn = requests.get('http://www.pgatour.com/data/R/{}/{}/tournsum.json'.format(CourseID, year)).json() # load JSON for course and year specified
        data = tourn['years'][0]['tours'][0]['trns'][0]['plrs'] # ignore extraneous metadata for now, get straight to the meat
        
        for rnd in data if data['name']['first'] + ' ' + data['name']['last'] == PlayerName:
            out['Year'].append(year)
            out['PlayerName'].append(PlayerName)
            out['PlayerID'].append(data['plrNum'])
            out['RoundNum'].append(rnd['rndNum'])
            out['CourseID'].append(rnd['courseNum'])
            out['RoundPos'].append(rnd['rndPos'])
            out['RoundScore'].append(rnd['rndScr'])
            
    return pd.DataFrame(out)

