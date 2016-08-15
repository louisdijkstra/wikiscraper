#!/usr/bin/env python
from __future__ import print_function, division
from optparse import OptionParser
import os
import sys
from IPy import IP

# add the python directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))[:-3] + 'python')

from WikipediaScraper import *

__author__ = "Louis Dijkstra"

usage = """%prog <input.csv> 

	<input.csv>		input file generated by scrape-users.py

Outputs a list of all unique users in the <input.csv>. 
See for filter options, the list below.
"""

def is_anonymized(username): 
	"""
		Returns True when the user is anonymous, otherwise False. 
	"""
	try: 
		IP(username)
		return True
	except: 
		return False

def is_bot(username): 
	"""
		Returns True when the user is a bot, otherwise False. 
	"""
	if 'bot' in username.lower(): 
		return True
	return False

def main():

	parser = OptionParser(usage=usage)	
	parser.add_option("--add-columns", action="store_true", dest="add_classification", default=False, 
				  			help="Adds the user classifications (bots/users) as a column")
	parser.add_option("--no-anonymized", action="store_true", dest="no_anonymized", default=False, 
				  			help="No anonymized users")
	parser.add_option("--no-bots", action="store_true", dest="no_bots", default=False, 
				  			help="No bots")
	parser.add_option("-m", action="store", dest="min", default=0, type=int, 
				  			help="Minimal number of revisions (Default: no threshold)")
	(options, args) = parser.parse_args()
	
	# process arguments
	if (len(args)!=1):
		parser.print_help()
		return 1

	inputfile = open(args[0], 'r')
	
	# ignore the header
	next(inputfile)

	users = set() # initialize user set

	for line in inputfile: 
		line     = line.split('\t')
		username = line[1].strip()
		n_edits  = int(line[2].strip())

		if options.no_bots: # check whether it's a bot
			if is_bot(username): 
				continue

		if n_edits < options.min: # sufficient edits
			continue

		if options.no_anonymized: # check whether its an ip address
			if is_anonymized(username): 
				continue

		users.add(username)

	if options.add_classification: 
		print('user\tbot\tip')
		for user in users: 
			print(user, end = '\t')

			if is_bot(user): 
				print('True', end = '\t')
			else: 
				print('False', end = '\t')

			if is_anonymized(user): 
				print('True')
			else: 
				print('False')
	else: 

		for user in users: 
			print(user)

	
if __name__ == '__main__':
	sys.exit(main())