import sys

import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import turn_words_singular, space_words_lower

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


def get_subclass_of_wikientity(qid):
    try:
        query = f"""SELECT ?item ?itemLabel 
                WHERE 
                    {{
                    wd:{qid} wdt:P279 ?item .
                    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                    }}"""
        df = wikidata_query(query)[['item.value', 'itemLabel.value']]
        df['item.value'] = df.apply(lambda x: x['item.value'][31:], axis=1)
        df.rename(columns={'item.value': 'subclassOf', 'itemLabel.value': 'subclassOf_label'}, inplace=True)
        df['qid'] = qid
        return df
    except:
        pass

def category_query(category: str):
    """
    It takes a category name as a string, and returns a query that will return all the possible QID's and QID-labels for that category.
    :param category: The category you want to search for
    :type category: str
    :return: The query returns the item, itemLabel, and itemDescription of the category.
    """
    category = space_words_lower(category)
    return f"""SELECT distinct ?item ?itemLabel ?itemDescription WHERE{{
    ?item ?label "{category}"@en.
    ?item wdt:P279 ?subclass .
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
