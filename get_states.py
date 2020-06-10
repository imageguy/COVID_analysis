#! /usr/bin/python3

# dumps JSON of US States and territories on stdout
# each has name, state abbreviation and population.
# territories other than Puerto Rico (including DC!) have pop=0
# capture in a file and add missing population numbers

import sys
import requests
import json

r = requests.get('https://covidtracking.com/api/v1/states/info.json' )

states = list()

for dd in r.json():
	states.append(dict( name=dd['name'],state=dd['state'], pop=0 ))


ff = open('./population2019.json')
lst= json.load(ff)['data']
ff.close


for curr in lst:
	for state in states:
		if state['name'] == curr['State']:
			state['pop'] = curr['Pop']

for state in states:
	print(json.dumps(state))


sys.exit( 0 )
