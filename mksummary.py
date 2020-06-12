#! /usr/bin/python3

# usage: mksummary.py [-h] [-v] [-o {pdf png}]
# outputs summary data
# for now, PDF is single file (uncomment 'with' statements to split)
# png is one file per table

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
parser.add_argument('-v', \
		action='store_true' ,\
		help='verbose')

args = parser.parse_args()

verbose = args.v

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


# positives
with PdfPages('summary.pdf') as pdf:


	if args.o == 'pdf':
		outspec = pdf
	else:
		outspec = 'png/summ_pos.png'
	plot_modules.plot_tested(states[0], -1, outspec )
	plot_modules.output_table(summary['positives'],\
		'Cumulative number of cases per million, most to least',\
		'Raw (unsmoothed) data', \
		'State', '# cases', outspec)


# new cases
#with PdfPages('summ_d1.pdf') as pdf:
	if args.o == 'pdf':
		outspec = pdf
	else:
		outspec = 'png/summ_d1.png'
	plot_modules.output_table(summary['pos_d1'],\
		'Daily new number of cases per million, most to least',\
		'From smoothed data', \
		'State', '# new daily cases', outspec)

# rate increase
#with PdfPages('summ_d2.pdf') as pdf:
	if args.o == 'pdf':
		outspec = pdf
	else:
		outspec = 'png/summ_d2.png'
	plot_modules.output_table(summary['pos_d2'],\
		'Change rate of new cases per million, most to least',\
		'From smoothed data', \
		'State', '# new daily cases change', outspec)

# rate increase acceleration
#with PdfPages('summ_d3.pdf') as pdf:
	if args.o == 'pdf':
		outspec = pdf
	else:
		outspec = 'png/summ_d3.png'
	plot_modules.output_table(summary['pos_d3'],\
		'Acceleration of change rate of new cases per million, most to least',\
		'From smoothed data', \
		'State', 'change rate acceleration', outspec)


# state risk analysis
n_d2_pos = 0
n_d2_neg = 0
n_d2_inc = 0
n_d2_dec = 0
d2_max = 0 
d2_max_state = ''
d2_min = 0 
d2_min_state = ''



for state in states:
	n_samples = state['n_samples']
	d1 = state['pos_d1'][n_samples-1]
	d2 = state['pos_d2'][n_samples-1]
	if d2 > d2_max :
		d2_max = d2
		d2_max_state = state['name']
	if d2 < d2_min :
		d2_min = d2
		d2_min_state = state['name']
	if d2 > 0:
		n_d2_pos += 1
	else:
		n_d2_neg +=1
	delta = d2 > state['pos_d2'][n_samples-3]
	if delta :
		n_d2_inc += 1
	else:
		n_d2_dec +=1
	if d2 > 1.0:
		print(state['name'], \
		'	:	d1='+"{:,.2f}".format(d1),\
		'	:	d2='+"{:,.2f}".format(d2) )
		

print( 'd2 min = ',"{:,.2f}".format(d2_min),' in ',d2_min_state)
print( 'd2 max = ',"{:,.2f}".format(d2_max),' in ',d2_max_state)
print( n_d2_pos, ' states with increasing rate' )
print( n_d2_neg, ' states with decreasing rate' )
print( n_d2_inc, ' states with accelerating rate' )
print( n_d2_dec, ' states with deccelerating rate' )


sys.exit(0)
