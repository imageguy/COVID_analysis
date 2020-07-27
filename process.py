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
support = 7	# positives
support_tst = 21	# tests
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
	state['tot_tested'] = [0]*n_samples
	vals = state['negatives']
	tested = state['tested']
	tot_tested = state['tot_tested']
	positives = state['positives']
	negatives = state['negatives']
	for day in range(0,n_samples):
		negatives[day] = ((state['data'])[n_samples-day-1])['negative']
		if negatives[day] == None :
			negatives[day] = negatives[day-1]
		else:
			negatives[day] /=(state['pop']/1000000)
		tot_tested[day] = positives[day] + negatives[day]
	for day in range(n_samples-1,1,-1):
		tested[day] = tot_tested[day] - tot_tested[day-1]
	# smooth tested
	state['smoothed_tested'] = [0]*(n_samples)
	smoothed = state['smoothed_tested']
	smooth_series( smoothed, support_tst, tested, days, n_samples)
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
	smooth_series( smoothed, support_tst, frac, days, n_samples)

def load_from_parsed(n_samples, pop, data, target, name):
	have_val = False
	for day in range(0,n_samples):
		target[day] = data[n_samples-day-1][name]
		if target[day] == None :
			if day == 0:
				target[day] = 0
			else:
				target[day] = target[day-1]
		else:
			target[day] /= pop
		if target[day] > 0.01:
			have_val = True
	return have_val


# must be called *after* state positives
# hospitalization, ICU, ventilators, mortality
def state_severe(state):
	n_samples = state['n_samples']
	if n_samples == 0:
		return
	datalen = len(state['data'])

	days = state['days']
	state['hosp'] = [0]*n_samples
	state['icu'] = [0]*n_samples
	state['vent'] = [0]*n_samples
	state['death'] = [0]*n_samples
	state['death_d1'] = [0]*n_samples
	state['death7'] = [0]*n_samples
	hosp = state['hosp']
	icu = state['icu']
	vent = state['vent']
	death = state['death']
	pop = state['pop']/1000000
	state['have_hosp'] = \
		load_from_parsed( n_samples, pop, state['data'], hosp, \
			'hospitalizedCurrently' )
	state['have_icu'] = \
		load_from_parsed( n_samples, pop, state['data'], icu, \
			'inIcuCurrently' )
	state['have_vent'] = \
		load_from_parsed( n_samples, pop, state['data'], vent, \
			'onVentilatorCurrently' )
	state['have_death'] = \
		load_from_parsed( n_samples, pop, state['data'], death, \
			'death' )
	wrk = state['death_d1']
	for i in range(1,n_samples):
			wrk[i] = (death[i]-death[i-1])/(days[i]-days[i-1])
	wrk = state['death7']
	for i in range(6,n_samples):
		wrk[i] = (death[i]-death[i-6])/7

# compute trend data
def trends(state):
	n_samples = state['n_samples']
	#print( state['name'])
	if n_samples == 0:
		return
	pos = state['positives'][n_samples-1]
	act = state['active'][n_samples-1]
	d1 = state['pos_d1'][n_samples-1]
	d2 = state['pos_d2'][n_samples-1]
	d3 = (d2 - state['pos_d2'][n_samples-3])/2
	state['days_to_double'] = dict()
	dd = state['days_to_double']
	if d1 > 0.09 :
		dd['pos'] = pos/d1
	else:
		dd['pos'] = -1
	if d2 > 0.009:
		dd['d1'] = d1/d2
	else:
		dd['d1'] = -1
	delta = d1*d1 + 4 * d2 * pos
	if delta >= 0 and d2 > 0.01:
		dd['model'] = (-d1 + math.sqrt(delta))/(2*d2)
	else:
		dd['model'] = -1
	dday = 0
	curr_act = act
	wrknew = state['pos_d1'][n_samples-active_period-1:n_samples]
	while curr_act < 2 * act:
		dday += 1
		curr_act -= wrknew[0]
		for i in range(active_period-1,1) :
			wrknew[i-1] = wrknew[i]
		delta = d1 + d2 * dday 
		if delta < 0 or (d2>-0.01 and d2 < 0.01):
			dday = -1
			break
		wrknew[active_period-1] = wrknew[active_period-2] + delta
		curr_act += wrknew[active_period-1]
	dd['act'] = dday
	state['days_doubled'] = dict()
	dd = state['days_doubled']
	i = 2
	while i < n_samples and pos < 2*state['positives'][n_samples-i]:
		i += 1
	dd['pos'] = i
	i = 2
	while i < n_samples and act < 2*state['active'][n_samples-i]:
		i += 1
	dd['act'] = i


