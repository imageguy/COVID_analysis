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

def plot_positives(state,n_days,outspec):
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


def plot_derivatives(state,n_days,outspec):
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

