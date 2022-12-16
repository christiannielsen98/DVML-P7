import gzip
import json

import inflect
import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal, BNode
from rdflib.namespace import RDFS

from UtilityFunctions.dictionary_functions import flatten_dictionary
from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.schema_functions import get_schema_predicate, get_schema_type
from UtilityFunctions.get_uri import get_uri

schema = Namespace("https://schema.org/")
skos = Namespace("https://www.w3.org/2004/02/skos/core#")
business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")
yelpcat = Namespace("https://purl.archive.org/purl/yelp/business_categories#")
yelpont = Namespace("https://purl.archive.org/purl/yelp/ontology#")
yelpent = Namespace("https://purl.archive.org/purl/yelp/yelp_entities#")

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

        schema_category_mappings_df = pd.read_csv(get_path("class_mappings_manual.csv"))
        schema_category_mappings_dict = dict([(i, eval(x)) for i, x in zip(schema_category_mappings_df['YelpCategory'],
                                                                           schema_category_mappings_df['SchemaType'])])

        class_hierarchies = pd.read_csv(get_path("class_hierarchy.csv"))

        split_categories_df = pd.read_excel(get_path("split_categories.xlsx"), names=["category", "split_category"])
        split_categories_dict = dict([(i, x.split(', ')) for i, x in zip(split_categories_df['category'],
                                                                         split_categories_df['split_category'])])

        G = Graph()  # Initialize an empty graph
        for idx, row in class_hierarchies.iterrows():  # Adds class hierarchies to the graph
            G.add(triple=(URIRef(Namespace(row['type'])),
                          RDFS.subClassOf,
                          URIRef(Namespace(row['superType']))))

        triple_file.write(G.serialize(format='nt'))

    with open(file=file_path, mode="r") as file:

        # Namespaces needed for URIs
        if file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json"]:
            url = business_uri
        elif file_name == 'yelp_academic_dataset_user.json':
            url = user_uri
            
        category_cache = set()  # Cache for categories to avoid duplicates.
        category_mappings_cache = set()  # Cache for category mappings to avoid duplicates.

        # Iterate over every object in the JSON file as each object is one line.
        for line in file:
            try:
                line = json.loads(line)  # json.loads loads the JSON object into a dictionary.

                # If the file is reviews, the url depends on the line being iterated over.
                if file_name == 'yelp_academic_dataset_review.json':
                    url = business_uri + line['business_id'] + '?hrid='

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
                    G.add(triple=(URIRef(subject),
                                  URIRef(schema + "author"),
                                  URIRef(yelpent + 'user_id/' + line["user_id"])))
                    del line["user_id"]  # No longer need the this key/value pair.

                line = flatten_dictionary(line)  # Some values are dictionaries themselves, so we flatten them before proceeding

                # Assign an RDFS Class to every subject (checkin does not have its own subject).
                if file_name == 'yelp_academic_dataset_business.json':
                    G.add(triple=(URIRef(subject),
                                    RDFS.Class,
                                    URIRef(schema + "LocalBusiness")))

                    if line['categories']:
                        # Categories are initially one long comma-separated string.
                        categories = line['categories'].split(", ")
                        del line['categories']  # No longer need this key/value pair.
                        
                        for category in categories:
                            category = category.replace(' ', '_')  # Need to replace whitespace as we use it as URI
                            G.add(triple=(URIRef(subject),
                                            URIRef(schema + "category"),
                                            URIRef(yelpcat + category)))
                            
                            if category not in category_cache:
                                G.add(triple=(URIRef(yelpcat + category),
                                                RDFS.Class,
                                                URIRef(yelpont + "datasetCategory")))

                                G.add(triple=(URIRef(yelpcat + category),
                                              RDFS.subClassOf,
                                              URIRef(schema + "LocalBusiness")))    
                            
                                # schema_category_mappping_dict is the mappings to schema.org obtained by MODEL
                                if category.replace('_', ' ') in schema_category_mappings_dict.keys():
                                    mappings = schema_category_mappings_dict[category.replace('_', ' ')]
                                    # If there is only one mapping, it is an exactMatch
                                   
                                    # If there are multiple mappings add each mapping as a narrowMatch
                                    for subcategory in mappings:
                                        G.add(triple=(URIRef(yelpcat + category),
                                                      URIRef(skos + "narrowMatch") if "&" in category or "/" in category 
                                                                                   else URIRef(skos + "exactMatch"),
                                                      URIRef(schema + subcategory)))

                                        if subcategory not in category_mappings_cache:
                                            G.add(triple=(URIRef(schema + subcategory),
                                                          RDFS.Class,
                                                          URIRef(yelpont + "schemaCategory")))
                                            category_mappings_cache.add(subcategory)

                                # If the category is not in the mapping, we check if it is a split category,
                                # and if true, add each of the split categories (example) as narrowMatch
                                if category in split_categories_dict.keys():
                                    for subcategory in split_categories_dict[category]:
                                        G.add(triple=(URIRef(yelpcat + category),
                                                        URIRef(skos + "narrowMatch"),
                                                        URIRef(yelpcat + subcategory)))

                                        if subcategory not in category_mappings_cache:
                                            G.add(triple=(URIRef(yelpcat + subcategory),
                                                          RDFS.Class,
                                                          URIRef(yelpont + "yelpCategory")))
                                            category_mappings_cache.add(subcategory)

                                else:
                                    p = inflect.engine()
                                    lower_cat = category.lower()
                                    preprocessed_category = p.singular_noun(lower_cat)
                                    preprocessed_category = preprocessed_category if preprocessed_category else lower_cat

                                    G.add(triple=(URIRef(yelpcat + category),
                                                    URIRef(skos + "exactMatch"),
                                                    URIRef(yelpcat + preprocessed_category)))

                                    if preprocessed_category not in category_mappings_cache:
                                        G.add(triple=(URIRef(yelpcat + preprocessed_category),
                                                      RDFS.Class,
                                                      URIRef(yelpont + "yelpCategory")))
                                        category_mappings_cache.add(preprocessed_category)

                            category_cache.add(category)

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
                                      URIRef(predicate),  # E.g., hasBusinessParking, hashours
                                      URIRef(b_node)))  # Blank Node

                        blanknode_class = get_schema_type(_predicate)

                        G.add(triple=(URIRef(b_node),
                                      URIRef(RDFS.Class),
                                      URIRef(blanknode_class)))

                        for sub_predicate, sub_object in _object.items():
                            G.add(triple=(URIRef(b_node),
                                          URIRef(yelpont + "has" + sub_predicate),
                                          Literal(sub_object)))

                    elif _predicate in ["date", "friends", "elite"]:  # The values to these keys contains listed objects
                        _object = str(_object)
                        obj_lst = _object.split(", ") if _predicate != "elite" else _object.split(",")  # Splits the listed objects

                        # get_schema_predicate assigns returns a proper schema.org predicate based on the key
                        # and a proper object datatype.
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        if obj_lst:
                            for obj in obj_lst:
                                if _predicate == "date":
                                    obj = obj.replace(" ", "T")  # Cleans the date attribute
                                G.add(triple=(URIRef(subject),
                                              URIRef(predicate),
                                              Literal(obj, datatype=object_type)))

                    elif _predicate == "business_id":  # If we are dealing with a reivew, we add a link to the business
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        obj = yelpent + _object
                        
                        G.add(triple=(URIRef(subject),
                                      URIRef(predicate),
                                      URIRef(obj)))

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
                G.add(triple=(URIRef(b_node),
                              URIRef(schema + "author"),
                              URIRef(user_uri + subject)))

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
    from discord_webhook import DiscordWebhook
    import datetime
    begin_time = datetime.datetime.now()
    import os
    myfiles=["/home/ubuntu/vol1/virtuoso/import/yelp_business.nt.gz", 
             "/home/ubuntu/vol1/virtuoso/import/yelp_checkin.nt.gz", 
             "/home/ubuntu/vol1/virtuoso/import/yelp_review.nt.gz", 
             "/home/ubuntu/vol1/virtuoso/import/yelp_user.nt.gz", 
             "/home/ubuntu/vol1/virtuoso/import/yelp_tip.nt.gz"]
    for i in myfiles:
        ## If file exists, delete it ##
        if os.path.isfile(i):
            os.remove(i)
        else:    ## Show an error ##
            print("Error: %s file not found" % i)
    
    # create_nt_file(file_name="yelp_academic_dataset_business.json")
    files = [
        'yelp_academic_dataset_business.json',
        'yelp_academic_dataset_user.json',
        'yelp_academic_dataset_review.json',
        'yelp_academic_dataset_checkin.json'
    ]
    try:
        start = time.time()
        for i in files:
            _start = time.time()
            create_nt_file(file_name=i)
            print(f'For {i} It took', time.time()-_start, 'seconds.')
        start_tip = time.time()
        create_tip_nt_file()
        print(f'For tip It took', time.time()-start_tip, 'seconds.')
        print(f'In total it took', time.time()-start, 'seconds.')
        message = f'create_nt_files done in hh:mm:ss {datetime.datetime.now() - begin_time}'
    except Exception as e:
        message = f'create_nt_files failed in hh:mm:ss {datetime.datetime.now() - begin_time}\n{e}'
        print(e)
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1051908340772515860/2jd9XbteomjiPwZCuoiZ7WN4LGe-xJzUPC8P1xPBBpbyECu00PSIIfs8tARmkI78t88v', content=message).execute()