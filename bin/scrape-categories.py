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

Scraps the categories of all Wikipedia pages in the 
<link-list.txt> file. The output is stored in CSV format 
(tab-delimited). It contains the following columns: 

	page_id  - id of the Wikipedia page
	name     - title of the page
	category - a category of the page
"""

def printHeader(file): 
	print("page_id\tname\tcategory", file=file)

def main():

	parser = OptionParser(usage=usage)	
	parser.add_option("--sleep", "-s", action="store", dest="sleep", default=None, type=float, 
				  			help="Sleep time scraping two pages. (Default: no sleep)")
	parser.add_option("-v", action="store_true", dest="verbose", default=False, 
				  			help="verbose.")
	(options, args) = parser.parse_args()
	
	# process arguments
	if (len(args)!=2):
		parser.print_help()
		return 1

	try: # in case a file is passed as the first argument
		inputfile = open(args[0], 'r')
		titles, links = [], [] 
		for title in inputfile: 
			title      = title.strip() 
			link_title = title.replace(' ', '%20')

			link = "https://en.wikipedia.org/w/api.php?action=query&titles=" + link_title + "&prop=categories&format=json&clshow=!hidden"

			# add to the lists
			titles.append(title)
			links.append(link)

	except: # in case just one title is given
		link_title = args[0].replace(' ', '%20') # replace the spaces
		titles, links = [args[0]], ["https://en.wikipedia.org/w/api.php?action=query&titles=" + link_title + "&prop=categories&format=json&clshow=!hidden"]

	outputfilename = args[1] 

	# if options.verbose: # prints the list of pages to be scraped
	# 	print("\nList of pages to be scraped:\n")
	# 	print("title\t\tlink")
	# 	print("-----\t\t----")
	# 	for name, link in zip(titles, links): 
	# 		print("%s\t\t%s"%(name, link))
	# 	print("-----\t\t----\n\n")

	i       = 0
	n_links = len(links)

	outputfile = open(outputfilename, 'w')

	printHeader(outputfile)

	# go through all the wikipedia links
	for title, link in zip(titles, links): 

		if options.verbose: 
			i += 1
			print('%d of %d links processed... (%.2f %%)'%(i, n_links, float(i) / float(n_links) * 100))
			print("Continuing with scraping %s (link: %s)"%(title, link))

		# get the raw data
		try: 
			data = json.loads(readInDataFromURL(link))
		except: 
			print("Couldn't process %s (link %s)"%(title, link))
			continue

		# walk through the categories
		for page_id, page in data['query']['pages'].items(): 
			try: 
				for category in page['categories']: 
					# print to the output file
					print('%s\t%s\t%s'%(page_id, title, category['title'][9:]), file=outputfile)
			except: 
				if options.verbose: 
					print('Page %s does not have any categorization...'%title)		

		if options.sleep != None: 
			time.sleep(options.sleep)

	if options.verbose: 
		print(" DONE")
	
if __name__ == '__main__':
	sys.exit(main())