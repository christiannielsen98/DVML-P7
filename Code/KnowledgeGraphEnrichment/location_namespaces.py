from rdflib import Namespace

schema = Namespace("https://schema.org/")
skos = Namespace("https://www.w3.org/2004/02/skos/core#")
business_uri = Namespace("https://www.yelp.com/biz/")
user_uri = Namespace("https://www.yelp.com/user_details?userid=")
yelpcat = Namespace("https://purl.archive.org/purl/yelp/business_categories#")
yelpont = Namespace("https://purl.archive.org/purl/yelp/ontology#")
yelpent = Namespace("https://purl.archive.org/purl/yelp/yelp_entities#")
wiki = Namespace("https://www.wikidata.org/entity/")
population_predicate = wiki + "P1082"  # P1082 = population
location_predicate = wiki + "P131"  # P131 = located in the administrative territorial entity
instance_of_predicate = wiki + "P31"  # P31 = instance of
