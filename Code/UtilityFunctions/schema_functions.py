import pandas as pd
from get_data_path import get_path
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
            return schema + "latitude", XSD.float
        case "longitude":
            return schema + "longitude", XSD.float
        case "stars":
            return schema + "starRating", XSD.float
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
        case _:  # If no schema.org predicate can be found, create predicate using example.org
            if isinstance(obj, str):
                object_type = XSD.string
            elif isinstance(obj, int):
                object_type = XSD.integer
            elif isinstance(obj, float):
                object_type = XSD.float
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
        case 'user':
            return schema + 'Person'
        case 'review':
            return schema + 'Review'
        case 'tip':
            return example + 'Tip'
        case _:  # This case happens for the business file.
            get_classes(entity)


def long_com_substring(st1, st2):
    """
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


def get_classes(entity: str):
    """
    :param entity: The RDF entity we want to check if it has a possible type in schema.org
    :return: The type to add as a class to the entity.
    """

    possible_classes = dict()
    entity_length = len(entity)

    for _type in list(schema_classes['label']): # schema_classes['label'] is all types in schema.org
        if long_com_substring(entity, _type) >= entity_length * 0.9:
            # If the longest common substring between the entity and schema.org types is similar with 90 %,
            # we add the type as key and the ratio between the two strings as value.
            ratio = entity_length / len(_type)
            possible_classes[_type] = ratio

    if len(possible_classes) > 0:
        return schema + max(possible_classes, key=possible_classes.get)  # Return the highest ratio key as the entities type.
    else:
        return schema + 'LocalBusiness'

if __name__ == "__main__":

    import time

    t1 = time.time()
    test2 = get_classes('Restaurants')
    print(test2)
    t2 = time.time()
    print(t2-t1)


