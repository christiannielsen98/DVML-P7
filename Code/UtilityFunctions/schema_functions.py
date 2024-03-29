import sys
import pandas as pd
from networkx import DiGraph
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from rdflib import Namespace, XSD
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import string_is_float



schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")
yelpont = Namespace("https://purl.archive.org/purl/yelp/yelp_ontology#")

schema_classes = pd.read_csv("Code/UtilityData/schemaorg-current-https-types.csv")
schema_classes.update(schema_classes.subTypeOf.str.replace('https://schema.org/', '', regex=False))


def get_schema_predicate(predicate, obj=None, file=None):
    """
    This match function gets as input keys and values from the Yelp JSON files and tries to map the keys to proper
    schema.org predicates and proper XSD datatypes. If no schema.org predicate can be found, create an example.org
    predicate based on the input "predicate" and with "obj" datatype as XSD datatype.
    :param predicate: A key from the JSON file
    :param obj: The value pair from the JSON file
    :param file: Used for special case of "date" if the file is checkin.
    :return: predicate and object + datatypes for the RDF triple.
    """
    match predicate:
        case "name":
            return schema + "legalName", XSD.string
        case "address":
            return schema + "address", XSD.string
        case "postal_code":
            return schema + "postalCode", XSD.string
        case "latitude":
            return schema + "latitude", XSD.decimal
        case "longitude":
            return schema + "longitude", XSD.decimal
        case "stars":
            return schema + "aggregateRating", XSD.decimal
        case "review_count":
            return schema + "reviewCount", XSD.integer
        case "is_open":
            return schema + "publicAccess", XSD.string
        case "categories":
            return schema + "category", XSD.string
        case "date":
            if file == "yelp_academic_dataset_checkin.json":
                return schema + "checkinTime", XSD.dateTime 
            else:
                return schema + "dateCreated", XSD.dateTime
        case "friends":
            return schema + "knows", XSD.string
        case "yelping_since":
            return schema + "dateCreated", XSD.dateTime
        case "business_id":
            return schema + "about", XSD.anyURI
        case "text":
            return schema + "description", XSD.string
        case "city":
            return yelpont + "locatedInCity", XSD.string
        case "state":
            return yelpont + "locatedInState", XSD.string
        case "BusinessParking" | "GoodForMeal" | "Ambience" | "Music" | "BestNights" | "HairSpecializesIn" | "DietaryRestrictions" | "hours":
            return yelpont + "has" + predicate.capitalize() if predicate == "hours" else yelpont + "has" + predicate, XSD.string
        # If no schema.org predicate can be found, create predicate using Yelp ontology.
        # Also assign the object datatype, by checking the original type.
        case _:  
            # For the case of strings, we also need to check if the string only contains digits or floats.
            if isinstance(obj, str):
                if obj.isdigit():
                    object_type = XSD.integer
                elif string_is_float(obj):
                    object_type = XSD.decimal
                else:
                    object_type = XSD.string
            elif isinstance(obj, int):
                object_type = XSD.integer
            elif isinstance(obj, float):
                object_type = XSD.decimal
            elif isinstance(obj, bool):
                object_type = XSD.boolean
            else:
                print("Error in SCHEMA!", "Type: ", type(obj))
                print(predicate, obj)
                pass
            return yelpont + predicate, object_type


def get_schema_type(entity: str):
    """
    This function assigns a schema.org (or example.org) type to a Yelp entity
    :param entity: The subject we want to assign a class to.
    :return: The proper class for the entity input.
    """

    match entity:
        case 'user':
            return schema + 'Person'
        case 'review':
            return schema + 'UserReview'
        case 'tip':
            return yelpont + 'Tip'
        case "BusinessParking":
            return schema + "ParkingFacility"
        case "GoodForMeal":
            return schema + "FoodService"
        case "Ambience" | "Music" | "BestNights" | "HairSpecializesIn" | "DietaryRestrictions":
            return schema + 'LocationFeatureSpecification'
        case "hours":
            return schema + 'OpeningHoursSpecification'
        case _:  #
            print(f"Unknown schema type for entity: {entity}")


def class_hierarchy(dictionary):
    """
    This function is used to create the hierarchy only for the relevant schema.org types for this ontology.
    :param dictionary: Input here is the category to schema type mapping dictionary returned from get_class_mappings().
    :return: a dataframe with schema type and its supertype(s).
    """

    schema_df = pd.read_csv("Code/UtilityData/schemaorg-current-https-types.csv")[["id", "subTypeOf"]]
    schema_df = schema_df.apply(
        lambda x: x.str.split(', ').explode())  # Some types have multiple supertypes, so we explode those rows.

    supertypes_dict = dict()

    graph = DiGraph()
    graph.add_edges_from(list(zip(schema_df["id"], schema_df["subTypeOf"])))  # Here we add EVERY row to the graph

    # We do a depth first search on the constructed graph starting at each type in the input dictionary.
    for _class in dictionary.values():
        supertypes = dfs_tree(graph, "https://schema.org/" + _class)
        edges = supertypes.edges()  # edges is a list of lists
        for edge in edges:
            supertypes_dict.setdefault(edge[0], set()).add(edge[1])

    supertypes_df = pd.DataFrame(list(supertypes_dict.items()), columns=['type', 'superType'])
    supertypes_df = supertypes_df.explode("superType")
    supertypes_df.dropna(inplace=True)

    return supertypes_df

if __name__ == "__main__":
    class_mappings_manual_df = pd.read_csv("Code/UtilityData/class_mappings_manual.csv")
    class_mappings_manual_df['SchemaType'] = class_mappings_manual_df.SchemaType.str.split(",")
    class_mappings_manual_df = class_mappings_manual_df.explode('SchemaType')
    class_mapping_dict = pd.Series(class_mappings_manual_df.SchemaType.values,index=class_mappings_manual_df.YelpCategory).to_dict()
    for key, value in class_mapping_dict.items():
        class_mapping_dict[key] = value.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")
    
    class_hierarchy_df = class_hierarchy(class_mapping_dict)
    class_hierarchy_df.to_csv(path_or_buf="Code/UtilityData/class_hierarchy.csv", index=False)

