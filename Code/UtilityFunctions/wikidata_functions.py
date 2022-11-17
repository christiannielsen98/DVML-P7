import sys
from math import ceil
import numpy as np
import pandas as pd
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import split_words_inc_slash, split_words, turn_words_singular

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


def category_query(category: str):
    """
    It takes a category name as a string, and returns a query that will return all the possible QID's and QID-labels for that category.
    :param category: The category you want to search for
    :type category: str
    :return: The query returns the item, itemLabel, and itemDescription of the category.
    """
    return f"""SELECT distinct ?item ?itemLabel ?itemDescription WHERE{{
    ?item ?label "{category}"@en.
    ?article schema:about ?item .
    ?article schema:inLanguage "en" .
    ?article schema:isPartOf <https://en.wikipedia.org/>.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}}}"""


def min_qid(df_qid: pd.DataFrame):
    """
    It takes a dataframe of QIDs and returns the minimum QID number and the itemLabel
    
    :param df_qid: the dataframe of the QID numbers and itemLabels
    :type df_qid: pd.DataFrame
    :return: The minimum QID number and the itemLabel
    """
    # Getting the minimum value of the QID number and the itemLabel
    index = df_qid['item.value'].apply(
        lambda x: int(x.split("/")[-1].replace("Q", ""))).idxmin()
    df = df_qid.loc[index][['item.value', 'itemLabel.value']]
    return df[0][31:], df[1]


def get_all_wikidata_claims(qid_list: list):
    """
    The function takes a list of wikidata QID's and returns a dictionary with the QID's as keys and the
    claims as values.
    :param qid_list: list
    :type qid_list: list
    :return: A dictionary with the QID as key and the claims as value
    """
    # Create list of all QID's
    category_qid_list = qid_list.tolist()
    category_qid_list = [i for i in category_qid_list if i is not np.nan]

    item_list_len = len(category_qid_list)
    # The limit is set to meet the requirements of the wikibase API wbgetentities (max 50)
    # Ceil makes sure that the each subset from item_list is no longer than 50
    limit = ceil(item_list_len / 50)

    # Seperates the item_list to a nested_list with max 50 items in each list
    piped_list = [category_qid_list[pipe::limit] for pipe in range(limit)]

    category_wikidata = {}
    for i in piped_list:
        category_wikidata.update(retrieve_wikidata_claims(i))
    return category_wikidata

def compare_qids(new_value: str, old_value: str):
    # check if the new qid is an instance of old qid
    return f"""SELECT ?s 
                WHERE {{?s wdt:P31 wd:{old_value} . 
                        VALUES ?s {{wd:{new_value}}} .
                }}"""

def categories_dict_singular(categories: list):
    """
    It takes the categories column of the business dataframe, and returns a dictionary of the
    categories, where each category is singular.
    :param biz: the business dataframe
    :type biz: pd.DataFrame
    :return: A dictionary of categories with the singular form of the category as the key and the plural
    form of the category as the value.
    """
    
    categories_unique = list(set(categories))

    # categories_dict = split_words(categories_unique, split_words_inc_slash)
    cat_string_man_handle_dict = pd.read_excel(get_path("split_categories.xlsx"), sheet_name="Sheet1", index_col=0, names=['column']).to_dict()['column']
    cat_string_man_handle_dict = {k: v.split(', ') for k, v in cat_string_man_handle_dict.items()}
    categories_dict = {i: [i] for i in categories_unique}
    categories_dict.update(cat_string_man_handle_dict)

    categories_dict_singular = turn_words_singular(categories_dict)
    return categories_dict_singular