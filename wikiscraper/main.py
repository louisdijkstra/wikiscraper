"""
Main functions to run scripts from.
"""

from __future__ import print_function

from .version import __version__

import sys
import os
import docopt
import math
import pandas as pd 
from pandas import DataFrame
from pandas import Series
from scipy import stats

from .scrape import *
from .helper import * 

def get_max_attempts(argument):
    """
    Gets the maximum number of scraping attempts from the raw argument. 
    """
    if argument == None: 
        return 5 # default
    if argument == 'no': 
        return float("inf") # unlimited number of attempts
    return int(argument)

def get_outputfile(argument): 
    """
    Gets the outputfile from the raw argument.
    """
    if argument != None: 
        return open(argument, 'w')
    return sys.stdout

def get_number_users():
    """
    Outputs the total number of registered English Wikipedia users. 
    The data is obtained from the url https://en.wikipedia.org/wiki/Special:Statistics.
    
    Usage:
        wikistats [-h] [-V] 

    Options: 
        -h, --help      This help text
        -V, --version   Version information
    """
    n_registered_users = get_number_registered_users()
    print('Total number of registered English Wikipedia users: %d'%n_registered_users)

def scrape(argv=sys.argv[1:]): 
    """
    Returns a list of articles that characterize the users that contributed 
    to the given list of articles the most.  

    Usage: 
        wikiscrape [-a attempts] [-h] [-v] [-V] <article-file>

    where 
        <article-file> is a file with on every line the title 
            of a Wikipedia article

    Options: 
        -a, --attempts attempts     Number of attempts to scrape the sites. In case of 'no', unlimited. (Default: 5)
        -h, --help      This help text
        -v, --verbose   Verbose
        -V, --version   Version information
    """
    arguments = docopt.docopt(scrape.__doc__, argv, version=__version__)

    # get the original list of articles
    original_list_of_articles = read_list_from_file(arguments['<article-file>'])

    # get the base for the names of the other, intermediate files
    base_name, file_extension = os.path.splitext(arguments['<article-file>'])

    # get all the file names with the intermediate results: 
    original_articles_filename   = arguments['<article-file>']
    original_community_filename  = "intermediate-results/%s_orig_community.csv"%base_name
    other_articles_filename      = "intermediate-results/%s_other_articles.csv"%base_name
    other_articles_list_filename = "intermediate-results/%s_list_unqiue_other_articles.csv"%base_name
    all_users_filename           = "intermediate-results/%s_all_users.csv"%base_name 

    # get a list of the users that contributed to the original list of articles
    if not os.path.isfile(original_community_filename): 

        # scrape the orginal list of articles
        scrape_list_articles_for_users(
                    original_list_of_articles,
                    output=open(original_community_filename, 'w'),
                    max_attempts=get_max_attempts( arguments['--attempts'] ),
                    header=True,
                    top=100000,
                    no_bots=True,
                    no_unregistered=True,
                    verbose=True
                )

    # get the unique lists of users
    df = pd.read_table(original_community_filename, sep='\t')
    list_of_original_users = df.user.unique()

    # print(list_of_original_users)

    # get a list of the other articles these users contributed to
    if not os.path.isfile(other_articles_filename): 

        scrape_list_users_for_articles(
                list(list_of_original_users),
                output=open(other_articles_filename, 'w'),
                max_attempts=get_max_attempts( arguments['--attempts'] ),
                header=True,
                verbose=True
        )

    # get the unique lists of all articles 
    df = pd.read_table(other_articles_filename, sep='\t')
    list_of_other_articles = list(df.title.unique())

    # get the difference
    list_of_other_articles = list(set(list_of_other_articles) - set(original_list_of_articles))

    # print(list_of_other_articles)
    # print(len(list_of_other_articles))

    # TODO change
    total_size_community = get_number_registered_users()

    outputfilename = '%s_final.csv'%base_name

    # reduce the list by articles that were already crawled
    if os.path.isfile(outputfilename): 
        df = pd.read_table(outputfilename, sep='\t')
        list_of_crawled_articles = list(df.title.unique())
        list_of_other_articles = list(set(list_of_other_articles) - set(list_of_crawled_articles))

    output = open('%s_final.csv'%base_name, 'w')

    print("title\ta\tb\tc\td\todds_ratio\tp_value")

    with open(outputfilename, 'a') as output: 
        print("title\ta\tb\tc\td\todds_ratio\tp_value", file=output)

    for article_title in list_of_other_articles: 
        table, flag = obtain_2x2_contigency_table(article_title, list_of_original_users, total_size_community, top=10000)
        if flag == SCRAPING_FAILED: 
            continue
        odds_ratio, p_value = stats.fisher_exact(table, alternative='greater')
        print("%s\t%d\t%d\t%d\t%d\t%f\t%f"%(article_title, table[0][0], table[1][0], table[0][1], table[1][1], odds_ratio, p_value))
        with open(outputfilename, 'a') as output: 
            print("%s\t%d\t%d\t%d\t%d\t%f\t%f"%(article_title, table[0][0], table[1][0], table[0][1], table[1][1], odds_ratio, p_value), file=output)

    # article_title = "Googol"
    # print(article_title)
    # table = obtain_2x2_contigency_table(article_title, list_of_original_users, total_size_community, top=10000)
    # odds_ratio, p_value = stats.fisher_exact(table)
    # print("%s\t%d\t%d\t%d\t%d\t%f\t%f"%(article_title, table[0][0], table[1][0], table[0][1], table[1][1], odds_ratio, p_value))


