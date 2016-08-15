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


def print_header(outputfile):
	"""
		Prints the header (column names) to a given output file
	"""
	print("name\tuser\tn_edits\tn_minor_edits\tfirst_edit\tlast_edit\tadded_bytes", file=outputfile)

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

def get_link(article_title, top_users = 10000):
	"""
		Returns the link to be scraped given the title of an article 
	
		Args:
			article_title - title of the article
			top_users - number of top contributors to be downloaded (Default: 10000)

	"""
	return "https://tools.wmflabs.org/xtools-articleinfo/?article=%s&project=en.wikipedia.org&editorlimit=%s#topeditors"%(
				article_title, 
				str(top_users)
			)

def main():

	parser = OptionParser(usage=usage)	
	parser.add_option("--attempts", "-a", action="store", dest="max_attempts", default=100, type=int, 
				  			help="Maximum number of attempts to scrape the given pages (Default: 100)")
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

	# process the list of articles 
	article_titles, links = [], [] # initialize

	if os.path.isfile(args[0]): # in case a file is passed as first argument
		with open(args[0], 'r') as inputfile:
			for article_title in inputfile: 
				article_title.strip() 
				article_title.replace(' ', '%20') # replace the spaces with %20 
				article_titles.append(article_title)
				links.append(get_link(article_title, top_users = options.top))
	else: # just one title given	
		article_titles.append( args[0] )
		links.append(get_link(args[0], top_users = options.top))

	# get the outputfilename 
	outputfilename = args[1] 
	outputfile     = open(outputfilename, 'w')
	print_header(outputfile) # print the column names to the output file

	if options.verbose: # prints the list of pages to be scraped
		print("\nList of pages to be scraped:\n")
		print("no.\t\ttitle\t\tlink")
		print("---\t\t-----\t\t----")
		for i, (article_title, link) in enumerate(zip(article_titles, links)): 
			print("%d\t\t%s\t\t%s"%(i+1, article_title, link))
		print("---\t\t-----\t\t----\n\n")

	successfully_scraped = 0 # number of successfully scraped pages
	n_links = len(links) # total number of links to be scraped

	attempt = 0 # number of attempts to scrape the articles in the list 
	failed_articles = [] # a list of the articles that failed to be scraped so far

	# try to scrape all the pages until you 1) scraped all, or 2) extended the number of attempts
	while (successfully == n_links) or (attempt < options.max_attempts): 

		for article_title, link in zip(article_titles, links): 
			if options.verbose: 
				print("Starting with scraping") 

	# go through all the wikipedia links
	for name, link in zip(article_titles, links): 

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
		print("DONE")

	# print list of failed names: 

	print('\npages that failed:\n\n')
	for page in list_names_failed: 
		print(page)

	outputfile.close()	
	
if __name__ == '__main__':
	sys.exit(main())