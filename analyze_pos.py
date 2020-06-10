#! /usr/bin/python3

# usage: analyze_pos.py [-h] [-v] [-a {pos,d1d2,d3}] [-r N] [-o {pdf,png}] 
# makes pdf or png, pdf is default
# plots positives, first/second derivatives and third derivative. All by
# default, use -a to select
# -r N - plot last N days. All days are plotted if not specified.

# By Nenad Rijavec
# Feel free to use, share or modify as you see fit.

import json
import sys, getopt, argparse
import os
import math
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from parse_data import parse_latest
import process
import plot_modules


parser = argparse.ArgumentParser(description='analysis of number of cases')
parser.add_argument('-o', \
		choices=['pdf', 'png'],  \
		default='pdf', \
		nargs='?', \
		help='output type, pdf or png, default is pdf')
parser.add_argument('-a', \
		default='pos,d1d2,d3', \
		const='', \
		nargs='?', \
		help='list of analyses to run, default is pos,d1d2,d3')
parser.add_argument('-r', \
		type=int, \
		default=-1, \
		nargs='?', \
		help='how many last days to run, default is all' \
		)
parser.add_argument('-v', \
		action='store_true' ,\
		help='verbose')

args = parser.parse_args()

plot_days = -1
plot_positives = False
plot_derivatives = False
plot_d2_analysis = False
if args.a.find('pos') > -1:
	plot_positives = True
if args.a.find('d1d2') > -1:
	plot_derivatives = True
if args.a.find('d3') > -1:
	plot_d2_analysis = True
verbose = args.v
n_days = args.r
if verbose and n_days == -1:
	print('analyzing all data since first case')
elif verbose:
	print( 'analyzing last', str(n_days), 'days')
	
#sys.exit(0)

if args.o == 'pdf':
	matplotlib.use('pdf')
	if verbose:
		print( 'generating PDF' )
else:
	matplotlib.use('agg')
	if verbose:
		print( 'generating PNG' )

states = parse_latest()

# generate the numbers
summary = process.analyze(states)


# plot positives
if plot_positives:
	if verbose:
		print( 'generating positives plot')
	with PdfPages('positive.pdf') as pdf:
		for state in states:
			if args.o == 'pdf':
				outspec = pdf
			else:
				outspec = 'png/' + state['state'] + '_pos.png'
			plot_modules.plot_positives(state,n_days,outspec)
# plot derivatives
if plot_derivatives:
	if verbose:
		print( 'generating derivatives plot')
	with PdfPages('pos_d1d2.pdf') as pdf:
		for state in states:
			if args.o == 'pdf':
				outspec = pdf
			else:
				outspec = 'png/'+state['state']+'_pos_d1d2.png'
			plot_modules.plot_derivatives(state,n_days,outspec)

# d2 analysis
if plot_d2_analysis:
	if verbose:
		print( 'generating d2 analysis plot')
	with PdfPages('pos_d2_analysis.pdf') as pdf:
		n_d2_pos = 0
		n_d2_neg = 0
		n_d2_inc = 0
		n_d2_dec = 0
		d2_max = 0 
		d2_max_state = ''
		d2_min = 0 
		d2_min_state = ''
		fig = plt.figure(figsize=(8,10))
		ax = fig.add_subplot(1,1,1)
		ax.set_xlabel( 'last 15 days' )
		ax.set_ylabel( 'second derivative of cases per million' )
				
		for state in states:
			if state['have_covid'] :
				n_samples = state['n_samples']
				d2 = state['pos_d2']
				if d2[n_samples-1] > d2_max :
					d2_max = d2[n_samples-1]
					d2_max_state = state['name']
				if d2[n_samples-1] < d2_min :
					d2_min = d2[n_samples-1]
					d2_min_state = state['name']
				if d2[n_samples-1] > 0:
					n_d2_pos += 1
				else:
					n_d2_neg +=1
				delta = d2[n_samples-1] > d2[n_samples-3]
				if delta :
					n_d2_inc += 1
				else:
					n_d2_dec +=1
				line, = ax.plot( range(15),\
				d2[(n_samples-15):], \
						label=state['name'])
		plt.title('Second derivatives of positive cases per million')
		if args.o == 'pdf':
			pdf.savefig()
		else:
			plt.savefig('png/d2_summary.png', format='png')
		plt.close()

		print( 'd2 min = ',"{:,.2f}".format(d2_min),' in ',d2_min_state)
		print( 'd2 max = ',"{:,.2f}".format(d2_max),' in ',d2_max_state)
		print( n_d2_pos, ' states with increasing rate' )
		print( n_d2_neg, ' states with decreasing rate' )
		print( n_d2_inc, ' states with accelerating rate' )
		print( n_d2_dec, ' states with deccelerating rate' )
