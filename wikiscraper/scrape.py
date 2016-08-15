from __future__ import print_function
import sys
import os
import math
import pandas as pd 
from pandas import DataFrame
from pandas import Series

from .helper import * 

SCRAPING_SUCCESSFULL = 1 # flag for when scraping was successful 
SCRAPING_FAILED      = 0 # flag for when scraping failed 

def skip(list, current_index, increase_index):
	"""
	Increases the current index with a specific number of steps
	given by increase_index and returns the value at that position
	"""
	current_index += increase_index
	return current_index, list[current_index]






def get_number_registered_users(): 
	"""
	Gets the total number of registered users (no bots and no IP addresses) for 
	the English Wikipedia from the url https://en.wikipedia.org/wiki/Special:Statistics

	Returns:
		# of registered English wikipedia users
	"""
	# the url to be scraped
	url = "https://en.wikipedia.org/wiki/Special:Statistics"

	# scrape the url
	try: 
		raw_data = read_in_data_from_url(url, headers=False, json=False)
	except: 
		return SCRAPING_FAILED

	n_registered_users = find_between(raw_data, "Registered users", "Active registered users")
	n_registered_users = int( n_registered_users.strip().replace(',', '') )

	return n_registered_users


def scrape_article_for_external_links(article_title, file=sys.stdout, header=False): 
	"""	
	Gets the external links for a given article. The output is only
	outputed (either to file or standard out, see option 'file') when the scraping 
	was successfull. 

	Args: 
		article_title - title of the article
		file          - the output is outputed there (Default: standard out)
		header        - when True, the header is outputted as well (default: False)

	Returns: 
		flag - is SCRAPING_SUCCESSFULL when successfull, otherwise SCRAPING_FAILED.
    """    
	# the url to be scraped
	url = "https://en.wikipedia.org/w/api.php?action=query&prop=extlinks&format=json&ellimit=5000&titles=%s"%(article_title.replace(' ', '%20'))

    # scrape the url
	try: 
		raw_data = read_in_data_from_url(url, headers=False, json=True)
	except: 
		return SCRAPING_FAILED

	if header: 
		print("page_id\tname\texternal_link", file=file)

	# walk through all the external links
	for page_id, page in raw_data['query']['pages'].items(): 
		if 'extlinks' in page: # check whether there are external links
			for extlink in page['extlinks']: 
				# print to the output file
				print('%s\t%s\t%s'%(page_id, article_title, extlink['*']), file=file)

	return SCRAPING_SUCCESSFULL

def scrape_article_for_categories(article_title, file=sys.stdout, header=False): 
	"""	
	Gets the Wikipedia categories for a given article. The output is only
	outputed (either to file or standard out, see option 'file') when the scraping 
	was successfull. Note: only returns the non hidden categories (hidden Wikipedia
	related categories are ignored).

	Args: 
		article_title - title of the article
		file          - the output is outputed there (Default: standard out)
		header        - when True, the header is outputted as well (default: False)

	Returns: 
		flag - is SCRAPING_SUCCESSFULL when successfull, otherwise SCRAPING_FAILED.
    """
	# the url to be scraped
	url = "https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=categories&format=json&clshow=!hidden"%(article_title.replace(' ', '%20'))

	# scrape the url
	try: 
		raw_data = read_in_data_from_url(url, headers=False, json=True)
	except:
		return SCRAPING_FAILED

	if header: 
		print("page_id\tname\tcategory", file=file)

	# walk through all the external links
	for page_id, page in raw_data['query']['pages'].items(): 
		if 'categories' in page: # check whether there are categories
			for category in page['categories']: 
				# print to the output file
				print('%s\t%s\t%s'%(page_id, article_title, category['title'][9:]), file=file)

