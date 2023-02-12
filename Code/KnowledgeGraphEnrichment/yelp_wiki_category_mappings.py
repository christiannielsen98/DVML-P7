import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import os
import gzip
import datetime
import numpy as np
import pandas as pd
from collections import Counter
from rdflib import Namespace, Graph, URIRef, Literal, XSD
from rdflib.namespace import RDFS
import inflect

from Code.UtilityFunctions.wikidata_functions import wikidata_query, get_subclass_of_wikientity, category_query, min_qid, categories_dict_singular
from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import space_words_lower


def create_yelp_wiki_schema_triples_csv():
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)
    categories = list(biz['categories'].str.cat(sep=', ').split(sep=', '))

    category_occurences = pd.DataFrame(list(dict(Counter(categories)).items()),
                                        columns=['category', 'occurences']).sort_values(by='occurences',ascending=False)
    # Maps the split categories to the original categories
    category_occurences['split_category'] = category_occurences['category'].map(categories_dict_singular(categories))
    category_occurences = category_occurences.explode('split_category')

    # Maps the yelp categories that are already mapped to a schemaType to the original category.
    class_mapping = pd.read_csv(get_path('class_mappings_manual.csv'))
    class_mapping['SchemaType'] = class_mapping['SchemaType'].apply(lambda x: eval(x)[0])
    category_occurences['split_category'] = category_occurences['split_category'].apply(lambda x: x.title().replace(' ', ''))
    category_occurences = category_occurences.merge(class_mapping,
                                                left_on='category',
                                                right_on='YelpCategory',
                                                how='left').drop(columns=['YelpCategory'])
    category_occurences['schema_or_yelp_category'] = category_occurences['SchemaType'].fillna(category_occurences['split_category'])

    category_qid = {}
    for cat in category_occurences.itertuples():
        try:
            # Turns the category into a queryable string by lowering the word.
            cat = space_words_lower(cat.schema_or_yelp_category)
            # Queries Wikidata for the QID of the category
            wikidata_cat_query = wikidata_query(category_query(category=cat))
            # Filters the QIDs by the ones that have a subclassOf relation, by taking the one with the lowest QID.
            qid = min_qid(wikidata_cat_query)
            # Inserts the QID and label into the dictionary
            category_qid[cat] = qid
            # If the QID is an instance of another entity, then the QID is replaced by the QID of the entity it is an instance of.
            instance_of_query = instance_of_query(qid)
            if not instance_of_query.empty:
                category_qid[cat] = wikidata_cat_query.loc[wikidata_cat_query['item.value'] == instance_of_query['instanceOf.value'][0]][['item.value', 'itemLabel.value']].apply(lambda x: (x[0].split('/')[-1], x[1]), axis=1)[0]
        except:
            pass

        
    category_qid = {k.title().replace(' ', ''): v for k, v in category_qid.items()}
    
    # Maps the QID to the split category
    category_occurences['qid'] = category_occurences['schema_or_yelp_category'].map(category_qid)
    category_occurences[['qid', 'qid_label']] = pd.DataFrame(category_occurences['qid'].tolist(),index=category_occurences.index)

    wiki_subclasses = pd.DataFrame()
    for qid in category_occurences['qid'].unique():
        wiki_subclasses = pd.concat([wiki_subclasses, get_subclass_of_wikientity(qid)], ignore_index=True)
    
    yelp_wiki_schema_triples_df = category_occurences.merge(wiki_subclasses, on='qid',how='left')
    yelp_wiki_schema_triples_df.to_csv(get_path("yelp_wiki_schema_triples_df.csv"), index=False)

def create_wiki_category_nt_files(yelp_wiki_schema_triples_df: pd.DataFrame):
    schema = Namespace("https://schema.org/")
    wiki = Namespace("https://www.wikidata.org/entity/")
    yelpcat = Namespace("https://purl.archive.org/purl/yelp/business_categories#")
    yelpont = Namespace("https://purl.archive.org/purl/yelp/yelp_ontology#")

    ## If file exists, delete it ##
    remove_files=f"{get_path('')}wikidata_category_triples.nt.gz"
    if os.path.isfile(remove_files):
        os.remove(remove_files)
    else:    ## Show an error ##
        print("Error: %s file not found" % remove_files)
    
    triple_file = gzip.open(filename=f"{get_path('')}wikidata_category_triples.nt.gz", mode="at", encoding="utf-8")

    G = Graph()
    yelp_wiki_schema_triples_df = pd.read_csv(get_path("yelp_wiki_schema_triples_df.csv"))
    for i in yelp_wiki_schema_triples_df.itertuples():
        if i.subclassOf is not np.nan:
            G.add((URIRef(wiki[i.qid]), URIRef(wiki["P279"]), URIRef(wiki[i.subclassOf])))
            G.add((URIRef(wiki[i.subclassOf]), URIRef(schema["label"]), Literal(i.subclassOf_label, datatype=XSD.string)))
        if i.qid is not np.nan:
            if i.SchemaType is not np.nan:
                G.add((URIRef(schema[i.SchemaType]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))
            else:
                p = inflect.engine()
                lower_subcat = space_words_lower(i.split_category)
                preprocessed_subcategory = p.singular_noun(lower_subcat)
                preprocessed_subcategory = preprocessed_subcategory if preprocessed_subcategory else lower_subcat
                yelp_category = preprocessed_subcategory.replace(' ', '_')
                
                G.add((URIRef(yelpcat[yelp_category]), URIRef(schema["sameAs"]), URIRef(wiki[i.qid])))
            G.add((URIRef(wiki[i.qid]), URIRef(RDFS["label"]), Literal(i.qid_label, datatype=XSD.string)))
            G.add((URIRef(wiki[i.qid]), URIRef(RDFS["Class"]), URIRef(yelpont['WikidataCategory'])))

    triple_file.write(G.serialize(format="nt"))
    triple_file.close()

if __name__ == "__main__":
    create_yelp_wiki_schema_triples_csv()
    create_wiki_category_nt_files()
