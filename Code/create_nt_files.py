import gzip
import json

import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal, BNode
from rdflib.namespace import RDFS

from UtilityFunctions.dictionary_functions import flatten_dictionary
from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.schema_functions import get_schema_predicate, get_schema_type
from UtilityFunctions.get_uri import get_uri

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")  # TODO: Find a better Namespace than example
skos = Namespace("https://www.w3.org/2004/02/skos/core#")

business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")
category_uri = Namespace("https://www.yelp.com/category/")


def create_nt_file(file_name: str):
    """
    This function takes as input one of four Yelp JSON files (The tip file is handled in different function), and
    transforms the objects in that file to RDF format, and writes them to a output file.
    :param file_name: The Yelp JSON file to transform to RDF.
    :return: a .nt.gz file with Yelp data in RDF format.
    """
    entity_name = file_name[22:-5]  # Either business, user, checkin or review
    triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/yelp_{entity_name}.nt.gz", mode="at",
                            encoding="utf-8")
    # triple_file = gzip.open(filename=f"yelp_{entity_name}.nt.gz", mode="at",
    #                         encoding="utf-8")
    file_path = get_path(file_name)

    if file_name == "yelp_academic_dataset_business.json":

        schema_category_mappings_df = pd.read_csv(get_path("class_mappings.csv"))
        schema_category_mappings_dict = dict([(i, eval(x)) for i, x in zip(schema_category_mappings_df['YelpCategory'],
                                                                           schema_category_mappings_df['SchemaType'])])

        class_hierarchies = pd.read_csv(get_path("class_hierarchy.csv"))

        split_categories_df = pd.read_excel(get_path("split_categories.xlsx"), names=["category", "split_category"])
        split_categories_dict = dict([(i, x.split(', ')) for i, x in zip(split_categories_df['category'],
                                                                         split_categories_df['split_category'])])

        G = Graph()
        for idx, row in class_hierarchies.iterrows():  # Adds class hierarchies to the graph
            G.add(triple=(URIRef(Namespace(row['type'])),
                          RDFS.subClassOf,
                          URIRef(Namespace(row['superType']))))

        triple_file.write(G.serialize(format='nt'))

        # Load location information based on Google API retrieved data.
        with open(file=get_path("location_unique.json"), mode="r") as file:  # TODO: Load new data.
            location_dict = json.load(file)

        # Required because when using "with open" the file is overwritten.
        location_dict = location_dict

    with open(file=file_path, mode="r") as file:
        # Namespaces needed for URIs
        if file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json"]:
            url = business_uri
        elif file_name == 'yelp_academic_dataset_review.json':
            url = business_uri + line['business_id'] + '?hrid='
        else:
            url = user_uri
            
        category_cache = set()  # Cache for categories to avoid duplicates.
        category_mappings_cache = set()  # Cache for category mappings to avoid duplicates.
        # Iterate over every object in the JSON file as each object is one line.
        for line in file:
            try:
                line = json.loads(line)  # json.loads loads the JSON object into a dictionary.
                G = Graph()  # Initialize a empty graph object to write a RDF triple to.

                json_key = list(line.keys())[0]  # Each dictionary has the ID as the value to the first key
                subject = get_uri(file_name) + line[json_key]  # get_uri makes sure the ID is a proper URI.
                

                # Creates a triple pointing to the subjects corresponding URL (Best practice).
                G.add(triple=(URIRef(subject),  # Subject
                              URIRef(schema + 'url'),  # Predicate
                              URIRef(url + line[json_key])))  # Object
                
                del line[json_key]  # After assigning the URI to the subject variable, we no longer need the first key/value pair
                # For reviews create a special triple making a connection between user and the review.
                if file_name == "yelp_academic_dataset_review.json":
                    G.add(triple=(URIRef(get_uri(file_name) + subject),
                                  URIRef(schema + "author"),
                                  URIRef(example + 'user_id/' + line["user_id"])))
                    del line["user_id"]  # No longer need the this key/value pair.

                line = flatten_dictionary(line)  # Some values are dictionaries themselves, so we flatten them before proceeding

                # Assign an RDFS Class to every subject (checkin does not have its own subject).
                if file_name == 'yelp_academic_dataset_business.json':
                    
                    if line['categories']:
                        # Categories are initially one long comma-separated string.
                        categories = line['categories'].split(", ")
                        del line['categories']  # No longer need this key/value pair.
                        
                        for category in categories:
                            category = category.replace(' ', '_')  # Need to replace whitespace as we use it as URI
                            G.add(triple=(URIRef(subject),
                                            URIRef(schema + "category"),
                                            URIRef(category_uri + category)))
                            
                            if category not in category_cache:
                                G.add(triple=(URIRef(category_uri + category),
                                                RDFS.Class,
                                                URIRef(example + "yelpCategory")))

                                G.add(triple=(URIRef(category_uri + category),
                                              RDFS.subClassOf,
                                              URIRef(schema + "LocalBusiness")))    
                            
                                # schema_category_mappping_dict is the mappings to schema.org obtained by MODEL
                                if category.replace('_', ' ') in schema_category_mappings_dict.keys():
                                    mappings = schema_category_mappings_dict[category.replace('_', ' ')]
                                    # If there is only one mapping, it is an exactMatch
                                   
                                    # If there are multiple mappings add each mapping as a narrowMatch
                                    for subcategory in mappings:
                                        G.add(triple=(URIRef(category_uri + category),
                                                      URIRef(skos + "narrowMatch") if "&" in category or "/" in category 
                                                                                   else URIRef(skos + "exactMatch"),
                                                      URIRef(schema + subcategory)))
                                        if subcategory not in category_mappings_cache:
                                            G.add(triple=(URIRef(schema + subcategory),
                                                          RDFS.Class,
                                                          URIRef(example + "schemaCategory")))
                                            category_mappings_cache.add(subcategory)

                                # If the category is not in the mapping, we check if it is a split category,
                                # and if true, add each of the split categories (example) as narrowMatch
                                elif category in split_categories_dict.keys():
                                    for subcategory in split_categories_dict[category]:
                                        G.add(triple=(URIRef(category_uri + category),
                                                        URIRef(skos + "narrowMatch"),
                                                        URIRef(example + subcategory)))

                                        if subcategory not in category_mappings_cache:
                                            G.add(triple=(URIRef(example + subcategory),
                                                          RDFS.Class,
                                                          URIRef(example + "exampleCategory")))
                                            category_mappings_cache.add(subcategory)

                                # If the category is not mapped AND not split, add a corresponding example category
                                # as an exactMatch.
                                else:
                                    G.add(triple=(URIRef(category_uri + category),
                                                    URIRef(skos + "exactMatch"),
                                                    URIRef(example + category)))

                                    if subcategory not in category_mappings_cache:
                                            G.add(triple=(URIRef(example + subcategory),
                                                          RDFS.Class,
                                                          URIRef(example + "exampleCategory")))
                                            category_mappings_cache.add(subcategory)
                            category_cache.add(category)

                    # Add location information to the business based on Google API retrieved data.
                    # TODO: implement new method of adding location information.
                    del [line['city'], line['state']]
                    location_rounded = f"{round(line['latitude'], 2)},{round(line['longitude'], 2)}"
                    for location_predicate, location_value in location_dict[location_rounded].items():
                        if location_value != None:
                            G.add(triple=(URIRef(subject),
                                            URIRef(example + "locatedIn" + location_predicate),
                                            URIRef(example + location_value.replace(" ", "_"))))

                elif file_name != 'yelp_academic_dataset_checkin.json':  # Adds a class to Users, Reviews and Tips

                    # get_schema_type returns the class for subjects.
                    subject_class = get_schema_type(entity_name)

                    G.add(triple=(URIRef(subject),
                                  RDFS.Class,
                                  URIRef(subject_class)))

                # Now we iterate over the rest of the key/value pairs and transform them to RDF format.
                for _predicate, _object in line.items():
                    try:
                        _object = eval(_object)
                        if _object == Ellipsis:  # Due to no text in a review
                            _object = "..."
                    except (TypeError, SyntaxError, NameError, AttributeError):
                        pass  # if the object cannot evaluate to a python object, we keep it as a string.
                    if isinstance(_object, type(None)) or str(_object).lower() == "null":  # Handle missng data in the JSON
                        continue

                    elif isinstance(_object, dict):
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        b_node = BNode()

                        G.add(triple=(URIRef(subject),
                                      URIRef(predicate),  # E.g., hasBusinessParking, hasHours
                                      Literal(b_node)))  # Blank Node

                        for sub_predicate, sub_object in _object.items():
                            G.add(triple=(URIRef(b_node),
                                          URIRef(example + "has" + sub_predicate),
                                          Literal(sub_object)))

                    elif _predicate in ["date", "friends", "elite"]:  # The values to these keys contains listed objects
                        _object = str(_object)
                        obj_lst = _object.split(", ") if _predicate != "elite" else _object.split(",")  # Splits the listed objects

                        # get_schema_predicate assigns returns a proper schema.org predicate based on the key
                        # and a proper object datatype.
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        for obj in obj_lst:
                            if _predicate == "date":
                                obj = obj.replace(" ", "T")  # Cleans the date attribute
                            G.add(triple=(URIRef(subject),
                                          URIRef(predicate),
                                          Literal(obj, datatype=object_type)))

                    else:
                        if _predicate == "yelping_since":
                            _object = _object.replace(" ", "T")

                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        G.add(triple=(URIRef(subject),
                                      URIRef(predicate),
                                      Literal(_object, datatype=object_type)))

                triple_file.write(
                    G.serialize(format='nt'))  # Writes to the .nt file the graph now containing a RDF triple.

            except Exception as e:
                print(e)
                print(subject, _predicate, _object)

    triple_file.close()


