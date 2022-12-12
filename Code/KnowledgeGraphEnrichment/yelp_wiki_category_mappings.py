import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import os
import gzip
import datetime
import numpy as np
import pandas as pd
from discord_webhook import DiscordWebhook
from collections import Counter
from rdflib import Namespace, Graph, URIRef, Literal, XSD
from rdflib.namespace import RDFS
from pprint import pprint
from deepdiff import DeepDiff


from Code.UtilityFunctions.wikidata_functions import wikidata_query, retrieve_wikidata_claims, category_query, min_qid, get_all_wikidata_claims, compare_qids, categories_dict_singular, get_qid_label
from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import space_words_lower


def create_yelp_wiki_schema_triples_csv():
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)
    categories = list(biz['categories'].str.cat(sep=', ').split(sep=', '))
    categories_dict_singular = categories_dict_singular(categories)

    category_occurences = pd.DataFrame(list(dict(Counter(categories)).items()),
                                   columns=['category', 'occurences'
                                            ]).sort_values(by='occurences',
                                                           ascending=False)
    # Maps the split categories to the original categories
    category_occurences['split_category'] = category_occurences['category'].map(categories_dict_singular)
    category_occurences = category_occurences.explode('split_category')

    # Maps the yelp categories that are already mapped to a schemaType to the original category.
    class_mapping = pd.read_csv(get_path('class_mappings.csv'))
    class_mapping['SchemaType'] = class_mapping['SchemaType'].apply(lambda x: eval(x)[0])
    category_occurences['split_category'] = category_occurences['split_category'].apply(lambda x: x.title().replace(' ', ''))
    category_occurences = category_occurences.merge(class_mapping,
                                                left_on='category',
                                                right_on='YelpCategory',
                                                how='left').drop(columns=['YelpCategory'])
    category_occurences['schema_or_yelp_category'] = category_occurences['SchemaType'].fillna(category_occurences['split_category'])


    # Query Wikidata for the QID of the split categories
    category_qid = {}
    category_qid2 = {}
    for cat in category_occurences.itertuples():
        try:
            cat = space_words_lower(cat.schema_or_yelp_category)
        
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
    category_qid_only_qid = {key: value[0] for (key, value) in category_qid.items()}
    category_qid2_only_qid = {key: value[0] for (key, value) in category_qid2.items()}
    ddiff = DeepDiff(category_qid_only_qid, category_qid2_only_qid, verbose_level=1)

    update_qid_dict = {}
    for key, value in ddiff['values_changed'].items():
        key = key[6:-2]
    # check if the new qid is an instance of old qid, then update with old qid if true
        if wikidata_query(
            compare_qids(new_value=value['new_value'],old_value=value['old_value'])).empty is False:
            print(f"Updating {key} from {value['new_value']} to {value['old_value']}")
            update_qid_dict[key] = category_qid[key]
    # update the qid dict with the new qids, 
    # updated values: {'airline': 'Q46970', 'boat tour': 'Q25040412', 'magazine': 'Q41298'}
    category_qid2.update(update_qid_dict)
    category_qid2 = {k.title().replace(' ', ''): v for k, v in category_qid2.items()}

    # Maps the QID to the split category
    category_occurences['qid'] = category_occurences['schema_or_yelp_category'].map(category_qid2)
    category_occurences[['qid', 'qid_label']] = pd.DataFrame(category_occurences['qid'].tolist(),index=category_occurences.index)

    category_wikidata = get_all_wikidata_claims(category_occurences['qid'])

    # Maps the wikidata subclasses to the split category
    category_triple = {}
    for key, values in category_wikidata.items():
        for value in values:
            for obj in value:
                if obj['mainsnak']['property'] == 'P279':
                    data_value = obj['mainsnak']['datavalue']['value']['id']
                    category_triple[key] = category_triple.get(key,[]) + [data_value]

    wiki_subclasses = pd.DataFrame(list(category_triple.items()),
                               columns=['category_qid',
                                        'subclassOf']).explode('subclassOf')

    wiki_subclasses['subclassOf_label'] = wiki_subclasses.apply(lambda x: get_qid_label(x.subclassOf), axis=1)

    yelp_wiki_schema_triples_df = category_occurences.merge(wiki_subclasses, 
                                                        left_on='qid', 
                                                        right_on='category_qid', 
                                                        how='left')
    yelp_wiki_schema_triples_df.to_csv(get_path("yelp_wiki_schema_triples_df.csv"), index=False)

def create_wiki_category_nt_files(yelp_wiki_schema_triples_df: pd.DataFrame):
    schema = Namespace("https://schema.org/")
    example = Namespace("https://example.org/")
    wiki = Namespace("https://www.wikidata.org/entity/")

    ## If file exists, delete it ##
    remove_files="/home/ubuntu/vol1/virtuoso/import/wikidata_category_triples.nt.gz"
    if os.path.isfile(remove_files):
        os.remove(remove_files)
    else:    ## Show an error ##
        print("Error: %s file not found" % remove_files)
    
    triple_file = gzip.open(filename="/home/ubuntu/vol1/virtuoso/import/wikidata_category_triples.nt.gz", mode="at", encoding="utf-8")

    G = Graph()
    for i in yelp_wiki_schema_triples_df.itertuples():
        if i.subclassOf is not np.nan:
            G.add((URIRef(wiki[i.qid]), URIRef(wiki["P279"]), URIRef(wiki[i.subclassOf])))
            G.add((URIRef(wiki[i.subclassOf]), URIRef(schema["label"]), Literal(i.subclassOf_label, datatype=XSD.string)))
        if i.qid is not np.nan:
            if i.SchemaType is not np.nan:
                G.add((URIRef(schema[i.SchemaType]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))
            else:
                G.add((URIRef(example[i.split_category]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))
            G.add((URIRef(wiki[i.qid]), URIRef(RDFS["label"]), Literal(i.qid_label, datatype=XSD.string)))
            G.add((URIRef(wiki[i.qid]), URIRef(RDFS["Class"]), URIRef(example['wikidataCategory'])))

    triple_file.write(G.serialize(format="nt"))
    triple_file.close()

if __name__ == "__main__":
    begin_time = datetime.datetime.now()
    try:
        # create_yelp_wiki_schema_triples_csv()
        yelp_wiki_schema_triples_df=pd.read_csv(get_path("yelp_wiki_schema_triples_df.csv"))
        create_wiki_category_nt_files(yelp_wiki_schema_triples_df)
        
        message = f"yelp_wiki_category_mappings execution is done - Time in hh:mm:ss - {datetime.datetime.now() - begin_time} \nbegan {begin_time} \nended {datetime.datetime.now()}"
    except Exception as e:
        message = "yelp_wiki_category_mappings broke with this error: " + str(e)
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/918876596763525150/d1aGYekdsL64QP0Dbx4zuaOrs_opUpFuTYkj1sHjYBJ8oUXOrruXhshP_cIFSq5phW-e', content=message)
    response = webhook.execute()
    print(message)