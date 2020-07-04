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
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib import enums
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# sorting functions for state trend table
# though output mostly as ints, values are floats, so no need to worry 
# about ties
def sort_pos(state):
	return state['positives'][state['n_samples']-1]

def sort_active(state):
	return state['active'][state['n_samples']-1]

def sort_d1(state):
	return state['pos_d1'][state['n_samples']-1]

def sort_d2(state):
	return state['pos_d2'][state['n_samples']-1]

def sort_d3(state):
	return state['pos_d3'][state['n_samples']-1]

def sort_dpos(state):
	val = state['days_to_double']['pos']
	if val == -1:
		return 99
	else:
		return val

def sort_dd1(state):
	val = state['days_to_double']['d1']
	if val == -1:
		return 99
	else:
		return val

def sort_dmodel(state):
	val = state['days_to_double']['model']
	if val == -1:
		return 99
	else:
		return val

def sort_amodel(state):
	val = state['days_to_double']['act']
	if val == -1:
		return 99
	else:
		return val

def sort_ddpos(state):
	return state['days_doubled']['pos']

def sort_ddact(state):
	return state['days_doubled']['act']

def sort_death(state):
	return  state['death'][state['n_samples']-1]

def sort_mort_pos(state):
	return state['death'][state['n_samples']-1]/state['positives'][state['n_samples']-1]

def sort_mort_pos14(state):
	return state['death'][state['n_samples']-1]/state['positives'][state['n_samples']-15]

def sort_mort_pop(state):
	return  state['death'][state['n_samples']-1]/10000

def single_trend_table( sorted, styles, elements, title, footnote ) :
	ptext = '<strong>%s</strong>' % title
	pp = Paragraph(title, styles['Title'])
	elements.append(pp)
	elements.append(Spacer(1, 10))
	data = [
		['', 'State', \
		'positives', \
		'active cases',
		'daily new',
		'daily new',\
		'daily new',\
		'days to double',\
		'',
		'',
		'days doubled',
		''],
		['', '', \
		'per million', \
		'per million',
		'per million',
		'rate of change',\
		'accel',\
		'pos',\
		'new',\
		'act',
		'pos',
		'act'],
	]
	ctr = 1
	for state in sorted:
		n_samples = state['n_samples']
		pos = state['positives'][n_samples-1]
		active = state['active'][n_samples-1]
		d1 = state['pos_d1'][n_samples-1]
		d2 = state['pos_d2'][n_samples-1]
		d3 = state['pos_d3'][n_samples-1]
		double_d = state['days_to_double']
		dd1 = int(double_d['d1'])
		if dd1 == -1:
			dd1str = 'N/A'
		else:
			dd1str = str(dd1)
		dmp = int(double_d['model'])
		if dmp == -1:
			dmpstr = 'N/A'
		else:
			dmpstr = str(dmp)
		#dmd = int(double_d['model'])
		dmd = int(double_d['act'])
		if dmd == -1:
			dmdstr = 'N/A'
		else:
			dmdstr = str(dmd)
			
		tabline = [ str(ctr), \
			state['name'], \
			str(int(pos)), \
			str(int(active)), \
			"{:,.2f}".format(d1),\
			"{:,.2f}".format(d2), \
			"{:,.2f}".format(d3), \
			dmpstr, \
			dd1str, \
			dmdstr,
			str(state['days_doubled']['pos']),\
			str(state['days_doubled']['act'])\
		]
		ctr += 1
		data.append(tabline)
	t=Table(data)
	t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
	('TEXTCOLOR',(1,2),(-1,-1),colors.red),
	('VALIGN',(0,0),(0,-1),'TOP'),
	('TEXTCOLOR',(0,0),(1,-1),colors.blue),
	('SPAN',(7,0),(9,0)),
	('SPAN',(10,0),(-1,0)),
	('ALIGN',(0,0),(-1,-1),'CENTER'),
	('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
	('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
	('LINEBEFORE', (0,0), (-1,1), 0.25, colors.black),
	('LINEABOVE', (6,1), (-1,1), 0.25, colors.black),
	('BOX', (0,0), (-1,-1), 0.25, colors.black),
	]))
	elements.append(t)
	if not footnote == '':
		elements.append(Spacer(1, 10))
		elements.append(Paragraph(footnote,styles['Normal']))
		
	elements.append(PageBreak())

