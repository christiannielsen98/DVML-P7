from rdflib import Namespace, URIRef, Literal, XSD

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")


def return_predicate(predicate, obj):
    match predicate:
        case "name":
            return schema + "name", XSD.string
        case "address":
            return schema + "address", XSD.string
        case "city":
            return schema + "location", XSD.string
        case "state":
            return schema + "location", XSD.string
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
        case _:
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
                return None
            return example + predicate, object_type


if __name__ == "__main__":
    print(return_predicate("test"))
