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
	return  state['eff_death']

def sort_death7(state):
	return  state['death7'][state['n_samples']-1]

def sort_mort_pos(state):
	return state['eff_death']/state['eff_positives']

def sort_mort_newpos(state):
	return state['death7'][state['n_samples']-1]/state['pos_d1'][state['n_samples']-1]

def sort_mort_pop(state):
	return  state['eff_death']/10000

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

	datestr = str(datetime.date.today()-datetime.timedelta(days=1))

	doc = SimpleDocTemplate(fname, pagesize=mysize)
	doc.title = 'State trends report ' + datestr
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
		'daily deaths/mil', \
		'mortality rate %',\
		''], \
		['', '', \
		'per million', \
		'per million', \
		'per million', \
		'avg over last week', \
		'infected', \
		'newly infected' \
		 ] \
	]
	ctr = 1
	for state in sorted:
		n_samples = state['n_samples']
		pos = state['eff_positives']
		pos14 = state['eff_positives14']
		active = state['active'][n_samples-1]
		death = state['eff_death']
		death7 = state['death7'][n_samples-1]
		d1 = state['pos_d1'][n_samples-1]
		pop = state['pop']
			
		tabline = [ str(ctr), \
			state['name'], \
			str(int(pos)), \
			str(int(active)), \
			str(int(death)), \
			"{:,.2f}".format(death7),\
			"{:,.2f}".format(100*death/pos),\
			"{:,.2f}".format(100*death7/d1)\
		]
		ctr += 1
		data.append(tabline)
	t=Table(data)
	t.setStyle(TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
	('TEXTCOLOR',(1,2),(-1,-1),colors.red),
	('VALIGN',(0,0),(0,-1),'TOP'),
	('TEXTCOLOR',(0,0),(1,-1),colors.blue),
	('SPAN',(6,0),(-1,0)),
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

def make_mortality_report(states, fname ):

	sorted = list()  # used to sort on different criteria
	for state in states:
		sorted.append(state)
		state['eff_death'] = state['death'][state['n_samples']-1]
		state['eff_positives'] = \
			state['positives'][state['n_samples']-1]
		state['eff_positives14'] = \
			state['eff_positives'] - \
		(state['positives'][state['n_samples']-1] -\
			state['positives'][state['n_samples']-15])

	mysize = (700,1250)

	datestr = str(datetime.date.today()-datetime.timedelta(days=1))

	doc = SimpleDocTemplate(fname, pagesize=mysize)
	doc.title = 'State trends report ' + datestr
	doc.title = 'State mortality report ' + datestr
	doc.topMargin = 36

	elements = []

	styles=getSampleStyleSheet()
	NAnote = ''

	sorted.sort(key=sort_death,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by total deaths', NAnote)

	sorted.sort(key=sort_death7,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State daily mortality, by last 7 day average ', NAnote)

	sorted.sort(key=sort_mort_pos,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by infected mortality rate', NAnote)

	sorted.sort(key=sort_mort_newpos,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			'State mortality by newly infected mortality rate', NAnote)


	n_days=60
	for state in states:
		state['eff_death'] = state['death'][state['n_samples']-1] -\
			state['death'][state['n_samples']-(n_days+1)]
		state['eff_positives'] = \
		state['positives'][state['n_samples']-1] -\
			state['positives'][state['n_samples']-(n_days+1)]
		state['eff_positives14'] = \
			state['eff_positives'] - \
		(state['positives'][state['n_samples']-1] -\
			state['positives'][state['n_samples']-15])

	sorted.sort(key=sort_death,reverse=True)
	single_mortality_table(  sorted, styles, elements, \
			str(n_days) + ' day state mortality by deaths', NAnote)

	sorted.sort(key=sort_mort_pos,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			str(n_days) + ' day state mortality by infected mortality rate', NAnote)

	sorted.sort(key=sort_mort_newpos,reverse=True)
	single_mortality_table( sorted, styles, elements, \
			str(n_days) + ' day state mortality by newly infected mortality rate', NAnote)


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

datestr = str(datetime.date.today()-datetime.timedelta(days=1))

# trend table for all states, sorted on each column
make_trend_report( states, 'trends-' + datestr + '.pdf' )

# mortality table for all states, sorted on each column
make_mortality_report( states, 'mortality-' + datestr + '.pdf' )

# antibody analysis
sum_tot = 0
sum_pos = 0
n_have = 0
sum_pop = 0
sum_vpos = 0
sum_vtot = 0
for state in states :
	n_samp = state['n_samples']
	tta = state['data'][0]['totalTestsAntibody']
	pta = state['data'][0]['positiveTestsAntibody']
	nta = state['data'][0]['negativeTestsAntibody']
	ttpa = state['data'][0]['totalTestsPeopleAntibody']
	ptpa = state['data'][0]['positiveTestsPeopleAntibody']
	ntpa = state['data'][0]['negativeTestsPeopleAntibody']
	if tta != None and tta > 1000 and pta != None and pta > 0 :
		pop = state['pop']
		pos = state['positives'][n_samp-1] * pop / 1000000
		tot = pos + state['negatives'][n_samp-1] * pop / 1000000
		print( state['name'], ":", pop,\
			'viral population: ', "{:,.2f}".format(100*pos/pop)+'%', \
			'test:', "{:,.2f}".format(100*pos/tot)+'%', \
			' antibody :', "{:,.2f}".format(100*pta/tta)+'%' )
		n_have += 1
		sum_tot += tta
		sum_pos += pta
		sum_vpos += pos
		sum_vtot += tot
		sum_pop += pop
print( n_have, "states, total population:", sum_pop )
print(  "viral:", sum_vpos, \
	"tested:", "{:,.2f}".format(100*sum_vpos / sum_vtot)+'%', \
	"population:", "{:,.2f}".format(100*sum_vpos / sum_pop )+'%' )
print(  "antibody:", 
	"{:,.2f}".format(100*sum_pos / sum_tot )+'%' )


# state trend analysis
n_d2_pos = 0
n_d2_neg = 0
n_d2_inc = 0
n_d2_dec = 0
d2_max = 0 
d2_max_state = ''
d2_min = 0 
d2_min_state = ''
death_max = 0
death_max_state = ''

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
	dd1 = state['death7'][n_samples-1]
	if dd1 > death_max:
		death_max = dd1
		death_max_state = state['name']

print( 'max number of new cases: ', int(summary['max_d1']), ' on ', \
	summary['max_d1_date'], ' in ', summary['max_d1_state'] )
print( 'max tests per million: ', int(summary['max_tpm']), ' on ', \
	summary['max_tpm_date'], ' in ', summary['max_tpm_state'] )
print( 'd2 min = ',"{:,.2f}".format(d2_min),' in ',d2_min_state)
print( 'd2 max = ',"{:,.2f}".format(d2_max),' in ',d2_max_state)
print( 'max death average over last 7 days = ',"{:,.2f}".format(death_max), \
		' in ',death_max_state)
print( n_d2_pos, ' states with increasing rate' )
print( n_d2_neg, ' states with decreasing rate' )
print( n_d2_inc, ' states with accelerating rate' )
print( n_d2_dec, ' states with deccelerating rate' )

sys.exit(0)
