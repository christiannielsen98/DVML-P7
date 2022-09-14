from rdflib import Namespace, Graph, URIRef, Literal, BNode, XSD
import json

from get_schema_predicate import return_predicate
from flatten_dict import flatten_dictionary
from get_data_path import get_path


schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")




for file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json", "yelp_academic_dataset_review.json", "yelp_academic_dataset_user.json"]:
    G = Graph()
    if file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json", "yelp_academic_dataset_review.json"]:
        uri = business_uri
    else:  # user
        uri = user_uri

    file_path = get_path(file_name)
    with open(file=file_path, mode="r") as file:
        for line in file:
            try:
                line = json.loads(line)

                json_key = list(line.keys())[0]  # Key of subject
                subject = line[json_key]
                del line[json_key]

                if file_name == "yelp_academic_dataset_review.json":
                    G.add(triple=(URIRef(user_uri + line["user_id"]), # Subject
                                  URIRef(schema + "author"), # Predicate
                                  Literal(subject, datatype=XSD.anyURI))) # Object
                    del line["user_id"]

                    uri = uri + line['business_id'] + "?hrid=" + subject # Other uri for review

                line = flatten_dictionary(line) # Flattens the nested dictionary

                for _predicate, _object in line.items():
                    if isinstance(_object, type(None)) or str(_object).lower() == "none":
                        pass

                    elif _predicate in ["categories", "date", "friends", "elite"]: # String containing listed objects
                        _object = str(_object)
                        obj_lst = _object.split(", ") if _predicate != "elite" else _object.split(",")

                        predicate, object_type = return_predicate(_predicate, _object, file_name)
                        for obj in obj_lst:
                            if _predicate == "date":
                                obj = obj.replace(" ", "T")

                            G.add(triple=(URIRef(uri + subject), # Subject
                                          URIRef(predicate), # Predicate
                                          Literal(obj, datatype=object_type))) # Object

                    else:
                        if _predicate == "yelping_since":
                            _object = _object.replace(" ", "T")
                        predicate, object_type = return_predicate(_predicate, _object, file_name)
                        G.add(triple=(URIRef(uri + subject), # Subject
                                      URIRef(predicate), # Predicate
                                      Literal(_object, datatype=object_type))) # Object

            except Exception as e:
                print(e)
                print(subject, _predicate, _object)
    G.serialize(destination=f"/home/ubuntu/vol1/{file_name[:-5]}.ttl")

G = Graph()

file_name = "yelp_academic_dataset_tip.json"
file_path = get_path(file_name)

with open(file=file_path, mode="r") as file:
    for line in file:
        try:
            line = json.loads(line)

            b_node = BNode()

            subject = line["user_id"]
            del line["user_id"]

            # user, author, b_node
            G.add(triple=(URIRef(user_uri + subject), # Subject
                          URIRef(schema + "author"), # Predicate
                          Literal(b_node))) # Object

            for _predicate, _object in line.items():
                predicate, object_type = return_predicate(_predicate, _object, file_name)

                if _predicate == "date":
                    obj = _object.replace(" ", "T")
                elif _predicate == "business_id":
                    obj = business_uri + _object
                else:
                    obj = _object

                G.add(triple=(URIRef(b_node), # Subject
                              URIRef(predicate), # Predicate
                              Literal(obj, datatype=object_type))) # Object

        except Exception as e:
            print(e)
            print(subject, _predicate, _object)

G.serialize(destination="/home/ubuntu/vol1/yelp_academic_dataset_tip.ttl")

