# DVML-P7

This repository contains the codebase behind a paper produced by the group DVML-7-01 from the Department of Computer Science at Aalborg University during a project period from September 2022 to January 2023. 

The main purpose of the project was to transform the [Yelp Open Dataset](https://www.yelp.com/dataset) to a knowledge graph.

The two directories "YelpOntology" and "Code" are the main directories used in the paper.

## YelpOntology
This directory represents our own Yelp ontology.
The directory contains 4 files. The 'create_ttl_file.ipynb' is used to create the full 'yelp_categories.ttl' file, containing all Yelp categories which could not be mapped to schema.org and therefore instead created in our own Yelp ontology. 
The 'yelp_ontology.ttl' file contains the description of our ontology, the 5 custom classes used, and the 114 properties which are not mapped to schema.org. The property descriptions include their IRI, property types, a comment explaining their meaning and use case, domain, range, and a label. 
Finally, the 'yelp_entities.ttl' file is used for the Yelp entities businesses, users, reviews, and tips. The file itself is empty, because if we were to include all entities, this would result in more than 8 million entries.

## Code

Here, the file 'create_nt_files.py' is used for creating the Yelp knowledge graph, according to the methods described in section 6 of the paper. 
The directories 'UtilityFunctions' and 'AuxiliaryFunctions' contain functions used during the knowledge graph construction. 
The directory 'CompetencyQuestions' contains the full notebooks behind answering the KG and external KG competency questions, as well as their corresponding markdown files. 
Finally, the 'KnowledgeGraphEnrichment' directory contains the code behind extracting data from Wikidata, linking Wikidata items to Yelp entities and merging the two knowledge graphs, also described in section 7 of the paper.

## Paper Abstract 


