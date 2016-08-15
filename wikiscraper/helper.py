import os
import sys
import urllib3
import json
from bs4 import BeautifulSoup
import requests
import shutil
from IPy import IP

urllib3.disable_warnings()

# user agent for scraping the XTools pages
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.96 Safari/537.36'}

"""
	File containing helper functions for crawling
	Wikipedia articles, revisions, references etc.
"""

# class ContigencyTable: 

# 	"""
# 	A class to represent a simple 2x2 contingency table 

# 	The representation is as follows: 

# 				|	X = 0 		| 		X = 1 	| 	total 
# 		---------------------------------------------------
# 		Y = 0 	| 		a 		| 		c 		|   a + c 
# 		Y = 1 	| 		b 		| 		d  		| 	b + d 
# 		---------------------------------------------------
# 		total 	| 	   a + b    |      c + d 	|   n = a+b+c+d
# 	"""
# 	def __init__(self): 
# 		self.a, self.b, self.c, self.d, self.n = 0,0,0,0,0

def find_between(s, first, last):
	"""
	Returns the characters in str between the sequences first 
	and last. 

	Source: http://stackoverflow.com/questions/3368969/find-string-between-two-substrings
	"""
	try:
	    start = s.index(first) + len(first)
	    end = s.index(last, start)
	    return s[start:end]
	except ValueError:
	    return ""

def is_anonymized(username): 
	"""
		Returns True when the user is anonymous, otherwise False. 

		Args: 
			username - the name of a Wikipedia user
	"""
	try: 
		IP(username)
		return True
	except: 
		return False

def is_bot(username): 
	"""
		Returns True when the user is a bot, otherwise False. 

		Args: 
			username - the name of a Wikipedia user
	"""
	if 'bot' in username.lower(): 
		return True
	return False


def read_list_from_file(filename): 
	"""	
		Reads in a list from file. Assumes that every line is a different
		entry. 

		Args:
			filename - the name of the file that contains the list

		Returns:
			list 
	"""
	l = [] 
	with open(filename, 'r') as inputfile:
		for username in inputfile: 
			l.append(username.strip())
	return l 

def read_in_data_from_url(url, headers=False, json=False): 
	"""
	Reads in the HTML data from a given site.

	Args:
		url     - the url of the site
		headers - when True, a fake agent is used
		json    - when True, the output is returned in JSON format
	
	Returns:
		raw HTML output or JSON formated data
	"""
	http = urllib3.PoolManager()

	if headers: # use fake agent
		request = http.request('GET', url, headers=USER_AGENT)
	else: 
		request = http.request('GET', url)

	soup = BeautifulSoup(request.data, 'html.parser')

	if json: # output in JSON format or not
		return json.loads(soup.get_text())
	else: 
		return soup.get_text()

def get_links(list_names, link="<NAME>", space_replace='%20'): 
	"""
	Turns a list of names/titles into a list of links 

	Args:
		list_names    - a list of names (either article tiles or user names)
		link          - the link that will be scraped. The part "<article-name>" will be replaced
				        by the actual article name as read from file. 
		space_replace - the spaces in the title/name will be replaced by this symbol for 
			            the links (default: %20). Otherwise, the links don't work.
	
	Returns: 
		list_names - the original list of names
		links      - a list with all the links
	"""
	links = []

	for name in list_names: 
		name = name.replace(' ', space_replace) # replace the spaces
		new_link = link.replace('<NAME>', name)
		links.append(new_link)

	return list_names, links

def read_in_links_from_file(inputfilename, link="<NAME>", space_replace='%20'): 
	"""
	Reads in a list of titles/names from the given input file. 
	We assume that every row is a seperate name. 

	Args:
		inputfilename - the location of the inputfile 
		link          - the link that will be scraped. The part "<NAME>" will be replaced
				        by the actual article name as read from file. 
		space_replace - the spaces in the title/name will be replaced by this symbol for 
			            the links (default: %20). Otherwise, the links don't work.
	
	Returns: 
		list_names - the list of names/titles
		links      - a list with all the links
	"""
	list_names = []

	# read in the list of usernames/titles
	with open(inputfilename, 'r') as inputfile:
		for name in inputfile: 
			list_names.append(name.strip())

	return list_names, get_links(list_names, link=link, space_replace=space_replace)
