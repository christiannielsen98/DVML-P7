import gzip
import json

from rdflib import Namespace, Graph, URIRef, Literal, BNode
from rdflib.namespace import RDFS

from UtilityFunctions.flatten_dict import flatten_dictionary
from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.schema_functions import get_schema_predicate, get_schema_type
from UtilityFunctions.get_uri import get_uri

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")


def create_nt_file(file_name: str):
    entity_name = file_name[22:-5]
    triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/yelp_{entity_name}.nt.gz", mode="at", encoding="utf-8")
    file_path = get_path(file_name)
    with open(file=file_path, mode="r") as file:
        for line in file:
            try:
                line = json.loads(line)
                G = Graph()
                if file_name in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json"]:
                    uri = business_uri
                elif file_name == 'yelp_academic_dataset_review.json':
                    uri = business_uri + line['business_id'] + '?hrid='
                else:  # user
                    uri = user_uri
                
                json_key = list(line.keys())[0]  # Key of subject
                subject = get_uri(file_name) + line[json_key]
                del line[json_key]
                G.add(triple=(URIRef(subject), 
                              URIRef(schema + 'url'), 
                              URIRef(uri + subject)))
                if file_name == "yelp_academic_dataset_review.json":
                    G.add(triple=(URIRef(example + 'user_id/' + line["user_id"]),  # Subject
                                  URIRef(schema + "author"),  # Predicate
                                  URIRef(get_uri(file_name) + subject)))  # Object
                    del line["user_id"]

                line = flatten_dictionary(line)  # Flattens the nested dictionary
                if file_name != 'yelp_academic_dataset_checkin.json':
                    G.add(triple=(URIRef(subject),
                                  RDFS.Class,
                                  URIRef(get_schema_type(entity_name))))

                for _predicate, _object in line.items():
                    if isinstance(_object, type(None)) or str(_object).lower() == "none":
                        pass

                    elif _predicate in ["categories", "date", "friends", "elite"]:  # String containing listed objects
                        _object = str(_object)
                        obj_lst = _object.split(", ") if _predicate != "elite" else _object.split(",")

                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        for obj in obj_lst:
                            if _predicate == "date":
                                obj = obj.replace(" ", "T")
                            G.add(triple=(URIRef(subject),  # Subject
                                          URIRef(predicate),  # Predicate
                                          Literal(obj, datatype=object_type)))  # Object

                    else:
                        if _predicate == "yelping_since":
                            _object = _object.replace(" ", "T")
                        predicate, object_type = get_schema_predicate(_predicate, _object, file_name)
                        G.add(triple=(URIRef(subject),  # Subject
                                      URIRef(predicate),  # Predicate
                                      Literal(_object, datatype=object_type)))  # Object
                triple_file.write(G.serialize(format='nt'))
            except Exception as e:
                print(e)
                print(subject, _predicate, _object)
    triple_file.close()


def create_tip_nt_file():
    file_name = "yelp_academic_dataset_tip.json"
    entity_name = file_name[22:-5]
    file_path = get_path(file_name)
    triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/yelp_{entity_name}.nt.gz", mode="at", encoding="utf-8")
    with open(file=file_path, mode="r") as file:
        for line in file:
            try:
                G = Graph()
                line = json.loads(line)

                b_node = BNode()

                subject = get_uri(file_name) + line["user_id"]
                del line["user_id"]

                # user, author, b_node
                G.add(triple=(URIRef(user_uri + subject),  # Subject
                              URIRef(schema + "author"),  # Predicate
                              Literal(b_node)))  # Object

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

                    G.add(triple=(URIRef(b_node),  # Subject
                                  URIRef(predicate),  # Predicate
                                  Literal(obj, datatype=object_type)))  # Object
                triple_file.write(G.serialize(format="nt"))
            except Exception as e:
                print(e)
                print(subject, _predicate, _object)
    triple_file.close()


if __name__ == "__main__":
    for _file in ["yelp_academic_dataset_business.json", "yelp_academic_dataset_checkin.json",
                  "yelp_academic_dataset_review.json", "yelp_academic_dataset_user.json"]:
        create_nt_file(file_name=_file)

    create_tip_nt_file()