def make_trend_report(states, fname ):

	sorted = list()  # used to sort on different criteria
	for state in states:
		sorted.append(state)

	mysize = (700,1250)

	doc = SimpleDocTemplate(fname, pagesize=mysize)
	doc.title = 'State trends report ' + str(datetime.date.today())
	doc.topMargin = 36

	elements = []

	styles=getSampleStyleSheet()
	NAnote = 'N/A - will never double under current trends'

	sorted.sort(key=sort_pos,reverse=True)
	single_trend_table( sorted, styles, elements, \
		'State trends by total positives', NAnote)

	sorted.sort(key=sort_active,reverse=True)
	single_trend_table( sorted, styles, elements, \
		'State trends by estimated active cases', NAnote)

	sorted.sort(key=sort_d1,reverse=True)
	single_trend_table( sorted, styles, elements, \
		'State trends by new cases', NAnote)

	sorted.sort(key=sort_d2,reverse=True)
	single_trend_table( sorted, styles, elements, \
		'State trends by by new case growth', NAnote)

	sorted.sort(key=sort_d3,reverse=True)
	single_trend_table( sorted, styles, elements, \
		'State trends by by new case growth acceleration', NAnote)

	sorted.sort(key=sort_dd1)
	single_trend_table( sorted, styles, elements, \
		'State trends by days to double new cases', NAnote)

	sorted.sort(key=sort_dmodel)
	single_trend_table( sorted, styles, elements, \
		'State trends by days to double total positives', \
		NAnote)

	sorted.sort(key=sort_amodel)
	single_trend_table( sorted, styles, elements, \
		'State trends by days to double active cases', \
		NAnote)

	sorted.sort(key=sort_ddpos)
	single_trend_table( sorted, styles, elements, \
		'State trends by days last doubling of total positives',\
			NAnote)

	sorted.sort(key=sort_ddact)
	single_trend_table( sorted, styles, elements, \
		'State trends by days for last doubling of active cases',\
			NAnote)

	# write the document to disk
	doc.build(elements)

def single_mortality_table( sorted, styles, elements, title, footnote ) :
	ptext = '<strong>%s</strong>' % title
	pp = Paragraph(title, styles['Title'])
	elements.append(pp)
	elements.append(Spacer(1, 10))
	data = [ \
		['', 'State', \
		'positives', \
		'active cases', \
		'deaths', \
		'mortality rate %',\
		'', \
		''], \
		['', '', \
		'per million', \
		'per million', \
		'per million', \
		'infected', \
		'infected-14', \
		'population' ] \
	]
	ctr = 1
	for state in sorted:
		n_samples = state['n_samples']
		pos = state['positives'][n_samples-1]
		active = state['active'][n_samples-1]
		death = state['death'][n_samples-1]
		pop = state['pop']
			
		tabline = [ str(ctr), \
			state['name'], \
			str(int(pos)), \
			str(int(active)), \
			str(int(death)), \
			"{:,.2f}".format(100*death/state['positives'][n_samples-1]),\
			"{:,.2f}".format(100*death/state['positives'][n_samples-15]),\
			"{:,.3f}".format(death/10000),\
		]
		ctr += 1
		data.append(tabline)
	t=Table(data)
	t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
	('TEXTCOLOR',(1,2),(-1,-1),colors.red),
	('VALIGN',(0,0),(0,-1),'TOP'),
	('TEXTCOLOR',(0,0),(1,-1),colors.blue),
	('SPAN',(5,0),(-1,0)),
	('ALIGN',(0,0),(-1,-1),'CENTER'),
	('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
	('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
	('LINEBEFORE', (0,0), (-1,1), 0.25, colors.black),
	('LINEABOVE', (5,1), (-1,1), 0.25, colors.black),
	('BOX', (0,0), (-1,-1), 0.25, colors.black),
	]))
	elements.append(t)
	if not footnote == '':
		elements.append(Spacer(1, 10))
		elements.append(Paragraph(footnote,styles['Normal']))
		
	elements.append(PageBreak())

def make_mortality_report(states, fname ):

	sorted = list()  # used to sort on different criteria
	for state in states:
		sorted.append(state)

	mysize = (700,1250)

	doc = SimpleDocTemplate(fname, pagesize=mysize)
	doc.title = 'State mortality report ' + str(datetime.date.today())
	doc.topMargin = 36

	elements = []

	styles=getSampleStyleSheet()
	NAnote = ''

	sorted.sort(key=sort_death,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by total deaths', NAnote)

	sorted.sort(key=sort_mort_pos,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by infected mortality rate', NAnote)

	sorted.sort(key=sort_mort_pos14,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by infected mortality rate, 14 day delay', NAnote)

	sorted.sort(key=sort_mort_pop,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by population mortality rate', NAnote)


	# write the document to disk
	doc.build(elements)


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

# trend table for all states, sorted on each column
make_trend_report( states, 'trends.pdf' )

# mortality table for all states, sorted on each column
make_mortality_report( states, 'mortality.pdf' )

# state trend analysis
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
	pos = state['positives'][n_samples-1]
	d1 = state['pos_d1'][n_samples-1]
	d2 = state['pos_d2'][n_samples-1]
	double_d = state['days_to_double']
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

print( 'max number of new cases: ', int(summary['max_d1']), ' on ', \
	summary['max_d1_date'], ' in ', summary['max_d1_state'] )
print( 'max tests per million: ', int(summary['max_tpm']), ' on ', \
	summary['max_tpm_date'], ' in ', summary['max_tpm_state'] )
print( 'd2 min = ',"{:,.2f}".format(d2_min),' in ',d2_min_state)
print( 'd2 max = ',"{:,.2f}".format(d2_max),' in ',d2_max_state)
print( n_d2_pos, ' states with increasing rate' )
print( n_d2_neg, ' states with decreasing rate' )
print( n_d2_inc, ' states with accelerating rate' )
print( n_d2_dec, ' states with deccelerating rate' )

sys.exit(0)
