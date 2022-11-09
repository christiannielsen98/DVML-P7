import pandas as pd
from networkx import DiGraph
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from rdflib import Namespace, XSD

from UtilityFunctions.get_data_path import get_path
from UtilityFunctions.string_functions import long_com_substring, str_split

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

schema_classes = pd.read_csv(get_path("schemaorg-current-https-types.csv"))
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
        case "review_count":
            return schema + "reviewCount", XSD.string
        case "yelping_since":
            return schema + "dateCreated", XSD.dateTime
        case "business_id":
            return schema + "about", XSD.anyURI
        case "text":
            return schema + "description", XSD.string
        case "BusinessParking" | "GoodForMeal" | "Ambience" | "Music" | "BestNights" | "HairSpecializesIn" | "DietaryRestrictions" | "hours":
            return example + "has" + predicate.capitalize(), XSD.string  # TODO: Find something instead of example
        case _:  # If no schema.org predicate can be found, create predicate using example.org
            if isinstance(obj, str):
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
                return None
            return example + predicate, object_type


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
            return example + 'Tip'
        case _:  #
            print(f"Unknown schema type for entity: {entity}")


def get_class_mappings(substring_threshold=0.90, ratio_threshold=1 / 2):
    """
    This function is used to extract all business categories, and find their best schema.org type if it exists.
    :param substring_threshold: The threshold for how long the longest common substring should be
    :param ratio_threshold: The threshold for the ratio between the category and its mapping word lengths.
    :return: Returns a dictionary with category as key and mapped schema type as value.
    """

    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)
    schema = pd.read_csv(get_path("schemaorg-current-https-types.csv"))[["label", "subTypeOf"]]
    biz["categories"] = biz["categories"].apply(str_split)

    # Iterate over categories in sublists ('If sublist' checks if the sublist is None) and insert them into a large set.
    categories = list({category for sublist in biz["categories"].tolist() if sublist for category in sublist})
    category_mapping = dict()

    for category in categories:
        category_length = len(category)
        possible_classes = dict()

        for schema_type in schema["label"]:
            # Only adds a schema type as a match if the longest common substring is at least 90% of the category,
            # and if the ratio between the category and schema type is 50 % or larger.
            if long_com_substring(category, schema_type) >= category_length * substring_threshold:
                ratio = min(category_length, len(schema_type)) / max(category_length, len(schema_type))
                if ratio >= ratio_threshold:
                    possible_classes[schema_type] = ratio

        if possible_classes:  # An empty dict will return False
            best_pos_class = max(possible_classes, key=possible_classes.get)
            category_mapping[category] = best_pos_class

    return category_mapping


def class_hierarchy(dictionary):
    """
    This function is used to create the hiearchy only for the relevant schema.org types for this ontology.
    :param dictionary: Input here is the category to schema type mapping dictionary returned from get_class_mappings().
    :return: a dictionary with schema type as key and its supertype as value.
    """

    schema_df = pd.read_csv(get_path("schemaorg-current-https-types.csv"))[["id", "subTypeOf"]].dropna()
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

    return supertypes_df


if __name__ == "__main__":
    dct = {'Synagogues': 'Synagogue', 'Jewelry': 'JewelryStore', 'Preschools': 'Preschool',
           'International': 'InternationalTrial', 'Courthouses': 'Courthouse', 'Pharmacy': 'Pharmacy',
           'Grocery': 'GroceryStore', 'Insurance': 'InsuranceAgency', 'Electricians': 'Electrician',
           'Vegetarian': 'VegetarianDiet', 'Shopping': 'ShoppingCenter', 'Contractors': 'GeneralContractor',
           'Bowling': 'BowlingAlley', 'Embassy': 'Embassy', 'Parking': 'ParkingMap', 'Restaurants': 'Restaurant',
           'Halal': 'HalalDiet', 'Electronics': 'ElectronicsStore', 'Campgrounds': 'Campground',
           'Osteopaths': 'Osteopathic', 'Playgrounds': 'Playground', 'Apartments': 'Apartment', 'Kosher': 'KosherDiet',
           'Education': 'EducationEvent', 'Vegan': 'VeganDiet', 'Automotive': 'AutomotiveBusiness',
           'Tattoo': 'TattooParlor'}

    class_mapping_dict = get_class_mappings()
    class_mapping_df = pd.DataFrame(list(class_mapping_dict.items()), columns=['YelpCategory', 'SchemaType'])
    print(class_mapping_df)
    # class_mapping_df.to_csv(path_or_buf=get_path("class_mappings.csv"), index=False)

    # class_hierarchy_df = class_hierarchy(class_mapping_dict)
    # class_hierarchy_df.to_csv(path_or_buf=get_path("class_hierarchy.csv"), index=False)
