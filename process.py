#! /usr/bin/python3

# all kinds of basic analytics are run from here and stored
# in states array and summary dictionary.

# call analyze below to generate all the data

# state_positives - builds data related to state dailt detected cases
# analyze - calls all the other analysis modules and builds the summary
# record

# By Nenad Rijavec
# Feel free to use, share or modify as you see fit.

import json
import sys
import datetime
import math
import matplotlib
import matplotlib.pyplot as plt
import operator
from matplotlib.backends.backend_pdf import PdfPages
from parse_data import parse_latest, load_json_file

# smoothing parameters - number of days
support = 7	# positives and tests
support_d1 = 3	# d1 - number of new cases
support_d2 = 3	# d2 - rate of change in new cases
support_d3 = 3	# d3 - acceleration of the rate of change in new cases

active_period = 21 # we assume infections in last this many days are
		   # still active


def parse_actions( states, actions ):
	statectr = 0
	state_len = len(states)
	for action in actions:
		while not action['state'] == states[statectr]['state']:
			statectr += 1
			if statectr == state_len:
				break
		if statectr == state_len:
			print( 'ERROR: no state ', action['state'] )
			return
		basedate =((states[statectr]['data'])[states[statectr]['n_samples']-1])['date']
		currdate = action['date']
		states[statectr]['actions'].append( [ (datetime.date.fromisoformat(\
                	currdate[0:4]+'-'+currdate[4:6]+'-'+currdate[6:8])- \
			basedate).days, action['action'] ] )

def smooth_series( smoothed, support, vals, days, n_samples):
	for i in range(support):
		smoothed[i] = vals[i]
	low = 0
	for curr in range( support, n_samples ):
		while days[curr] - days[low] > 7:
			low += 1
		sum = 0
		n = 0
		for i in range(low, curr+1):
			n += 1
			sum += vals[i]
		smoothed[curr] = sum/n

def state_positives(state):
	datalen = len(state['data'])
	# skip to first date with positive case
	first = datalen-1 ;
	while first>0 and ((state['data'])[first])['positive']==0:
		first -= 1
	n_samples = first + 1

	state['days'] = [0]*n_samples
	days = state['days']
	state['positives'] = [0]*n_samples
	vals = state['positives'] 
	state['basedate'] =((state['data'])[n_samples-1])['date']
	for day in range(0,n_samples):
		days[day] = \
			(((state['data'])[n_samples-day-1])['date']-\
				state['basedate']).days
		vals[day] = ((state['data'])[n_samples-day-1])['positive']
		if vals[day] == None :
			vals[day] = vals[day-1]
		else:
			vals[day] /=(state['pop']/1000000)
	if vals[n_samples-1] == 0 :
		state['have_covid'] = False
		state['n_samples'] = 0
		print( 'no cases in ' + state['name'] )
	else:
		state['have_covid'] = True
		state['n_samples'] = n_samples
		state['smoothed_pos'] = [0]*(n_samples)
		state['active'] = [0]*(n_samples)
		smoothed = state['smoothed_pos']
		active = state['active']
		# first and second derivative
		state['pos_d1'] = [0]*n_samples
		state['pos_d2'] = [0]*n_samples
		state['pos_d3'] = [0]*n_samples
		d1 = state['pos_d1']
		d2 = state['pos_d2']
		d3 = state['pos_d3']
		wrk = [0]*n_samples
		# smoothed positives
		smooth_series( smoothed, support, vals, days, n_samples)
		# actives, smoothed from positives
		for i in range(active_period) :
			wrk[i] = vals[i]
		for i in range(active_period,n_samples):
			wrk[i] = vals[i] - vals[i-active_period]
		smooth_series( active, support, wrk, days, n_samples)
		# first derivative of smoothed positives
		for i in range(1,n_samples):
			wrk[i] = (smoothed[i]-smoothed[i-1])/(days[i]-days[i-1])
		smooth_series( d1, support_d1, wrk, days, n_samples)
		# second derivative of smoothed positives
		wrk[1] = 0
		for i in range(2,n_samples):
			wrk[i] = (d1[i]-d1[i-1])/(days[i]-days[i-1])
		smooth_series( d2, support_d2, wrk, days, n_samples)
		# third derivative of smoothed positives
		wrk[1] = 0
		for i in range(2,n_samples):
			wrk[i] = (d2[i]-d2[i-1])/(days[i]-days[i-1])
		smooth_series( d3, support_d3, wrk, days, n_samples)

