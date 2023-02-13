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
The directory 'UtilityFunctions' contain functions used during the knowledge graph construction. 
The directory 'CompetencyQuestions' contains the full notebooks behind answering the KG and external KG competency questions, as well as their corresponding markdown files. 
Finally, the 'KnowledgeGraphEnrichment' directory contains the code behind extracting data from Wikidata, linking Wikidata items to Yelp entities and merging the two knowledge graphs, also described in section 7 of the paper.

### For runnig the code and creating our Yelp Knowledge Graph, the following steps are required:

The machine requires a minimum of 64GB of RAM to run the Virtuoso and a disc size of at least 32GB to store the data and the Virtuoso database.

1. Clone this repository to a directory of your choice.
2. Create a Python 3.10.6 virtual environment and install the requirements from the 'requirements.txt' file.
3. Download the Yelp Open Dataset from [here](https://www.yelp.com/dataset) and extract the files to the 'Data' directory.
4. Create a Virtuoso Docker by following [this guide](https://people.cs.aau.dk/~matteo/notes/virtuoso-setup-on-docker.html) created by Matteo Lissandrini.
5. Edit the `data_path.txt` file in the 'Config' directory to point to the directory where you extracted the Yelp Open Dataset.
6. Optional for newer data: Download the schema.org ontology from [here](https://schema.org/version/latest/schemaorg-current-https-types.csv) and place it in the data directory, then run the command `python schema_functions.py` (this replaces the `class_hierarchy.csv` file in the 'UtilityData' directory).
7.  Run the 'create_yelp_nt.py' file to create the Yelp n-triple files. Using the following command: `python create_yelp_nt.py`
8.  Replace the `import.isql` in the import folder of your Virtuoso directory with our `import.isql` file in the 'Virtuoso' directory.
9.  Run the `import.isql` file to import the Yelp n-triple files into the Virtuoso database. Using the following command: `docker exec -it vos isql  1111 exec="LOAD /import/import.isql"`
    1.  if it fails, try changing the path to the all the .nt.gz files in the import.isql file to the path of the .nt.gz files, that should have been created in the data directory when running `create_yelp_nt.py`.
10. Now the Yelp knowledge graph is created and can be queried using SPARQL.

## Paper Abstract 
One way to represent data is to model it as a knowledge graph, where nodes represent entities of interest and edges represent different relations between these entities. While large open-domain knowledge graphs exist, such as Wikidata and DBpedia, smaller domain-specific knowledge graphs are seeing a rise in applications. However, knowledge graph construction is complex and still sees challenges with regards to integrating heterogeneous data sources and data quality.
In this paper, we contribute with two things; one, showcasing how to properly construct knowledge graphs, using techniques such as competency questions and ontology alignment; two, constructing an applicable Yelp domain knowledge graph with a related Yelp ontology, and enriching it with the Wikidata knowledge graph. This will have an impact as a resource to support, for instance, research in advanced recommendation engines.

In light of this, we investigate multiple methods. We set up KG requirements in the form of $16$ competency questions, of which 14 could be answered by the Yelp KG we created. We create mappings from the Yelp business category domain to the \textit{schema.org} ontology, using a semantic model. Using a similarity threshold of $0.68$, we obtain $291$ ($23.6\%$) high quality category mappings, resulting in $94.6\%$ of all businesses having at least one of their categories mapped. 

We also align parts of our Yelp knowledge graph with the Wikidata ontology, specifically the categories and locations. For the categories, a total of $564$ ($39.8\%$) of the categories are mapped with a `sameAs' relation. Likewise, for the locations, we correctly link the city of $96.82\%$ of businesses, thereby providing the full knowledge of these cities in Wikidata, such as population and counties. Last, we also constructed a Yelp ontology containing $5$ classes and $116$ properties, representing the Yelp Open Dataset domain.

The final knowledge graph contains over $244$ million triples, approximately $72$ million resources and $144$ predicates, with an average in-degree and out-degree of $3.35$ and $12.20$ respectively.
