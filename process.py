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
import matplotlib
import matplotlib.pyplot as plt
import operator
from matplotlib.backends.backend_pdf import PdfPages
from parse_data import parse_latest

# smoothing parameters - number of days
support = 7	# positives
support_d1 = 3	# d1 - number of new cases
support_d2 = 3	# d2 - rate of change in new cases
support_d3 = 3	# d3 - acceleration of the rate of change in new cases

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
		smoothed = state['smoothed_pos']
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

def analyze(states) :
	for state in states:
		state_positives(state)
	# remove any states with no cases
	n_states = len(states)
	ctr = 0
	while ctr < n_states :
		state = states[ctr]
		if not state['have_covid'] :
			n_states -= 1
			print( 'removing ' + state['name'])
			states.pop(ctr)
		else:
			ctr +=1
	for state in states:
		state_positives(state)
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
	return(summary)

		