# must be called *after* state positives
def state_tested(state):
	n_samples = state['n_samples']
	if n_samples == 0:
		return
	datalen = len(state['data'])

	days = state['days']
	state['negatives'] = [0]*n_samples
	state['tested'] = [0]*n_samples
	vals = state['negatives']
	tested = state['tested']
	positives = state['positives']
	negatives = state['negatives']
	for day in range(0,n_samples):
		negatives[day] = ((state['data'])[n_samples-day-1])['negative']
		if negatives[day] == None :
			negatives[day] = negatives[day-1]
		else:
			negatives[day] /=(state['pop']/1000000)
		tested[day] = positives[day] + negatives[day]
#	if state['name'] == 'Georgia' :
#		print( 'negatives' )
#		print( negatives )
#		print( 'positives' )
#		print( positives )
#		print( 'tested' )
#		print( tested )
	for day in range(n_samples-1,1,-1):
		tested[day] -= tested[day-1]
	# smooth tested
	state['smoothed_tested'] = [0]*(n_samples)
	smoothed = state['smoothed_tested']
	smooth_series( smoothed, support, tested, days, n_samples)
	# fraction positive
	state['frac_positive'] = [0]*n_samples
	frac = state['frac_positive']
	for day in range(1,n_samples):
		if tested[day] > 0:
			frac[day] = (positives[day] - positives[day-1])/\
				tested[day]
		else:
			frac[day] = 0
	# smooth frac
	state['smoothed_frac'] = [0]*(n_samples)
	smoothed = state['smoothed_frac']
	smooth_series( smoothed, support, frac, days, n_samples)

# compute trend data
def trends(state):
	n_samples = state['n_samples']
	if n_samples == 0:
		return
	pos = state['positives'][n_samples-1]
	d1 = state['pos_d1'][n_samples-1]
	d2 = state['pos_d2'][n_samples-1]
	d3 = (d2 - state['pos_d2'][n_samples-3])/2
	state['days_to_double'] = dict()
	dd = state['days_to_double']
	dd['pos'] = pos/d1
	if d2 > 0:
		dd['d1'] = d1/d2
	else:
		dd['d1'] = -1
	delta = d1*d1 + 4 * d2 * pos
	if delta >= 0:
		dd['model'] = (-d1 + math.sqrt(delta))/(2*d2)
	else:
		dd['model'] = -1


def analyze(states) :
	for state in states:
		state_positives(state)
		state_tested(state)
		trends(state)
	# remove any states with no cases
	n_states = len(states)
	ctr = 0
	while ctr < n_states :
		state = states[ctr]
		if not state['have_covid'] :
			n_states -= 1
			#print( 'removing ' + state['name'])
			states.pop(ctr)
		else:
			ctr +=1

	# uncomment to parse actions
	# sample actions.json format
	#{"name": "Alaska", "state": "AK", "date": "20200328", "action": "close"}
	#{"name": "Alaska", "state": "AK", "date": "20200424", "action": "open"}

	#actions = list()
	#ff = load_json_file('actions.json', actions)
	#actions.sort(key = lambda i: i['state'])
	#parse_actions( states, actions )

	# build various global arrays and values
	summary = dict()
	summary['active_states'] = n_states
	# array of positives per M, lowest to highest
	wrkdict = dict()
	for state in states:
		wrkdict[state['name']] = \
			state['positives'][state['n_samples']-1]
	summary['positives'] = \
		dict( sorted(wrkdict.items(), key=operator.itemgetter(1)))
	# array of new daily positives per M, lowest to highest
	wrkdict = dict()
	for state in states:
		wrkdict[state['name']] = \
			state['pos_d1'][state['n_samples']-1]
	summary['pos_d1'] = \
		dict( sorted(wrkdict.items(), key=operator.itemgetter(1)))
	# array of rate of growth new daily positives per M, lowest to highest
	wrkdict = dict()
	for state in states:
		wrkdict[state['name']] = \
			state['pos_d2'][state['n_samples']-1]
	summary['pos_d2'] = \
		dict( sorted(wrkdict.items(), key=operator.itemgetter(1)))
	# array of accel of rate of growth new daily positives per M, lowest to highest
	wrkdict = dict()
	for state in states:
		wrkdict[state['name']] = \
			state['pos_d3'][state['n_samples']-1]
	summary['pos_d3'] = \
		dict( sorted(wrkdict.items(), key=operator.itemgetter(1)))
	# max values
	max_d1 = 0
	max_d1_date = None
	max_d1_state = None
	for state in states:
		max = 0
		max_d = None
		for day in range( state['n_samples'] ):
			if state['pos_d1'][day] > max:
				max = state['pos_d1'][day] 
				max_d = day
		if max > max_d1:
			max_d1 = max
			max_d1_state = state['name']
			max_d1_date = state['basedate'] + \
					datetime.timedelta( max_d )
	summary['max_d1'] = max_d1
	summary['max_d1_date'] = max_d1_date
	summary['max_d1_state'] = max_d1_state
				
	return(summary)

		
