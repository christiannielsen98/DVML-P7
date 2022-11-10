import sys

sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

import gzip
from math import ceil
import numpy as np
import pandas as pd
from collections import Counter
from rdflib import Namespace, Graph, URIRef

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.wikidata_query_tools import (
    retrieve_wikidata_claims, wikidata_query)
from Code.UtilityFunctions.string_functions import split_words_inc_slash, split_words, turn_words_singular


def category_query(category: str):
    return f"""SELECT distinct ?item ?itemLabel ?itemDescription WHERE{{
    ?item ?label "{category}"@en.
    ?article schema:about ?item .
    ?article schema:inLanguage "en" .
    ?article schema:isPartOf <https://en.wikipedia.org/>.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}}}"""


def min_qid(df_qid):
    # Getting the minimum value of the QID number
    return 'Q' + str(df_qid['item.value'].apply(lambda x: int(x.split("/")[-1].replace("Q", ""))).min())


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

categories_unique = list(
    set(biz['categories'].str.cat(sep=', ').split(sep=', ')))
categories = list(biz['categories'].str.cat(sep=', ').split(sep=', '))

category_occurences = pd.DataFrame(list(dict(Counter(categories)).items()),
                                   columns=['category', 'occurences'
                                            ]).sort_values(by='occurences',
                                                           ascending=False)

categories_dict = split_words(categories_unique, split_words_inc_slash)
categories_dict_singular = turn_words_singular(categories_dict)

# Maps the split categories to the original categories
category_occurences['split_category'] = category_occurences['category'].map(categories_dict_singular)
category_occurences = category_occurences.explode('split_category')

# Maps the yelp categories that are already mapped to a schemaType to the original category.
class_mapping = pd.read_csv('Code/UtilityFiles/class_mappings.csv')
category_occurences = category_occurences.merge(class_mapping,
                                                left_on='category',
                                                right_on='YelpCategory',
                                                how='left')

# Query Wikidata for the QID of the split categories
category_qid = {}
for i in category_occurences['split_category'].to_list():
    try:
        cat = i.lower()
        cat_qid = min_qid(wikidata_query(
            category_query(category=cat)))
        category_qid[cat] = cat_qid
    except:
        pass

# Maps the QID to the split category
category_occurences['qid'] = category_occurences['split_category'].map(
    category_qid)

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

yelp_wiki_schema_triples_df = category_occurences.merge(
    wiki_subclasses, left_on='qid', right_on='category_qid', how='left')


schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")
wiki = Namespace("https://www.wikidata.org/entity/")

triple_file = gzip.open(filename=f"/home/ubuntu/vol1/virtuoso/import/yelp_business.nt.gz", mode="at",encoding="utf-8")

G = Graph()
for i in yelp_wiki_schema_triples_df.itertuples():
    if i.SchemaType is not np.nan:
        G.add(
            (
                URIRef(schema[i.SchemaType]),
                URIRef(schema["sameAs"]),
                URIRef(wiki[i.qid]),
            )
        )
    else:
        if i.qid is not np.nan:
            if "&" in i.category:
                G.add(
                    (
                        URIRef(example["_".join(i.category.split(" "))]),
                        URIRef(example["superclassOf"]),
                        URIRef(wiki[i.qid]),
                    )
                )
            else:
                G.add(
                    (
                        URIRef(example["_".join(i.category.split(" "))]),
                        URIRef(schema["sameAs"]),
                        URIRef(wiki[i.qid]),
                    )
                )
    if i.subclassOf is not None:
        G.add((wiki[i.category_qid], wiki["P279"], wiki[i.subclassOf]))

# nt = G.serialize(destination="categories.nt", format="nt")

triple_file.write(G.serialize(format="nt"))
triple_file.close()

if __name__ == "__main__":
    pass