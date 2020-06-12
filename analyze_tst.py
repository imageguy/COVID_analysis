#! /usr/bin/python3

# usage: analyze_tst.py [-h] [-v] [-r N] [-o {pdf,png}] 
# makes pdf or png, pdf is default
# plots related to number of daily tests.
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


# plot tests
with PdfPages('tests.pdf') as pdf:
	for state in states:
		if args.o == 'pdf':
			outspec = pdf
		else:
			outspec = 'png/' + state['state'] + '_tst.png'
		plot_modules.plot_tested(state,n_days,outspec)

