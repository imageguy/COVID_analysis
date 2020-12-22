#! /usr/bin/python3

# each JSON record (data for a single state on a single day) is assumed to
# be on a single line.
# assume that 'latest.json' is sorted by reverse day and then state
# assume that states are sorted the same as states.json in latest.json
# we ignore today's data in latest.json, since they're probably incomplete
# parse_latest extracts relevant values from each record and populates the
# states array

import json
import sys
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from operator import itemgetter, attrgetter

def load_json_file( name, lst ):
	ff = open( name )
	for line in ff:
		lst.append(json.loads(line))
	ff.close()

def parse_day(raw):
	parsed = dict()
	datestr = str(raw['date'])
	parsed['date'] = datetime.date.fromisoformat(\
        	datestr[0:4]+'-'+datestr[4:6]+'-'+datestr[6:8])
	parsed['positive'] = raw['positive']
	parsed['negative'] = raw['negative']
	parsed['recovered'] = raw['recovered']
	parsed['death'] = raw['death']
	parsed['hospitalizedCurrently'] = raw['hospitalizedCurrently']
	parsed['inIcuCurrently'] = raw['inIcuCurrently']
	parsed['onVentilatorCurrently'] = raw['onVentilatorCurrently']
	if 'totalTestsAntibody' in raw.keys():
		parsed['totalTestsAntibody'] = raw['totalTestsAntibody']
	else :
		parsed['totalTestsAntibody'] = 0
	if 'positiveTestsAntibody' in raw.keys():
		parsed['positiveTestsAntibody'] = raw['positiveTestsAntibody']
	else :
		parsed['positiveTestsAntibody'] = 0
	if 'negativeTestsAntibody' in raw.keys():
		parsed['negativeTestsAntibody'] = raw['negativeTestsAntibody']
	else :
		parsed['negativeTestsAntibody'] = 0
	if 'totalTestsPeopleAntibody' in raw.keys():
		parsed['totalTestsPeopleAntibody'] = raw['totalTestsPeopleAntibody']
	else :
		parsed['totalTestsPeopleAntibody'] = 0
	if 'positiveTestsPeopleAntibody' in raw.keys():
		parsed['positiveTestsPeopleAntibody'] = raw['positiveTestsPeopleAntibody']
	else :
		parsed['positiveTestsPeopleAntibody'] = 0
	if 'negativeTestsPeopleAntibody' in raw.keys():
		parsed['negativeTestsPeopleAntibody'] = raw['negativeTestsPeopleAntibody']
	else :
		parsed['negativeTestsPeopleAntibody'] = 0
	#parsed[''] = raw['']
	return( parsed )

	#parsed[''] = raw['']
	return( parsed )

def parse_latest():
	states = list()
	ff = load_json_file('states.json', states)
	ff = load_json_file('us.json', states)

	latest = list()
	ff = load_json_file('latest.json', latest)

	for state in states:
		state['data'] = []
		state['actions'] = []

	today = datetime.date.today()
	last_day = None
	curr_state = 0
	n_states = len(states)-1
	for rec in latest:
		data = parse_day(rec)
		if not data['date'] == last_day:
			curr_state = 0
			last_day = data['date']
		# ignore today's data
		if not data['date'] == today:
			while not (states[curr_state])['state']==rec['state']\
					and curr_state < n_states:
				curr_state += 1
			if curr_state == n_states:
				print( "ERR: missing state ", rec['state'])
				sys.exit( 1 )
			((states[curr_state])['data']).append(data)
	
	latest_us = list()
	ff = load_json_file('latest_us.json', latest_us)
	last_day = None
	curr_state = len(states)-1
	for rec in latest_us:
		data = parse_day(rec)
		# ignore today's data
		if not data['date'] == today:
			((states[curr_state])['data']).append(data)
	return(states)