def scrape_article(argv=sys.argv[1:]):
    """
    Gets of users that edited a list of given articles the most. 

    Usage:
        wikiscrape_article [--no-bots] [--no-unregistered] [-a attempts] [-o output] [-t top] [-h] [-v] [-V] <articles>

    where 
        <articles> is either 1) a file with all the article titles (every row is 
                one article), or, 2) a single article title.

    Example: 

        In case you want to obtain all users that made most edits for the article 
        "MDMA", type 

            wikiscrape_article "MDMA" 

    Options: 
        --no-bots                   Bots are ignored 
        --no-unregistered           Unregistered users (with just an IP address) are ignored
        -a, --attempts attempts     Number of attempts to scrape the sites. In case of 'no', unlimited. (Default: 5)
        -o, --output output         Output is stored in given file (Default: standard out)
        -t, --top top               Top number of users (by number of edits) scraped (Default: 10000)
        -h, --help                  This help text
        -v, --verbose               Verbose
        -V, --version               Version information
    """
        # process the arguments
    arguments = docopt.docopt(scrape_article.__doc__, argv, version=__version__)

    # get a list of all articles that need to be scraped 
    if os.path.isfile(arguments['<articles>']): # in case a file is passed as first argument
        list_of_articles = read_list_from_file(arguments['<articles>'])
    else: # just one article given
        list_of_articles = [arguments['<articles>']]
  
    top = 10000 if arguments['--top'] == None else int(arguments['--top'])

    scrape_list_articles_for_users(
                list_of_articles,
                output=get_outputfile(arguments['--output']),
                max_attempts=get_max_attempts( arguments['--attempts'] ),
                header=True,
                top=top,
                no_bots=arguments['--no-bots'],
                no_unregistered=arguments['--no-unregistered'],
                verbose=arguments['--verbose']
            )

def scrape_user(argv=sys.argv[1:]):
    """
    Gets a list of articles that were edited the most for every user in the 
    given list. 

    Usage:
        wikiscrape_user [-a attempts] [-o output] [-h] [-v] [-V] <users>

    where 
        <users> is either 1) a file with all the usernames (every row is 
                one user), or, 2) a single username.

    Example: 

        In case you want to obtain all articles for the user 'Sizeofint', type

            wikiscrape_user "Sizeofint" 

    Options: 
        -a, --attempts attempts     Number of attempts to scrape the sites. In case of 'no', unlimited. (Default: 5)
        -o, --output output         Output is stored in given file (Default: standard out)
        -h, --help                  This help text
        -v, --verbose               Verbose
        -V, --version               Version information
    """
    # process the arguments
    arguments = docopt.docopt(scrape_user.__doc__, argv, version=__version__)

    # get a list of all users that need to be scraped 
    if os.path.isfile(arguments['<users>']): # in case a file is passed as first argument
        list_of_users = read_list_from_file(arguments['<users>'])
    else: # just one user given
        list_of_users = [arguments['<users>']]
      
    scrape_list_users_for_articles(
                list_of_users,
                output=get_outputfile(arguments['--output']),
                max_attempts=get_max_attempts( arguments['--attempts'] ),
                header=True,
                verbose=arguments['--verbose']
        )
