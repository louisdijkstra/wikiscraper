`data/`
=======

This directory contains the following files: 

* `co-contribution_network.gephi` - the co-contribution network for the designer drug community (suitable for Gephi). We reduced the original number of nodes (which is over 200,000) by selecting the top 250 articles that received most contributions from the designer drug community, which yielded a set of 7,745. (The discrepancy is because some articles had the same number of contributors). In addition, we filtered out nodes with a degree of 1; edges with a weight less than 3 were removed as well. The node size in the figure reflects the node’s degree. The color of the node represents the empirical Bayes contribution probability estimate; red reflects a low contribution probability, yellow is middle-ground, and blue corresponds to high contribution probabilities.

* `co-contribution_network.gexf` - the co-contribution network stored in the GEXF format on which the `.gephi` file is based. The network file was generated using the following script: 
    
        $ python bin/create-network2.py -T 250 data/designer_drugs_peripheral_articles.csv data/designer_drugs.csv data/co-contribution_network.gexf

* `designer_drugs_peripheral_articles.csv` - the list of all peripheral articles for the designer drugs community. The columns represent the following: 

    - `user`: the user name;     
    - `title`: the title of the Wikipedia articles, and
    - `n_edits`: the number of edits he/she made to the article. 

* `designer_drugs_user_community.csv` - a list of all the users in the designer drugs user community, i.e., the core users. The columns represent the following: 

    - `name`: the title of the core article; 
    - `user`: the user name; 
    - `n_edits`: total number of edits; 
    - `n_minor_edits`: number of minor edits; 
    - `first_edit`: when the user made his/her first edit; 
    - `last_edit`: when the user made his/her last edit; 
    - `added_bytes`: number of bytes added to the article. 
    
* `designer_drugs.csv` - the main data file. Every line is a peripheral article. The columns represent: 

    - `title`: the title of the article; 
    - `s`: the number of core users that contributed to the article; 
    - `n`: the total number of users that contributed to the article; 
    - `rate`: the fraction s/n; 
    - `eb_estimate`: the empirical Bayes estimate of the contribution probability; 
    - `alpha1`: the alpha parameter for the Beta posterior for this article;
    - `beta1`: the beta parameter for the Beta posterior for this article;
    - `credible_low`: the start of the 95% HPD credible interval; 
    - `credible_high`: the end of the 95% HPD credible interval; 
    - `credible_width`: the width of the interval, i.e., `credible_high` - `credible_low`;
    - `rank_based_on_eb_estimate` - rank based on the empirical Bayes estimate; 
    - `rank_based_on_n` - rank based on the total number of users that contributed;    
    - `rank_based_on_s` - rank based on the number of core users that contributed.

* `list-designer-drugs.txt` - list of the designer drugs articles used to define the user community. 
