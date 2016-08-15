#!/usr/bin/env python
from __future__ import print_function, division
from optparse import OptionParser
import os
import sys

# add the python directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))[:-3] + 'python')

from WikipediaScraper import *

__author__ = "Louis Dijkstra"

usage = """%prog <title> <output.csv>

	<title>			title of the wikipedia page to be crawled or a 
					file with a list of titles (every row a different
					title)
	<output.csv> 	output file location

Scraps the users that made revisions to the Wikipedia pages whos title 
are given in the <title> argument. The output is stored in CSV format 
(tab-delimited). It contains the following columns: 

	name          - title of the page
	user          - the user name or ip that made a revision
	n_edits       - the total number of edits that user made
	n_minor_edits - the number of minor edits that user made
	first_edit    - the time of the first edit
	last_edit     - the time of the last edit 
	added_bytes   - the total number of bytes added

"""

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


GET_DATA_SUCCESS = 1
GET_DATA_FAILURE = 0 


def printHeader(file): 
	print("name\tuser\tn_edits\tn_minor_edits\tfirst_edit\tlast_edit\tadded_bytes", file=file)

def get_data(raw_data, name, file = sys.stdout): 
	"""
		Processes the raw data from the website and outputs 
		the data of interest
	"""

	raw_data = raw_data.splitlines() # split it in lines
	# print(raw_data)

	# go to the table of relevance
	i = 0 
	line = raw_data[i]
	while not 'Added (Bytes)' in line: 
		i   += 1
		try: 
			line = raw_data[i]
		except: 
			return GET_DATA_FAILURE

	i += 3 # get to the starting point of the list

	line = raw_data[i]

	while len(line) != 0: # not the end of the table

		print(name, end='\t', file=file)
		print(line.strip(), end='\t', file=file) # user name
		i += 5
		line = raw_data[i]
		print(line.strip(), end='\t', file=file) # number of edits
		i += 1
		line = raw_data[i]
		print(line.strip(), end='\t', file=file) # number of minor edits
		i += 2
		line = raw_data[i]
		print(line.strip(), end='\t', file=file) # first edit
		i += 1
		line = raw_data[i]
		print(line.strip(), end='\t', file=file) # last edit
		i += 2
		line = raw_data[i]
		print(line.strip().replace(',', ''), file=file) # added_bytes
		i += 3
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
				  			help="A file with pages scraped already. When given, scrawled page are not scrawled again (Default: None)")
	parser.add_option("--sleep", "-s", action="store", dest="sleep", default=None, type=float, 
				  			help="Sleep time scraping two pages. (Default: no sleep)")
	parser.add_option("--top", "-t", action="store", dest="top", default=10000, type=int, 
				  			help="Number of top users to be scraped. (Default: 10000)")
	parser.add_option("-v", action="store_true", dest="verbose", default=False, 
				  			help="verbose.")
	(options, args) = parser.parse_args()
	
	# process arguments
	if (len(args)!=2):
		parser.print_help()
		return 1

	# get the links to be scraped

	already_scraped = set()
	if options.file != None: 
		oldfile = open(options.file, 'r')
		next(oldfile) # ignore header
		for line in oldfile: 
			line = line.split()
			already_scraped.add(line[0].strip())

	try: # in case a file is passed as the first argument
		linkfile = open(args[0], 'r')
		names, links = [], [] 
		for name in linkfile: 
			name = name.strip() 

			if name in already_scraped: 
				continue

			link = "https://tools.wmflabs.org/xtools-articleinfo/?article=" + name.strip() + "&project=en.wikipedia.org&editorlimit=" + str(options.top) + "#topeditors"
			
			# add to the lists
			names.append(name)
			links.append(link)

	except: # in case just one title is given
		names, links = [args[0]], ["https://tools.wmflabs.org/xtools-articleinfo/?article=" + args[0] + "&project=en.wikipedia.org&editorlimit=" + str(options.top) + "#topeditors"]

	outputfilename = args[1] 

	if options.verbose: # prints the list of pages to be scraped
		print("\nList of pages to be scraped:\n")
		print("title\t\tlink")
		print("-----\t\t----")
		for name, link in zip(names, links): 
			print("%s\t\t%s"%(name, link))
		print("-----\t\t----\n\n")

	i       = 0
	n_links = len(links)

	outputfile = open(outputfilename, 'w')
	printHeader(outputfile)

	list_names_failed = []

	# go through all the wikipedia links
	for name, link in zip(names, links): 

		if options.verbose: 
			i += 1
			print('%d of %d links processed (%.2f %%)\t%d of %d links failed (%.2f %%)'%(i, n_links, float(i) / float(n_links) * 100, len(list_names_failed), i, float(len(list_names_failed)) / float(i) * 100))
			print("Continuing with scraping %s (link: %s)"%(name, link))

		# get the raw data
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

		data = readInDataFromURL(link, headers=USER_AGENT)

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