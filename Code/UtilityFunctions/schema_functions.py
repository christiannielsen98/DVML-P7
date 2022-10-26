import pandas as pd
from Code.UtilityFunctions.get_data_path import get_path
from rdflib import Namespace, XSD

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

schema_classes = pd.read_csv(get_path("schemaorg-current-https-types.csv"))
schema_classes.update(schema_classes.subTypeOf.str.replace('https://schema.org/', '', regex=False))


def get_schema_predicate(predicate, obj, file):
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
            return schema + "name", XSD.string
        case "address":
            return schema + "address", XSD.string
        case "city":
            return schema + "location", XSD.string
        case "state":
            return schema + "addressRegion", XSD.string
        case "postal_code":
            return schema + "postalCode", XSD.string  # integer?
        case "latitude":
            return schema + "latitude", XSD.decimal
        case "longitude":
            return schema + "longitude", XSD.decimal
        case "stars":
            return schema + "starRating", XSD.decimal
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
            return example + "has" + predicate.capitalize(), XSD.string  # TODO: Find
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
    This function assigns a schema.org (or example.org) Class to a Yelp entity
    :param entity: The subject we want to assign a Class to
    :return: The proper class for the entity input
    """

    match entity:
        case 'business':
            return schema + "LocalBusiness"
        case 'user':
            return schema + 'Person'
        case 'review':
            return schema + 'UserReview'
        case 'tip':
            return example + 'Tip'
        case _:  # 
            print(f"Unknown schema type for entity: {entity}")


def long_com_substring(st1, st2):
    """
    This function is used for matching business categories with schema.org types.
    :param st1: The string we want to check for.
    :param st2: The string we check longest substring (st1) in.
    :return: Returns the length of the longest substring
    """

    ans = 0
    for a in range(len(st1)):
        for b in range(len(st2)):
            k = 0
            while (a + k) < len(st1) and (b + k) < len(st2) and st1[a + k] == st2[b + k]:
                k = k + 1
            ans = max(ans, k)

    return ans


def str_split(string):
    if isinstance(string, str):
        return string.split(", ")
    else:
        return string


def get_class_mappings(file_path):
    """
    This function is used to extract all business categories, and find their best schema.org type if it exists. 
    :param file: The file to be read as a dataframe. This function is only used for the business JSON.
    :return: Returns a dictionary with category as key and mapped schema type as value.
    """

    biz = pd.read_json(file_path, lines=True)#["categories"]
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
            if long_com_substring(category, schema_type) >= category_length * 0.90:
                ratio = category_length / len(schema_type)
                if ratio >= 1/2:
                    possible_classes[schema_type] = ratio

        if possible_classes:  # An empty dict will return False
            best_pos_class = max(possible_classes, key=possible_classes.get)  # Get the schema.org type with highest ratio
            category_mapping[category] = best_pos_class

    return category_mapping


def class_hierarchy(dictionary):
    """
    This function is used to create the hiearchy only for the relevant schema.org types for this ontology.
    :param dictionary: Input here is the category to schema type mapping dictionary returned from get_class_mappings().
    :return: a dictionary with schema type as key and its supertype as value.
    """
    from networkx import DiGraph
    from networkx.algorithms.traversal.depth_first_search import dfs_tree

    schema = pd.read_csv(get_path("schemaorg-current-https-types.csv"))[["id", "subTypeOf"]].dropna()

    supertypes_set = set()

    graph = DiGraph()
    graph.add_edges_from(list(zip(schema["id"], schema["subTypeOf"]))) # Here we add EVERY row to the graph

    for _class in dictionary.values():
        supertypes = dfs_tree(graph, "https://schema.org/" + _class)
        supertypes_set.update(set(supertypes.nodes()))

    res_df = schema[schema["id"].isin(supertypes_set)]  # Extracts all relevant rows
    res_df = res_df.apply(lambda x: x.str.split(', ').explode()) # Some types have multiple supertypes, so we explode those rows.
    res_df = res_df.set_index('id').to_dict()['subTypeOf'] # Convert to dict with id as key and supertype as value

    return res_df


if __name__ == "__main__":
    dct = {'Synagogues': 'Synagogue', 'Jewelry': 'JewelryStore', 'Preschools': 'Preschool', 'International': 'InternationalTrial', 'Courthouses': 'Courthouse', 'Pharmacy': 'Pharmacy', 'Grocery': 'GroceryStore', 'Insurance': 'InsuranceAgency', 'Electricians': 'Electrician', 'Vegetarian': 'VegetarianDiet', 'Shopping': 'ShoppingCenter', 'Contractors': 'GeneralContractor', 'Bowling': 'BowlingAlley', 'Embassy': 'Embassy', 'Parking': 'ParkingMap', 'Restaurants': 'Restaurant', 'Halal': 'HalalDiet', 'Electronics': 'ElectronicsStore', 'Campgrounds': 'Campground', 'Osteopaths': 'Osteopathic', 'Playgrounds': 'Playground', 'Apartments': 'Apartment', 'Kosher': 'KosherDiet', 'Education': 'EducationEvent', 'Vegan': 'VeganDiet', 'Automotive': 'AutomotiveBusiness', 'Tattoo': 'TattooParlor'}
    print(class_hierarchy(dct))

    # from networkx import DiGraph
    # from networkx.algorithms.traversal.depth_first_search import dfs_tree
    #
    # schema = pd.read_csv(get_path("schemaorg-current-https-types.csv"))[["id", "subTypeOf"]]
    #
    # graph = DiGraph()
    # graph.add_edges_from(schema[['id', 'subTypeOf']].to_records(index=False))  # Here we add EVERY row to the graph

    # print(graph.edges)

    # supertypes = dfs_tree(graph, "https://schema.org/" + dct["Synagogues"])
    # print(supertypes)

    # import time
    #
    # t1 = time.time()
    # test2 = get_class_mappings('Restaurants')
    # print(test2)
    # t2 = time.time()
    # print(t2-t1)



