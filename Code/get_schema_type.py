from rdflib import Namespace

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")

def get_schema_type(entity):
    match entity:
        case 'business':
            return schema + "LocalBusiness"
        case 'user':
            return schema + 'Person'
        case 'review':
            return schema + 'Review'
        case 'tip':
            return example + 'Tip'
