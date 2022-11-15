import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

import gzip
from math import ceil
import numpy as np
import pandas as pd
from collections import Counter
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDFS
from pprint import pprint
from deepdiff import DeepDiff
import urllib.parse

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.wikidata_query_tools import retrieve_wikidata_claims, wikidata_query
from Code.UtilityFunctions.string_functions import split_words_inc_slash, split_words, turn_words_singular


def category_query(category: str):
    return f"""SELECT distinct ?item ?itemLabel ?itemDescription WHERE{{
    ?item ?label "{category}"@en.
    ?article schema:about ?item .
    ?article schema:inLanguage "en" .
    ?article schema:isPartOf <https://en.wikipedia.org/>.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}}}"""


def min_qid(df_qid):
    # Getting the minimum value of the QID number and the itemLabel
    index = df_qid['item.value'].apply(
        lambda x: int(x.split("/")[-1].replace("Q", ""))).idxmin()
    df = df_qid.loc[index][['item.value', 'itemLabel.value']]
    return df[0][31:], df[1]


def get_all_wikidata_claims(qid_list: list):
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


biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

categories_unique = list(set(biz['categories'].str.cat(sep=', ').split(sep=', ')))
categories = list(biz['categories'].str.cat(sep=', ').split(sep=', '))

category_occurences = pd.DataFrame(list(dict(Counter(categories)).items()),
                                   columns=['category', 'occurences'
                                            ]).sort_values(by='occurences',
                                                           ascending=False)

# categories_dict = split_words(categories_unique, split_words_inc_slash)
cat_string_man_handle_dict = pd.read_excel(get_path("split_categories.xlsx"), sheet_name="Sheet1", index_col=0, names=['column']).to_dict()['column']
cat_string_man_handle_dict = {k: v.split(', ') for k, v in cat_string_man_handle_dict.items()}
categories_dict = {category_occurences["category"][i]: [category_occurences["category"][i]] for i in range(len(category_occurences))}
categories_dict.update(cat_string_man_handle_dict)

categories_dict_singular = turn_words_singular(categories_dict)

# Maps the split categories to the original categories
category_occurences['split_category'] = category_occurences['category'].map(categories_dict_singular)
category_occurences = category_occurences.explode('split_category')

# Maps the yelp categories that are already mapped to a schemaType to the original category.
class_mapping = pd.read_csv(get_path('class_mappings.csv'))
category_occurences['split_category'] = category_occurences['split_category'].apply(lambda x: x.title().replace(' ', ''))
category_occurences = category_occurences.merge(class_mapping,
                                                left_on='split_category',
                                                right_on='YelpCategory',
                                                how='left')

# Query Wikidata for the QID of the split categories
category_qid = {}
category_qid2 = {}
for cat in category_occurences["split_category"].to_list():
    try:
        wikidata_query_cat_query = wikidata_query(category_query(
            category=cat))  # Querys wikidata for the QID of the category
        category_qid[cat] = (
            wikidata_query_cat_query["item.value"][0][31:],
            wikidata_query_cat_query["itemLabel.value"][0]
        )  # Adds QID and label of the first result of the query
        category_qid2[cat] = min_qid(
            wikidata_query_cat_query
        )  # Adds QID and label with min_qid function
    except:
        pass

# compares the two dictionaries and returns the differences in old value and new value for every key
category_qid_only_qid = {
    key: value[0]
    for (key, value) in category_qid.items()
}
category_qid2_only_qid = {
    key: value[0]
    for (key, value) in category_qid2.items()
}
ddiff = DeepDiff(category_qid_only_qid,
                 category_qid2_only_qid,
                 verbose_level=1)


def compare_qids(new_value: str, old_value: str):
    # check if the new qid is an instance of old qid
    return f"""SELECT ?s 
                WHERE {{?s wdt:P31 wd:{old_value} . 
                        VALUES ?s {{wd:{new_value}}} .
                }}"""


update_qid_dict = {}
for key, value in ddiff['values_changed'].items():
    if key.__contains__("[0]") is True:
        # check if the new qid is an instance of old qid, then update with old qid if true
        if wikidata_query(
                compare_qids(new_value=value['new_value'],
                             old_value=value['old_value'])).empty is False:
            print(
                f"Updating {key} from {value['new_value']} to {value['old_value']}"
            )
            update_qid_dict[key[6:-5]] = category_qid[key[6:-5]]
# update the qid dict with the new qids, 
# updated values: {'airline': 'Q46970', 'boat tour': 'Q25040412', 'magazine': 'Q41298'}
category_qid2.update(update_qid_dict)

# Maps the QID to the split category
category_occurences['qid'] = category_occurences['split_category'].map(
    category_qid2)
category_occurences[['qid', 'qid_label'
                     ]] = pd.DataFrame(category_occurences['qid'].tolist(),
                                       index=category_occurences.index)

category_wikidata = get_all_wikidata_claims(category_occurences['qid'])

# Maps the wikidata subclasses to the split category
category_triple = {}
for key, values in category_wikidata.items():
    for value in values:
        for obj in value:
            if obj['mainsnak']['property'] == 'P279':
                data_value = obj['mainsnak']['datavalue']['value']['id']
                category_triple[key] = category_triple.get(key,
                                                           []) + [data_value]

wiki_subclasses = pd.DataFrame(list(category_triple.items()),
                               columns=['category_qid',
                                        'subclassOf']).explode('subclassOf')

yelp_wiki_schema_triples_df = category_occurences.merge(wiki_subclasses, 
                                                        left_on='qid', 
                                                        right_on='category_qid', 
                                                        how='left')

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")
wiki = Namespace("https://www.wikidata.org/entity/")

triple_file = gzip.open(filename=f"yelp_business.nt.gz",
                        mode="at",
                        encoding="utf-8")

G = Graph()
for i in yelp_wiki_schema_triples_df.itertuples():
    if i.subclassOf is not np.nan:
        G.add((URIRef(wiki[i.qid]), URIRef(wiki["P279"]), URIRef(wiki[i.subclassOf])))
    if i.qid is not np.nan:
        G.add((URIRef(wiki[i.qid]), URIRef(RDFS["label"]), Literal(i.qid_label)))
        G.add((URIRef(wiki[i.qid]), URIRef(RDFS["Class"]), URIRef(example['WikiCategory'])))
        if i.SchemaType is not np.nan:
            G.add((URIRef(schema[i.SchemaType]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))
        else:
            G.add((URIRef(example[i.split_category]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))

triple_file.write(G.serialize(format="nt"))
triple_file.close()

if __name__ == "__main__":
    pass