def scrape_list_articles_for_users(list_of_articles, output=sys.stdout, max_attempts=5, header=True, top=10000, no_bots=False, no_unregistered=False, verbose=False): 
	"""
	Scrapes a list of articles for the users that contributed most to each of the articles 
	separately. 

	Args:
		list_of_articles - a list of titles of Wikipedia articles
		output           - either outputfile or standard out
		max_attempts     - Number of attempts to scrape the sites.
		header           - when True, the header is outputted as well (Default: True)
		top              - top number of users (by number of edits) scraped (Default: 10000)
		no_bots 	     - bot users are ignored
		no_unregistered  - unregistered users are ignored
		verbose          - when true, output is more verbose
	"""
	if verbose: 
		print('\nwikiscrape')
		print('----------\n')
		print("Preparing to scrape the top edited articles.\n")
		print("# articles\t\t: %d"%len(list_of_articles))
		if max_attempts == math.inf: 
		    print("# scrape attempts\t: unlimited")
		else: 
		    print("# scrape attempts\t: %d"%max_attempts)
		print("top\t\t\t: %d"%top)
		if output != sys.stdout: 
		    print('output\t\t\t: %s'%output)
		else: 
		    print('output\t\t\t: standard out')
		print('\n')

	# print the header
	if header: 
		print("name\tuser\tn_edits\tn_minor_edits\tfirst_edit\tlast_edit\tadded_bytes", file=output)

	n_attempt              = 0 # number of attempts
	initial_n_articles     = len(list_of_articles)
	n_successfully_scraped = 0

	# scrape until 1) the number of attempts did not exceed its maximum, or 2) all pages have been scraped
	while n_attempt < max_attempts and len(list_of_articles) > 0: 
		# go over all users that still need to be crawled
		for i, title in enumerate(list_of_articles): 
			flag = scrape_article_for_users(title, file=output, top=top, header=False, no_bots=no_bots, no_unregistered=no_unregistered)
			if flag == SCRAPING_SUCCESSFULL: 
				del list_of_articles[i] # remove the user from the list of users that still need to be scraped
				n_successfully_scraped += 1
				if verbose and output != sys.stdout: 
					print('Scraped %d of %d articles\t(%.2f %%)'%(
							n_successfully_scraped, 
							initial_n_articles, 
							float(n_successfully_scraped) / float(initial_n_articles) * 100))
		n_attempt += 1



def obtain_2x2_contigency_table(article_title, users_of_interest, total_size_community, top=10000):
	"""
	Obtains the relevant data to preform a hypothesis test of association between 
	contributing to the article with the title <article_title> and the community of 
	interest, given by the list <users_of_interest>. This function scrapes the 
	list of users that contributed to the article and return the values a, b, c and 
	d as given in the following 2x2 contingency table: 

							|	community of interest 	|	rest wikipedia 	|	total 
	------------------------------------------------------------------------------------
	contributed to article 	|			a 				| 			c 		| 	q = a + c 
	not contributed 		| 			b 				| 			d 		| 	r = b + d 
	------------------------------------------------------------------------------------
	total 					| s = len(users_of_interest)| 	t =	c + d 		| total_size_community

	Args:
		article_title        - the title of the article
		users_of_interest    - list with user names in the community of interest
		total_size_community - number of registered users in Wikipedia (see get_number_registered_users)
		top                  - top number of users (by number of edits) scraped (Default: 10000)
		verbose              - when true, output is more verbose

	Returns: 
		the 2x2 table: [[a, c], [c, d]] 
		flag - whether scraping was successfull or not
	""" 
	n_users_of_interest = len(users_of_interest)
	# get a list of all the user names that edited the page
	list_users_that_contributed = scrape_article_for_users(article_title, file=sys.stdout, header=False, top=top, no_bots=True, no_unregistered=True, only_usernames=True)

	if list_users_that_contributed == 0: 
		return [[None, None], [None, None]], SCRAPING_FAILED

	# number of users that contributed
	n_contributed = len(list_users_that_contributed)

	a = len(set(users_of_interest) & set(list_users_that_contributed))
	b = n_users_of_interest - a
	c = len(list_users_that_contributed) - a
	d = total_size_community - a - b - c

	return [[a, c], [b, d]], SCRAPING_SUCCESSFULL

def scrape_article_for_users(article_title, file=sys.stdout, header=False, top=10000, no_bots=False, no_unregistered=False, only_usernames=False): 
	"""	
	Gets the top users that contributed to the given article. The output is only
	outputed (either to file or standard out, see option 'file') when the scraping 
	was successfull. 

	Args: 
		article_title   - title of the article
		file            - the output is outputed there (Default: standard out)
		header          - when True, the header is outputted as well (default: False)
		top             - top number of users scraped (Default: 10000)
		no_bots 	    - bot users are ignored
		no_unregistered - unregistered users are ignored
		only_usernames  - if True, the function returns only a list of usernames that edited the page

	Returns: 
		flag - is SCRAPING_SUCCESSFULL when successfull, otherwise SCRAPING_FAILED.
    """
	# the url to be scraped
	url = "https://tools.wmflabs.org/xtools-articleinfo/?article=%s&project=en.wikipedia.org&editorlimit=%s#topeditors"%(
				str(article_title).replace(' ', '%20'), str(top))

	# scrape the url
	try: 
		raw_data = read_in_data_from_url(url, headers=True, json=False)
	except:
		return SCRAPING_FAILED

	# split into lines
	raw_data = raw_data.splitlines() 

	# go to the relevant table (just after the line with 'Added (Bytes)')
	i, line = 0, raw_data[0]
	while not 'Added (Bytes)' in line: 
		try: 
			i, line = skip(raw_data, i, 1)
		except: 
			return SCRAPING_FAILED

	if header: # prints the header	
		print("name\tuser\tn_edits\tn_minor_edits\tfirst_edit\tlast_edit\tadded_bytes", file=file)

	i, line = skip(raw_data, i, 3) # get to the starting point of the list

	list_usernames = []

	while len(line) != 0: # not the end of the table
		# get the user name 
		username = line.strip() 

		if no_bots and is_bot(username): 
			i, line = skip(raw_data, i, 14)
			continue
		if no_unregistered and is_anonymized(username): 
			i, line = skip(raw_data, i, 14)
			continue

		if only_usernames: # only interested in the usernames
			list_usernames.append(username) 
			i, line = skip(raw_data, i, 14)
		else: 	
			print("%s\t%s"%(article_title, username), end='\t', file=file) # article title and username
			i, line = skip(raw_data, i, 5)
			print(line.strip(), end='\t', file=file) # number of edits
			i, line = skip(raw_data, i, 1)
			print(line.strip(), end='\t', file=file) # number of minor edits
			i, line = skip(raw_data, i, 2)
			print(line.strip(), end='\t', file=file) # first edit
			i, line = skip(raw_data, i, 1)
			print(line.strip(), end='\t', file=file) # last edit
			i, line = skip(raw_data, i, 2)
			print(line.strip().replace(',', ''), file=file) # added_bytes
			i, line = skip(raw_data, i, 3)

	if only_usernames: 
		return list_usernames
	return SCRAPING_SUCCESSFULL

