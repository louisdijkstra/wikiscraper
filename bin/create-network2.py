#!/usr/bin/env python
from __future__ import print_function, division
from optparse import OptionParser
import os
import sys
import networkx as nx
import pandas as pd
from pandas import DataFrame
from pandas import Series

__author__ = "Louis Dijkstra"

usage = """%prog <users.tsv> <articles.tsv> <output.gexf>

	<users.tsv>		file generated by scrape-top-edits-for-users.py
	<articles.tsv>  file with the empirical Bayes estimates for all the articles
	<output.gexf> 	output file that will contain the network data (suitable for Gephy)

Creates a network from all the articles in the <articles.tsv> file. Every node 
is associated with a weight equal to the empirical Bayes estimate (eb_estimate). 

The connections between the nodes are based on <users.tsv>; the weighted
edges represent the number of users that contributed ot both articles. 

The <users.tsv> file should contain the following columns: 

	user 	title 	 n_edits

The <articles.tsv> file should contain the following columns: 

	title	s	n	rate	eb_estimate	alpha1	beta1	credible_low	credible_high	credible_width	rank_based_on_eb_estimate	rank_based_on_n	rank_based_on_s
"""

def main():

	parser = OptionParser(usage=usage)	
	parser.add_option("-m", action="store", dest="min_weight", default=0, type=int, 
				  			help="Minimal weight for the edges to be taken into account (Default: no minimum)")
	parser.add_option("-k", action="store", dest="min_rank", default=None, type=int, 
				  			help="Minimum rank.")
	parser.add_option("-l", action="store", dest="max_rank", default=None, type=int, 
				  			help="Maximum rank.")
	parser.add_option("-t", action="store", dest="top", default=None, type=int, 
				  			help="Top number of articles with highest Empirical Bayes estimates are added.")
	parser.add_option("-T", action="store", dest="top_contributors", default=None, type=int, 
				  			help="Top number of articles with the highest number of contributors from the community of interest (s)")
	parser.add_option("-u", action="store", dest="min_users", default=0, type=int, 
				  			help="Minimal number of editors for an article to be taken into account (Default: no minimum)")
	parser.add_option("-v", action="store_true", dest="verbose", default=False, 
				  			help="verbose.")
	(options, args) = parser.parse_args()
	
	# process arguments
	if (len(args)!=3):
		parser.print_help()
		return 1

	userfilename    = args[0]
	articlefilename = args[1]
	outputfilename  = args[2]

	# read in the data
	user_df    = DataFrame.from_csv(userfilename, sep='\t', index_col=False) # the core users
	article_df = DataFrame.from_csv(articlefilename, sep='\t', index_col=False) # all the pheripheral articles

	article_df = article_df.sort_values(by=['rank_based_on_eb_estimate'])

	# get the top number of users
	if options.top is not None: 
		article_df = article_df[article_df['rank_based_on_eb_estimate'] <= options.top]

	if options.min_rank is not None: 
		article_df = article_df[article_df['rank_based_on_eb_estimate'] >= options.min_rank]

	if options.max_rank is not None: 
		article_df = article_df[article_df['rank_based_on_eb_estimate'] <= options.max_rank]

	if options.top_contributors is not None: 
		article_df = article_df[article_df['rank_based_on_s'] <= options.top_contributors]

	# get all articles with the minimum number of editors from the community into account
	article_df = article_df[article_df['s'] >= options.min_users]

	# get all the unique article titles 
	unique_articles = article_df.title.unique()

	# remove all the articles from the user list that are not in the article list
	user_df = user_df[user_df['title'].isin(list(unique_articles))]

	# get all the unique users
	unique_users = user_df.user.unique()
	n_users = len(unique_users)

	# initialize the network
	G = nx.Graph()

	# add the articles as nodes to the network
	for article in article_df.iterrows():
		G.add_node(article[1]['title'], 
			eb_estimate=article[1]['eb_estimate'],
			rate=article[1]['rate'], 
			contributors_from_drug_community=article[1]['s'],
			total_number_contributors=article[1]['n'], 
			rank_based_on_n=article[1]['rank_based_on_n'],
			rank_based_on_s=article[1]['rank_based_on_s'],
			rank_based_on_eb_estimate=article[1]['rank_based_on_eb_estimate'],
			credible_width=article[1]['credible_width']
			)

	# walk through every single user and go through his/her contributions
	for i, username in enumerate(unique_users): 
		if options.verbose: 
			print('Processing user no. %d of %d\t(%.2f %%)\tname: %s'%(i+1, n_users, float(i+1)/float(n_users) * 100, username))

		df_for_one_user = user_df[user_df.user == username] 

		articles = list(df_for_one_user.title) # get the articles for this user

		# only use the articles that were in the original list
		# articles = list(set(unique_articles).intersection(articles))

		# add the edges
		for i in range(len(articles) - 1): 
			article1 = articles[i]
			if not article1 in unique_articles: 
				continue 

			for j in range(i+1, len(articles)): 
				article2 = articles[j]
				if not article2 in unique_articles: 
					continue 
				if G.has_edge(article1, article2):
					G[article1][article2]['weight'] += 1
				else:
					G.add_edge(article1, article2, weight=1)

	print("Total of %d nodes and %d edges were added" % (G.number_of_nodes(), G.number_of_edges()))
	
	# walk through the edges and see whether their weight is sufficient
	for u,v,a in G.edges(data=True):
		if a['weight'] < options.min_weight: 
			G.remove_edge(u,v)

	nx.write_gexf(G, outputfilename)

if __name__ == '__main__':
	sys.exit(main())