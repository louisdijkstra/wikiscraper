#!/usr/bin/env python
from __future__ import print_function, division
from optparse import OptionParser
import os
import sys

# add the python directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))[:-3] + 'python')

from WikipediaScraper import *

__author__ = "Louis Dijkstra"

usage = """%prog <user> <output.csv>

	<user>			username of a specific Wikipedia user or a 
					file with a list of user names (every row a different
					title)
	<output.csv> 	output file location

Scrapes the top edits for the given users. The output is stored in CSV format 
(tab-delimited). It contains the following columns: 

	user          - the username 
	title         - title of the wikipedia page
	n_edits       - the number of edits that user made

"""

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

GET_DATA_SUCCESS = 1
GET_DATA_FAILURE = 0 

def printHeader(file): 
	print("user\ttitle\tn_edits", file=file)

def get_data(raw_data, name, file = sys.stdout): 
	"""
		Processes the raw data from the website and outputs 
		the data of interest
	"""

	raw_data = raw_data.splitlines() # split it in lines

	# go to the table of relevance
	i = 0 
	line = raw_data[i]
	while not 'TOP edits per namespace [hide]' in line: 
		i   += 1
		try: 
			line = raw_data[i]
		except: 
			return GET_DATA_FAILURE

	i += 5 # get to the starting point of the list

	line = raw_data[i]

	while len(line) != 0: # not the end of the table
		print(name, end='\t', file=file)
		n_edits = line.strip()
		i += 1
		line = raw_data[i]
		print(line.strip(), end='\t', file=file) # user name
		print(n_edits, file=file)
		i += 6
		line = raw_data[i]

	return GET_DATA_SUCCESS

def sleep(options): 
	if options.sleep != None: 
		time.sleep(options.sleep)
		if options.verbose: 
			print('Sleeping for %d seconds...'%options.sleep)

def main():

	parser = OptionParser(usage=usage)	
	parser.add_option("--file", "-f", action="store", dest="file", default=None, 
				  			help="A file with pages scraped already. When given, crawled users are not crawled again (Default: None)")
	parser.add_option("--sleep", "-s", action="store", dest="sleep", default=None, type=float, 
				  			help="Sleep time scraping two pages. (Default: no sleep)")
	parser.add_option("-v", action="store_true", dest="verbose", default=False, 
				  			help="verbose.")
	(options, args) = parser.parse_args()
	
	# process arguments
	if (len(args)!=2):
		parser.print_help()
		return 1

	# get the users to be scraped

	already_scraped = set()
	if options.file != None: 
		oldfile = open(options.file, 'r')
		next(oldfile) # ignore header
		for line in oldfile: 
			line = line.split('\t')
			already_scraped.add(line[0].strip())

	try: # in case a file is passed as the first argument
		userfile = open(args[0], 'r')
		users, links = [], [] 
		for username in userfile: 
			username = username.strip() 

			if username in already_scraped: 
				continue

			link_username = username.replace(' ', '%20') # replacing the spaces 

			link = "https://tools.wmflabs.org/xtools/topedits/?user=" + link_username + "&project=en.wikipedia.org&namespace=0&article="

			# add to the lists
			users.append(username)
			links.append(link)

	except: # in case just one title is given
		link_username = args[0].replace(' ', '%20') # replace the spaces
		users, links = [args[0]], ["https://tools.wmflabs.org/xtools/topedits/?user=" + args[0] + "&project=en.wikipedia.org&namespace=0&article="]

	outputfilename = args[1] 

	if options.verbose: # prints the list of pages to be scraped
		print("\nList of pages to be scraped:\n")
		print("username\t\tlink")
		print("--------\t\t----")
		for name, link in zip(users, links): 
			print("%s\t\t%s"%(name, link))
		print("---------\t\t----\n\n")

	i       = 0
	n_links = len(links)

	outputfile = open(outputfilename, 'w')
	printHeader(outputfile)

	list_names_failed = []

	# go through all the wikipedia links
	for name, link in zip(users, links): 

		if options.verbose: 
			i += 1
			print('%d of %d links processed (%.2f %%)\t%d of %d links failed (%.2f %%)'%(i, n_links, float(i) / float(n_links) * 100, len(list_names_failed), i, float(len(list_names_failed)) / float(i) * 100))
			print("Continuing with scraping %s (link: %s)"%(name, link))

		# get the raw data
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

		try: 
			data = readInDataFromURL(link, headers=USER_AGENT)
		except: 
			print("Couldn't process %s (link %s)"%(name, link))
			continue

		flag = get_data(data, name, file=outputfile)
		if flag == GET_DATA_FAILURE: 
			list_names_failed.append(name)

		sleep(options)
	
	if options.verbose: 
		print(" DONE")

	# print list of failed names: 

	print('\npages that failed:\n\n')
	for page in list_names_failed: 
		print(page)
	
if __name__ == '__main__':
	sys.exit(main())