def scrape_list_users_for_articles(list_of_users, output=sys.stdout, max_attempts=5, header=True, verbose=False): 
	"""
	Scrapes a list of users for the articles that they edited the most.  

	Args:
		list_of_users    - a list of usernames
		output           - either outputfile or standard out
		max_attempts     - Number of attempts to scrape the sites.
		header           - when True, the header is outputted as well (Default: True)
		verbose          - when true, output is more verbose
	"""
	if verbose: 
		print('\nwikiscrape')
		print('----------\n')
		print("Preparing to scrape the top edited articles.\n")
		print("# users\t\t\t: %d"%len(list_of_users))
		if max_attempts == math.inf: 
		    print("# scrape attempts\t: unlimited")
		else: 
		    print("# scrape attempts\t: %d"%max_attempts)
		if output != sys.stdout: 
		    print('output\t\t\t: %s'%output)
		else: 
		    print('output\t\t\t: standard out')
		print('\n')

	# print the header
	if header: 
		print("user\ttitle\tn_edits", file=output)

	n_attempt              = 0 # number of attempts
	initial_n_users        = len(list_of_users)
	n_successfully_scraped = 0

	# scrape until 1) the number of attempts did not exceed its maximum, or 2) all pages have been scraped
	while n_attempt < max_attempts and len(list_of_users) > 0: 
		# go over all users that still need to be crawled
		for i, username in enumerate(list_of_users): 
			flag = scrape_user_for_articles(username, file=output, header=False, verbose=False)
			if flag == SCRAPING_SUCCESSFULL: 
				del list_of_users[i] # remove the user from the list of users that still need to be scraped
				n_successfully_scraped += 1
				if verbose and output != sys.stdout: 
					print('Scraped %d of %d users\t(%.2f %%)'%(
							n_successfully_scraped, 
							initial_n_users, 
  							float(n_successfully_scraped) / float(initial_n_users) * 100))
		n_attempt += 1

def scrape_user_for_articles(username, file=sys.stdout, header=False, verbose=False): 
	"""	
	Gets the top edits for the Wikipedian with the given username. The output is only
	outputed (either to file or standard out, see option 'file') when the scraping 
	was successfull. 

	Args: 
		username      - the username of the user
		file          - the output is outputed there (Default: standard out)
		header        - when True, the header is outputted as well (default: False)

	Returns: 
		flag - is SCRAPING_SUCCESSFULL when successfull, otherwise SCRAPING_FAILED.
    """
    # the url to be scraped
	url = "https://tools.wmflabs.org/xtools/topedits/?user=%s&project=en.wikipedia.org&namespace=0&article="%(username.replace(' ', '%20'))

	if verbose: 
		print("Start scraping user %s\t(link: %s)"%(username, url))

    # scrape the url
	try: 
		raw_data = read_in_data_from_url(url, headers=True, json=False)
	except:
		return SCRAPING_FAILED

	# split into lines
	raw_data = raw_data.splitlines() 

	# go to the relevant table (just after the line with 'TOP edits per namespace [hide]')
	i, line = 0, raw_data[0]
	while not 'TOP edits per namespace [hide]' in line: 
		try: 
			i, line = skip(raw_data, i, 1)
		except: 
			return SCRAPING_FAILED

	if header: # prints the header	
		print("user\ttitle\tn_edits", file=file)

	i, line = skip(raw_data, i, 5) # get to the starting point of the list

	while len(line) != 0: # not the end of the table
		print(username, end='\t', file=file) # the username
		n_edits = line.strip()
		i, line = skip(raw_data, i, 1)
		print(line.strip(), end='\t', file=file) # article title
		print(n_edits, file=file) # number of edits
		i, line = skip(raw_data, i, 6)

	return SCRAPING_SUCCESSFULL