# data normalized by number of tests. Called after global processing
# builds the global testing values.
# We build positives, actives, d1, d2 and d3 arrays normalized by the tests per
# global norm_tpm to make infection rates comparable among the states.
# We also build positives and actives normalized by the tests per million (tpm)
# rates on the normbase day to see the relation between the infection and test
# rates
def state_normalized(state,summary):
	n_samples = state['n_samples']
	normdays = summary['norm_days']
	norm_tpm = summary['max_tpm']
	normbase = n_samples - normdays
	state['normbase'] = normbase
	pos = state['positives']
	tpm = state['tot_tested']
	days = state['days']
	state['norm_pos'] = [0]*normdays
	state['norm_act'] = [0]*normdays
	state['norm_d1'] = [0]*normdays
	state['norm_d2'] = [0]*normdays
	state['norm_d3'] = [0]*normdays
	state['nloc_pos'] = [0]*normdays
	state['nloc_act'] = [0]*normdays
	npos = state['norm_pos']
	nact = state['norm_act']
	d1 = state['norm_d1']
	d2 = state['norm_d2']
	d3 = state['norm_d3']
	nlpos = state['nloc_pos']
	nlact = state['nloc_act']
	vals = [0]*normdays
	valsloc = [0]*normdays
	wrk = [0]*normdays
	# number of tests on any day might be zero, even with smoothing
	tt = tpm[normbase]
	day = normbase+1
	while tt == 0:
		tt = tpm[day]
		day += 1
	tpm_base = tt
	state['tpm_base'] = tpm_base # used for local normalization
	for day in range(normbase,n_samples):
		if not tpm[day] == 0:
			tt = tpm[day]
		vals[day-normbase] = norm_tpm * pos[day] / tt
		valsloc[day-normbase] = tpm_base * pos[day] / tt
	# smoothed positives
	smooth_series( npos, support, vals, days[normbase:], normdays)
	# actives, smoothed from positives
	for i in range(active_period) :
		wrk[i] = vals[i]
	for i in range(active_period,normdays):
		wrk[i] = vals[i] - vals[i-active_period]
	smooth_series( nact, support, wrk, days[normbase:], normdays)
	# first derivative of smoothed positives
	for i in range(1,normdays):
		wrk[i] = (npos[i]-npos[i-1])/(days[normbase+i] - \
			days[normbase+i-1])
	smooth_series( d1, support, wrk, days[normbase:], normdays)
	# second derivative of smoothed positives
	wrk[1] = 0
	for i in range(2,normdays):
		wrk[i] = (d1[i]-d1[i-1])/(days[normbase+i]-days[normbase+i-1])
	smooth_series( d2, support, wrk, days[normbase:], normdays)
	# third derivative of smoothed positives
	wrk[1] = 0
	for i in range(2,normdays):
		wrk[i] = (d2[i]-d2[i-1])/(days[normbase+i]-days[normbase+i-1])
	smooth_series( d2, support, wrk, days[normbase:], normdays)
	# data scaled to local base tpm. d1,d2,d3 are the same as for the
	# global normalization.
	smooth_series( nlpos, support, valsloc, days[normbase:], normdays)
	# actives, smoothed from positives
	for i in range(active_period) :
		wrk[i] = valsloc[i]
	for i in range(active_period,normdays):
		wrk[i] = valsloc[i] - valsloc[i-active_period]
	smooth_series( nlact, support, wrk, days[normbase:], normdays)
	

def analyze(states) :
	for state in states:
		state_positives(state)
		state_tested(state)
		state_severe(state)
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
	# max test per million rate
	max_tpm = 0
	max_tpm_date = None
	max_tpm_state = None
	for state in states:
		max = 0
		max_d = None
		for day in range( state['n_samples'] ):
			if state['tot_tested'][day] > max:
				max = state['tot_tested'][day] 
				max_d = day
		if max > max_tpm:
			max_tpm = max
			max_tpm_state = state['name']
			max_tpm_date = state['basedate'] + \
					datetime.timedelta( max_d )
	summary['max_tpm'] = max_tpm
	summary['max_tpm_date'] = max_tpm_date
	summary['max_tpm_state'] = max_tpm_state

	# per-state processing that depends on summary

	# we compute normalized data starting 5/1 - it's 5/2 here because we
	# don't process today's data
	normdays = (datetime.date.today() - datetime.date(2020,5,2)).days
	summary['norm_days'] = normdays
	for state in states:
		state_normalized(state,summary)
				
	return(summary)

		
