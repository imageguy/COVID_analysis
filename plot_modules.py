#! /usr/bin/python3

# plotting modules
# output depends on the type of the third param:
# <class 'matplotlib.backends.backend_pdf.PdfPages'> : pdf.savefig()
# else, treat as filename to write PNG image to
# n_days gives how many last days to output. -1 is from the beginning


import json
import sys
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from parse_data import parse_latest
import process

pdftype= '<class \'matplotlib.backends.backend_pdf.PdfPages\'>'

# to center the state name (more or less)
def offset( name ):
	return( len(name)*0.005)

def plot_positives_save(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	ax = fig.add_subplot(1,1,1)
	if n_days == -1:
		start = 0
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	ax.set_ylabel( 'cases per million' )
	line, = ax.plot( state['days'][start:], state['positives'][start:],\
			label='raw')
	line, = ax.plot( state['days'][start:], state['smoothed_pos'][start:], \
			label='7 day running average')
	line, = ax.plot( state['days'][start:], state['active'][start:], \
			label='active cases')
	ax.legend()
	plt.title(state['name'])
	plt.figtext( 0.1, 0.05, 'first case on ' + \
		str(state['basedate']) + ', ' + \
		str((state['days'])[n_samples-1]+1) + ' days with cases, ' + \
		str(int(state['positives'][n_samples-1])) + ' cumulative cases per million' )

	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()

def plot_positives(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	ax = fig.add_subplot(1,1,1)
	if n_days == -1:
		start = 0
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	ax.set_ylabel( 'cases per million' )
	line, = ax.plot( state['days'][start:], state['positives'][start:],\
			label='raw')
	line, = ax.plot( state['days'][start:], state['smoothed_pos'][start:], \
			label='7 day running average')
	axd2 = ax.twinx()
	color = 'tab:red'
	axd2.set_ylabel( 'active cases', color=color )
	axd2.tick_params(axis='y', labelcolor=color )
	line2, = axd2.plot( state['days'][start:], state['active'][start:], \
			label='active cases', color=color )
	plt.title(state['name'])
	plt.figtext( 0.1, 0.05, 'first case on ' + \
		str(state['basedate']) + ', ' + \
		str((state['days'])[n_samples-1]+1) + ' days with cases, ' + \
		str(int(state['positives'][n_samples-1])) + ' cumulative cases per million' )

	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()


def plot_derivatives(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	ax = fig.add_subplot(1,1,1)
	color = 'tab:blue'
	if n_days == -1:
		start = 8
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	ax.set_ylabel( 'daily new cases per million', color=color )
	ax.tick_params(axis='y', labelcolor=color )
	line1, = ax.plot( state['days'][start:], state['pos_d1'][start:],\
			color=color, \
			label='new daily cases')
	axd2 = ax.twinx()
	color = 'tab:red'
	axd2.set_ylabel( 'daily new cases per million rate of change', color=color )
	axd2.tick_params(axis='y', labelcolor=color )
	line2, = axd2.plot( state['days'][start:], state['pos_d2'][start:], \
			label='new daily cases change', color=color)
	line3, =axd2.plot( state['days'][start:], [0]*(n_samples-start), color='black')
	line3.set_dashes([10,10])
	plt.title(state['name'])
	plt.figtext( 0.1, 0.05, 'first case on ' + \
		str(state['basedate']) + ', ' + \
		str((state['days'])[n_samples-1]+1) + ' days with cases, ' + \
		str(int(state['positives'][n_samples-1])) + ' cumulative cases per million' )

	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()

def plot_combined(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	plt.figtext( 0.5-offset(state['name']),0.95, state['name'], size='xx-large' )
	ax = fig.add_subplot(211)
	color = 'blue'
	if n_days == -1:
		start = 0
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	normbase = state['normbase']
	normstart = 0
	if normbase < start:
		normstart = start - normbase 
		normbase = start
	ax.set_ylabel( 'cases per million' )
	line, = ax.plot( state['days'][start:], state['positives'][start:],\
			label='raw')
	line, = ax.plot( state['days'][start:], state['smoothed_pos'][start:], \
			label='7 day running average', color=color)
#	line, = ax.plot( state['days'][start:], state['active'][start:], \
#			label='active cases', color='orange')
	axd2 = ax.twinx()
	color = 'tab:orange'
	axd2.set_ylabel( 'active cases', color=color )
	axd2.tick_params(axis='y', labelcolor=color )
	line2, = axd2.plot( state['days'][start:], state['active'][start:], \
			label='active cases', color=color )
#	line, = ax.plot( state['days'][normbase:], \
#			state['norm_pos'][normstart:], \
#			label='normalized total', linestyle=':', color=color)
#	line, = ax.plot( state['days'][normbase:], \
#			state['nloc_act'][normstart:], \
#			label='normalized active', \
#			linestyle=':', color='orange')
	# uncomment parsing in parse_latest to get the data
	for act in state['actions']:
		if act[1] == 'close' :
			ax.axvline(act[0], color='red', dashes=[10,10])
		else:
			ax.axvline(act[0], color='green', dashes=[10,10])
		
	ax.legend()
	plt.title('cumulative number of cases')
	plt.figtext( 0.1, 0.45, 'first case on ' + \
		str(state['basedate']) + ', ' + \
		str((state['days'])[n_samples-1]+1) + ' days with cases, ' + \
		str(int(state['positives'][n_samples-1])) + ' cumulative cases per million' )
	ax1 = fig.add_axes([0.15, 0.1, 0.7, 0.3])
	if n_days == -1:
		start = 0
		ax1.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax1.set_xlabel( 'last '+str(n_days) + ' days' )
	color = 'tab:green'
	ax1.set_ylabel( 'daily new cases per million', color=color )
	ax1.tick_params(axis='y', labelcolor=color )
	line1, = ax1.plot( state['days'][start:], state['pos_d1'][start:],\
			color=color, \
			label='new daily cases')
	ax2=ax1.twinx()
	color = 'tab:red'
	ax2.set_ylabel( 'daily new cases per million rate of change', color=color )
	ax2.tick_params(axis='y', labelcolor=color )
	line2, = ax2.plot( state['days'][start:], state['pos_d2'][start:], \
			label='new daily cases change', color=color)
	line3, =ax2.plot( state['days'][start:], [0]*(n_samples-start), color='black')
	line3.set_dashes([10,10])
	for act in state['actions']:
		if act[1] == 'close' :
			ax2.axvline(act[0], color='red', dashes=[10,10])
		else:
			ax2.axvline(act[0], color='green', dashes=[10,10])
	plt.title('daily new cases and trend')
	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()

def plot_severe(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	plt.figtext( 0.5-offset(state['name']),0.95, state['name'], size='xx-large' )
	ax = fig.add_subplot(211)
	color = 'orange'
	if n_days == -1:
		start = 0
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	ax.set_ylabel( 'active cases per million' )
	lbl_artist = []
	lbl_tag = []
	line0, = ax.plot( state['days'][start:], state['active'][start:], \
			label='active',color=color)
	lbl_artist.append(line0)
	lbl_tag.append('active cases (left scale)')
	#ax.legend()
	ax2=ax.twinx()
	if state['have_hosp']:
		line1, = ax2.plot(state['days'][start:],state['hosp'][start:],\
				color='green')
		lbl_artist.append(line1)
		lbl_tag.append('currently hospitalized')
	if state['have_icu']:
		line2, = ax2.plot(state['days'][start:],state['icu'][start:],\
				color='blue')
		lbl_artist.append(line2)
		lbl_tag.append('currently in ICU')
	if state['have_vent']:
		line3, = ax2.plot(state['days'][start:],state['vent'][start:],\
				color='yellow')
		lbl_artist.append(line3)
		lbl_tag.append('currently on ventilator')
	if state['have_death']:
		line4, = ax2.plot(state['days'][start:],state['death'][start:],\
				color='red')
		lbl_artist.append(line4)
		lbl_tag.append('cumulative mortality')
	matplotlib.pyplot.legend( lbl_artist, lbl_tag )
	color = 'tab:red'
	ax2.set_ylabel( 'severe cases per million', color=color )
	ax2.tick_params(axis='y', labelcolor=color )
	plt.title('severe cases')
	plt.figtext( 0.1, 0.46, 'first case on ' + \
		str(state['basedate']) + ', ' + \
		str((state['days'])[n_samples-1]+1) + ' days with cases, ' + \
		str(int(state['positives'][n_samples-1])) + ' cumulative cases per million' )
	if not state['have_hosp'] or not state['have_icu'] or \
			not state['have_vent'] or not state['have_death']:
		outstr = 'missing from state data: '
		had_item = False
		if not state['have_hosp']:
			outstr += 'currently in hospital'
			had_item = True
		if not state['have_icu']:
			if had_item:
				outstr += ', '
			outstr += 'currently in ICU'
			had_item = True
		if not state['have_vent']:
			if had_item:
				outstr += ', '
			outstr += 'currently on ventilator'
			had_item = True
		if not state['have_death']:
			if had_item:
				outstr += ', '
			outstr += 'mortality'
		plt.figtext( 0.1, 0.44, outstr )

	ax3 = fig.add_axes([0.15, 0.1, 0.7, 0.3])
	if n_days == -1:
		start = 0
		ax3.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax3.set_xlabel( 'last '+str(n_days) + ' days' )
	color = 'tab:green'
	ax3.set_ylabel( 'cumulative cases per million', color=color )
	ax3.tick_params(axis='y', labelcolor=color )
	line1, = ax3.plot( state['days'][start:], state['positives'][start:],\
			color=color, \
			label='cumulative cases')
	ax4=ax3.twinx()
	color = 'tab:red'
	ax4.set_ylabel( 'mortality rate, percent, daily deaths/million', color=color )
	ax4.tick_params(axis='y', labelcolor=color )
	val = [0]*n_samples
	for i in range(n_samples):
		if state['death'][i] == 0:
			val[i] = 0
		elif state['positives'][i] == 0:
			val[i] = 0
		else:
			val[i] = 100*state['death'][i] / state['positives'][i]
	line2, = ax4.plot( state['days'][start:], val[start:], \
			label='cumulative mortality rate', color=color)
	line3, = ax4.plot( state['days'][start:], state['death_d1'][start:], \
			linestyle=':', label='daily deaths', color=color)
	line4, = ax4.plot( state['days'][start:], state['death7'][start:], \
			label='smoothed daily deaths', color="blue")
	matplotlib.pyplot.legend( (line1, line2, line3, line4),\
		('cumulative cases', 'cumulative mortality rate', \
		'raw daily deaths per million', \
		'smoothed daily deaths per million') )
	plt.title('mortality rate')
	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()


def plot_tested(state,n_days,outspec):
	if not state['have_covid']:
		return
	n_samples = state['n_samples']
	fig = plt.figure(figsize=(8,10))
	ax = fig.add_subplot(1,1,1)
	color = 'tab:blue'
	if n_days == -1:
		start = 8
		ax.set_xlabel( 'days since first case' )
	else:
		start = n_samples-n_days
		ax.set_xlabel( 'last '+str(n_days) + ' days' )
	ax.set_ylabel( 'tests per day per million', color=color )
	ax.tick_params(axis='y', labelcolor=color )

	line1, = ax.plot( state['days'][start:], state['smoothed_tested'][start:],\
			color=color, \
			label='new daily tests')
	axd2 = ax.twinx()
	color = 'tab:red'
	axd2.set_ylabel( 'daily percent positive tests', color=color )
	axd2.tick_params(axis='y', labelcolor=color )
	line2, = axd2.plot( state['days'][start:],  \
		[ int((1000*state['smoothed_frac'][i])/10) for i in \
			range(start,n_samples) ], \
			label='daily percent positive tests', color=color)
	plt.title(state['name'])
	plt.figtext( 0.1, 0.05, \
	'number of tests a day per million people, 7 day running average' )
	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()

def output_table(data, title, comment, col1, col2, outspec):
	fig = plt.figure(figsize=(8,8))
	ax = fig.add_subplot(1,1,1)
	ax.axis('tight')
	ax.axis('off')
	plt.title(title)
	n_states = len(data)
	tbl=[[0]*4 for i in range(n_states//2+1)]
	i = (n_states//2)-1
	tbl[i+1][2] = ' '
	tbl[i+1][3] = ' '
	k = 0
	offset=2
	for name,val in data.items():
		tbl[i][offset] = name
		tbl[i][offset+1] = "{:,.2f}".format(val)
		i -= 1
		k += 1
		if k > (n_states//2)-1 and offset == 2:
			offset = 0
			i = (n_states//2)
#	i = n_states-1
#	for name,val in summary['pos_d1'].items():
#		tbl[i][2] = name
#		tbl[i][3] = "{:,.2f}".format(val)
#		i -= 1
#	i = n_states-1
#	for name,val in summary['pos_d2'].items():
#		tbl[i][4] = name
#		tbl[i][5] = "{:,.2f}".format(val)
#		i -= 1
	tt = ax.table(\
		colLabels=( col1, col2, col1, col2 ),\
		cellText=tbl,loc='center' )
	plt.figtext( 0.2, 0.1, comment )
	outtype = str(type(outspec))
	if outtype == pdftype :
		outspec.savefig() # output spec is PDF back end
	else:
		# outspec is file for PNG output
		plt.savefig(outspec, format='png')
	plt.close()

