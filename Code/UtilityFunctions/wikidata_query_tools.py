import sys

import pandas as pd
import requests
from SPARQLWrapper import SPARQLWrapper, JSON


def wikidata_query(sparql_query: str):
    """
    It takes a SPARQL query as a string, and returns a pandas dataframe of the results
    
    :param sparql_query: the query you want to run
    :type sparql_query: str
    :return: The query returns the wikidata item id, the wikidata item label, the wikidata item
    description, and the wikidata item category.
    """
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
