import gzip
import json

import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal, BNode
from rdflib.namespace import RDFS

from UtilityFunctions.dictionary_functions import flatten_dictionary
from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.string_functions import
from UtilityFunctions.schema_functions import get_schema_predicate, get_schema_type, get_class_mappings, class_hierarchy
from UtilityFunctions.get_uri import get_uri

from Code.Development.create_categories_nt_file import split_words, split_words_inc_slash

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")


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
        class_mappings = get_class_mappings()
        class_hierarchies = pd.read_csv(get_path("class_hierarchy.csv"))

        G = Graph()
        for idx, row in class_hierarchies.iterrows():
            G.add(triple=(URIRef(Namespace(row['type'])),
                          RDFS.subClassOf,
                          URIRef(Namespace(row['superType']))))

        triple_file.write(G.serialize(format='nt'))  # Writes to the .nt file the graph now containing a RDF triple.

        # Load location information based on Google API retireved data.
        with open(file=get_path("location_unique.json"), mode="r") as file:
            location_dict = json.load(file)

        # Required...
        location_dict = location_dict

    with open(file=file_path, mode="r") as file:
        for line in file:
            # Iterates over every object in the JSON file, as each object is one line.
            try:
                line = json.loads(line)  # json.loads loads the JSON object into a dictionary.
                G = Graph()  # initialize a empty graph object to write a RDF triple to.

                # business and checkin both use the business Namespace, reviews uses a custom one, and user also has its own.
                if file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json"]:
                    uri = business_uri
                elif file_name == 'yelp_academic_dataset_review.json':
                    uri = business_uri + line['business_id'] + '?hrid='
                else:  #
                    uri = user_uri

                json_key = list(line.keys())[0]  # Each dictionary has the ID as the value to the first key
                subject = get_uri(file_name) + line[json_key]  # get_uri makes sure the ID is a proper URI.
                del line[json_key]  # After assigning the URI to the subject variable, we no longer need the first key/value pair

                # Creates a triple pointing to the subjects corresponding URL (Best practice).
                G.add(triple=(URIRef(subject),  # Subject
                              URIRef(schema + 'url'),  # Predicate
                              URIRef(uri + subject)))  # Object

                # For reviews create a special triple making a connection between user and the review.
                if file_name == "yelp_academic_dataset_review.json":
                    G.add(triple=(URIRef(example + 'user_id/' + line["user_id"]),
                                  URIRef(schema + "author"),
                                  URIRef(get_uri(file_name) + subject)))
                    del line["user_id"]  # No longer need the this key/value pair.

                line = flatten_dictionary(line)  # Some values are dictionaries themselves, so we flatten them before proceeding

                # Assigns a RDFS Class to every subject (checkin does not have its own subject).
                if file_name != 'yelp_academic_dataset_checkin.json':
                    if file_name == 'yelp_academic_dataset_business.json':
                        if line['categories']:
                            # Get 'categories' key, unpack all its values, and run them through get_schema_type.
                            # If the specific category has a match in schema.org types CSV file, add that as a Class.
                            # If not we just add the parent class LocalBusiness.

                            possible_types = line['categories'].split(", ")
                            
                            for pos_type in possible_types:
                                # schema_type = get_schema_type(pos_type)
                                if pos_type in class_mappings.keys():
                                    G.add(triple=(URIRef(subject),
                                                  RDFS.Class,
                                                  URIRef(class_mappings[pos_type])))
                                else:
                                    G.add(triple=(URIRef(subject),
                                                  RDFS.Class,
                                                  URIRef(example + pos_type.replace(" ", "_"))))  # Fix " " in URI

                        # Add location information to the business based on Google API retrieved data.
                        del [line['city'], line['state']]
                        location_rounded = f"{round(line['latitude'], 2)},{round(line['longitude'], 2)}"
                        for location_predicate, location_value in location_dict[location_rounded].items():
                            if location_value is not None:
                                G.add(triple=(URIRef(subject),
                                              URIRef(example + "locatedIn" + location_predicate),
                                              URIRef(example + location_value.replace(" ", "_"))))

                    else:
                        G.add(triple=(URIRef(subject),
                                      RDFS.Class,
                                      URIRef(get_schema_type(entity_name))))

                # Now we iterate over the rest of the key/value pairs and transform them to RDF format.
                for _predicate, _object in line.items():
                    try:
                        _object = eval(_object)
                        if _object == Ellipsis:  # Due to no text in a review
                            _object = "..."
                    except (TypeError, SyntaxError, NameError, AttributeError):
                        pass
                    if isinstance(_object, type(None)) or str(_object).lower() in ["none", "null"]:  # Why do we do this?
                        pass

                    elif isinstance(_object, dict):
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        b_node = BNode()

                        G.add(triple=(URIRef(subject),
                                      URIRef(predicate),  # E.g., hasBusinessParking, hasHours
                                      Literal(b_node)))  # Blank Node

                        for __predicate, __object in _object.items():
                            G.add(triple=(URIRef(b_node),
                                          URIRef(example + "has" + __predicate),
                                          Literal(__object)))

                    elif _predicate in ["categories", "date", "friends", "elite"]:  # The values to these keys contains listed objects
                        _object = str(_object)
                        obj_lst = _object.split(", ") if _predicate != "elite" else _object.split( ",")  # Splits the listed objects

                        # get_schema_predicate assigns returns a proper schema.org predicate based on the key and a proper object datatype.
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        for obj in obj_lst:
                            if _predicate == "date":
                                obj = obj.replace(" ", "T")  # Cleans the date attribute
                            G.add(triple=(URIRef(subject),
                                          URIRef(predicate),
                                          Literal(obj, datatype=object_type)))

                    else:
                        if _predicate == "yelping_since":
                            _object = _object.replace(" ", "T")  # Cleans the yelping_since attribute

                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        G.add(triple=(URIRef(subject),
                                      URIRef(predicate),
                                      Literal(_object, datatype=object_type)))

                triple_file.write(G.serialize(format='nt'))  # Writes to the .nt file the graph now containing a RDF triple.

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

                subject = get_uri(file_name) + line["user_id"]
                del line["user_id"]

                # Creates the edge between a user and their tip
                G.add(triple=(URIRef(user_uri + subject),
                              URIRef(schema + "author"),
                              Literal(b_node)))

                # Assigns a RDFS Class to the blank node.
                G.add(triple=(URIRef(b_node),
                              RDFS.Class,
                              URIRef(get_schema_type(entity_name))))

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
    # create_nt_file(file_name="yelp_academic_dataset_business.json")
    files = [
        'yelp_academic_dataset_business.json',
        'yelp_academic_dataset_user.json',
        'yelp_academic_dataset_review.json',
        'yelp_academic_dataset_checkin.json'
    ]
    for i in files:
        create_nt_file(file_name=i)
    create_tip_nt_file()
