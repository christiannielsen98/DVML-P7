import gzip
import json
import sys
import os

import inflect
import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal, BNode
from rdflib.namespace import RDFS

from UtilityFunctions.dictionary_functions import flatten_dictionary
from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.schema_functions import get_schema_predicate, get_schema_type
from UtilityFunctions.get_iri import get_iri

sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

schema = Namespace("https://schema.org/")
skos = Namespace("https://www.w3.org/2004/02/skos/core#")
yelpcat = Namespace("https://purl.archive.org/purl/yelp/business_categories#")
yelpont = Namespace("https://purl.archive.org/purl/yelp/yelp_ontology#")

def create_schema_file(file_name: str):
    """
    This function takes as input the Yelp business JSON file, and adds the yelp category to schema type semantic mappings to the KG.
    :param file_name: The Yelp JSON file to transform to RDF.
    :return: a .nt.gz file with Yelp data in RDF format.
    """
    triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/schema_mappings.nt.gz", mode="at",
                            encoding="utf-8")
    file_path = get_path(file_name)
    
    # We load in the semantic mappings as a dict and we also load the class hiearchies from schema.org
    schema_category_mappings_df = pd.read_csv(get_path("class_mappings_manual.csv"))
    schema_category_mappings_dict = dict([(i, eval(x)) for i, x in zip(schema_category_mappings_df['YelpCategory'],
                                                                        schema_category_mappings_df['SchemaType'])])
    class_hierarchies = pd.read_csv(get_path("class_hierarchy.csv"))

    G = Graph()  # Initialize an empty graph
    for idx, row in class_hierarchies.iterrows():  # Adds class hierarchies to the graph
        G.add(triple=(URIRef(Namespace(row['type'])),
                        RDFS.subClassOf,
                        URIRef(Namespace(row['superType']))))

    triple_file.write(G.serialize(format='nt'))

    with open(file=file_path, mode="r") as file:
     
        category_mappings_cache = set()  # Cache for category mappings to avoid duplicates.

        # Iterate over every object in the JSON file as each object is one line.
        for line in file:
            try:
                line = json.loads(line)  # json.loads loads the JSON object into a dictionary.

                G = Graph()  # Initialize a empty graph object to write a RDF triple to.

                json_key = list(line.keys())[0]  # Each dictionary has the ID as the value to the first key
                subject = get_iri(file_name) + line[json_key]  # get_iri makes sure the ID is a proper URI. 
                
                del line[json_key]  # After assigning the URI to the subject variable, we no longer need the first key/value pair

                line = flatten_dictionary(line)  # Some values are dictionaries themselves, so we flatten them before proceeding

                if line['categories']:
                    # Categories are initially one long comma-separated string.
                    categories = line['categories'].split(", ")
                    del line['categories']  # No longer need this key/value pair.
                    
                    for category in categories:
                        category = category.replace(' ', '_')  # Need to replace whitespace as we use it as URI
                        
                        if category.replace('_', ' ') in schema_category_mappings_dict.keys():
                            mappings = schema_category_mappings_dict[category.replace('_', ' ')]

                            # If there is only one mapping, it is an closeMatch                                
                            # If the original category is concatenated, add each mapping as a narrowMatch to the categrory
                            for subcategory in mappings:
                                G.add(triple=(URIRef(yelpcat + category),
                                                URIRef(skos + "narrowMatch") if "&" in category or "/" in category 
                                                                            else URIRef(skos + "closeMatch"),
                                                URIRef(schema + subcategory)))

                                if subcategory not in category_mappings_cache:
                                    G.add(triple=(URIRef(schema + subcategory),
                                                    RDFS.Class,
                                                    URIRef(yelpont + "SchemaCategory")))
                                    category_mappings_cache.add(subcategory)

                triple_file.write(
                    G.serialize(format='nt'))  # Writes to the .nt file the graph now containing RDF triples.

            except Exception as e:
                print(e)
                print(f"{subject} failed")

    triple_file.close()



if __name__ == "__main__":

    if os.path.isfile("/home/ubuntu/vol1/virtuoso/import/schema_mappings.nt.gz"):
        os.remove("/home/ubuntu/vol1/virtuoso/import/schema_mappings.nt.gz")
    else:
        print("Error: schema_mappings.nt.gz file not found")

    create_schema_file("yelp_academic_dataset_business.json")
    