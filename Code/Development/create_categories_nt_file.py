import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import pandas as pd
from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.wikidata_query_tools import wikidata_query, retrieve_wikidata_claims
from math import ceil
import numpy as np
import inflect


def category_query(category: str):
    return f"""SELECT distinct ?item ?itemLabel ?itemDescription WHERE{{
    ?item ?label "{category}"@en.
    ?article schema:about ?item .
    ?article schema:inLanguage "en" .
    ?article schema:isPartOf <https://en.wikipedia.org/>.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}}}"""
    
biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

categories_unique = list(set(biz['categories'].str.cat(sep=', ').split(sep=', ')))
categories = list(biz['categories'].str.cat(sep=', ').split(sep=', '))

from collections import Counter

category_occurences = pd.DataFrame(list(dict(Counter(categories)).items()), columns=['category', 'occurences']).sort_values(by='occurences', ascending=False)

def split_words_inc_slash(word):
    # Splitting the words that have a slash in them, and turning them into two words
    word_space = word.split(' ')
    word_space
    new_wordlist_a = []
    new_wordlist_b = []
    for i in word_space:
        i = i.lower()
        if '/' not in i:
            new_wordlist_a.append(i)
            new_wordlist_b.append(i)
        else:
            slash_split = i.split('/')
            new_wordlist_a.append(slash_split[0])
            new_wordlist_b.append(slash_split[1])
    new_word_a = ' '.join(new_wordlist_a)
    new_word_b = ' '.join(new_wordlist_b)
    return [new_word_a, new_word_b]

# transforms Yelp category words to words that is succesfull in finding the QID on wikidata
# TODO: fix & split issues
# TODO: fix & split has to be done first, and / split after

def split_words(categories_unique, split_word_inc_slash):
    categories_dict = {}
    for word in categories_unique:
        if '&' in word:
            word_list = list(filter(None, word.lower().split(sep=' & ')))
            categories_dict[word] = word_list
        elif '/' in word:
            categories_dict[word] = split_word_inc_slash(word)
        else:
            categories_dict[word] = [word.lower()]
    return categories_dict

categories_dict = split_words(categories_unique, split_words_inc_slash)


def turn_words_singular(categories_dict):
    p = inflect.engine()
    categories_dict_singular = {}
    for key, value in categories_dict.items():
        new_value = []
        for word in value:
            if p.singular_noun(word) is False:
                word = word
            else:
                word = p.singular_noun(word)
            new_value.append(word)
        categories_dict_singular[key] = new_value
    return categories_dict_singular

categories_dict_singular = turn_words_singular(categories_dict)

# Maps the splitted categories to the original categories
category_occurences['splitted_category'] = category_occurences['category'].map(categories_dict_singular)
category_occurences = category_occurences.explode('splitted_category')

# Maps the yelp categories that are already mapped to a schemaType to the original category.
class_mapping = pd.read_csv('Code/UtilityFiles/class_mappings.csv')
category_occurences = category_occurences.merge(class_mapping, left_on='category', right_on='YelpCategory', how='left')


# Query Wikidata for the QID of the splitted categories
category_qid = {}
for i in category_occurences['splitted_category'].to_list():
    try:
        cat = i.lower()
        cat_qid = wikidata_query(category_query(category=cat))['item.value'][0][31:]
        category_qid[cat] = cat_qid
    except:
        pass

# Maps the QID to the splitted category
category_occurences['qid'] = category_occurences['splitted_category'].map(category_qid)

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

category_wikidata = get_all_wikidata_claims(category_occurences['qid'])

# Maps the wikidata subclasses to the splitted category
category_triple = {}
for key, values in category_wikidata.items():
    for value in values:
        for obj in value:
            if obj['mainsnak']['property'] == 'P279':
                data_value = obj['mainsnak']['datavalue']['value']['id']
                category_triple[key] = category_triple.get(key, []) + [data_value]
category_triple

wiki_subclasses = pd.DataFrame(list(category_triple.items()), columns=['category_qid', 'subclassOf']).explode('subclassOf')

yelp_wiki_schema_triples_df = category_occurences.merge(wiki_subclasses, left_on='qid', right_on='category_qid', how='left')

print(yelp_wiki_schema_triples_df)