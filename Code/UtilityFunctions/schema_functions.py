from rdflib import Namespace, XSD

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")


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


def get_schema_type(entity):
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
            return schema + 'Review'
        case 'tip':
            return example + 'Tip'


if __name__ == "__main__":
    print(get_schema_predicate("test"))
