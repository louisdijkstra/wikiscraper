Wikiscraper
===========

This repository contains the code/scripts for the Wikipedia Scraper; a tool for scraping both artciles and users on the online encyclopedia Wikipedia. 

This repository is published under the Apache 2, see `LICENSE`.

## Getting started

The code/scripts in this project are written in Python. We require __Python 3__ to be installed. First, install `virtualenv` (if you haven't already): 

    $ pip install virtualenv 

Create a virtual environment called `wiki` by typing in the main directory: 

    $ virtualenv -p python3 wiki
    $ source wiki/bin/activate

You can now easily install all requirements by typing

    $ pip install -r requirements.txt

Make sure that whenever you start working with the scripts in this repository to source the environment: 

    $ source wiki/bin/activate

## Directory structure 

The repository consists of the following directories/files: 

* `bin/` - contains various Python scripts.

* `data/` - contains the raw data files. See the `README.md` for a more elaborate description of each file. 

* `wikiscraper/` - the wikiscraper package.

## Contact

Louis Dijkstra

__E-mail__: louisdijkstra (at) gmail.com