def create_tip_nt_file():
    """
    Special case of the create_nt_file function. This function transforms the tip JSON file to RDF format.
    We do this in a special function because this transformation requires blank nodes.
    :return: A .nt.gz file with Yelp tip data in RDF format.
    """

    file_name = "yelp_academic_dataset_tip.json"
    entity_name = file_name[22:-5]
    file_path = get_path(file_name)
    triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/yelp_{entity_name}.nt.gz", mode="at",
                            encoding="utf-8")

    with open(file=file_path, mode="r") as file:
        for line in file:
            try:
                line = json.loads(line)
                G = Graph()
                b_node = BNode()

                subject = line["user_id"]

                # get_schema_type returns the class for subjects.
                subject_class = get_schema_type(entity_name)
                del line["user_id"]

                # Creates the edge between a user and their tip
                G.add(triple=(URIRef(user_uri + subject),
                              URIRef(schema + "author"),
                              Literal(b_node)))

                # Assigns a RDFS Class to the blank node.
                G.add(triple=(URIRef(b_node),
                              RDFS.Class,
                              URIRef(subject_class)))

                for _predicate, _object in line.items():
                    predicate, object_type = get_schema_predicate(_predicate, _object, file_name)

                    if _predicate == "date":
                        obj = _object.replace(" ", "T")
                    elif _predicate == "business_id":
                        obj = business_uri + _object
                    else:
                        obj = _object

                    G.add(triple=(URIRef(b_node),
                                  URIRef(predicate),
                                  Literal(obj, datatype=object_type)))

                triple_file.write(G.serialize(format="nt"))

            except Exception as e:
                print(e)
                print(subject, _predicate, _object)

    triple_file.close()


if __name__ == "__main__":
    import time

    # create_nt_file(file_name="yelp_academic_dataset_business.json")
    files = [
        'yelp_academic_dataset_business.json',
        'yelp_academic_dataset_user.json',
        'yelp_academic_dataset_review.json',
        'yelp_academic_dataset_checkin.json'
    ]
    start = time.time()
    for i in files:
        _start = time.time()
        create_nt_file(file_name=i)
        print(f'For {i} It took', time.time()-_start, 'seconds.')
    start_tip = time.time()
    create_tip_nt_file()
    print(f'For tip It took', time.time()-start_tip, 'seconds.')
    print(f'In total it took', time.time()-start, 'seconds.')
