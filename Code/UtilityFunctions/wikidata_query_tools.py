from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from Code.UtilityFunctions.get_data_path import get_path
import sys
import requests
from math import ceil

def wikidata_query(sparql_query: str):
    # From https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Cats
    user_agent = "Yelp knowledge graph mapping/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_df = pd.json_normalize(results['results']['bindings'])
    return results_df


def retrieve_wikidata_claims(item_list):
    """
    Sends a request to the Wikidata API and transform the data from JSON into a dictionary to
    extract the claims each property has.
    :param item_list: A list with up to 50 wikidata items written with Q-code
    :return: A nested list, with all the properties each item has
    """
    # Creates the query by seperating each item with "|"
    item_list_query = ""
    for item in range(len(item_list)):
        if item == (len(item_list) - 1):
            item_list_query += item_list[item]
        else:
            item_list_query += item_list[item] + "%7C"

    # The string with API wbgetentities to find multiple items in an optimal format
    URL = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={item_list_query}&props=claims&languages=en&formatversion=2"

    # Opens a HTMl session and gets the DATA from the API
    with requests.Session() as S:
        DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())
    # Appends the properties of each item to a nested list
        
    nested_dict = {}
    for entity in DATA["entities"]:
        try:
            nested_dict[entity] = list(DATA["entities"][entity]["claims"].values())
        except:
            pass

    return nested_dict