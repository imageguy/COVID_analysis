#! /usr/bin/python3

# gets the latest state-level cumulative data and puts it in latest.json
# each JSON record is output on a separate line. Parser requires 
# such formatting

# By Nenad Rijavec
# Feel free to use, share or modify as you see fit.

import sys
import requests
import json

r = requests.get('https://covidtracking.com/api/v1/states/daily.json' )

ff = open('./latest.json', 'w')
for dd in r.json():
	ff.write(json.dumps(dd))
	ff.write('\n')
ff.close()

sys.exit( 0 )
