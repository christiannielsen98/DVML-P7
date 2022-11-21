import re
import pandas as pd
import numpy as np

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.string_functions import str_split, turn_words_singular

from sentence_transformers import SentenceTransformer

pd.options.mode.chained_assignment = None


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)
schema = pd.read_csv(get_path("schemaorg-current-https-types.csv"))[["label", "subTypeOf"]]


def space_words_lower(string):
    return re.sub('(?<!^)([A-Z])([^A-Z])', r' \1\2', string).lower()


def clean_yelp_categories():
    categories_unique = list(set(biz["categories"].str.cat(sep=', ').split(sep=', ')))
    categories_dict = {categories_unique[i]: [categories_unique[i]] for i in range(len(categories_unique))}

    cat_string_manually_handled_dict = pd.read_excel(get_path("split_categories.xlsx"), sheet_name="Sheet1", index_col=0, names=['column']).to_dict()['column']
    cat_string_manually_handled_dict = {k: v.split(', ') for k, v in cat_string_manually_handled_dict.items()}
    categories_dict.update(cat_string_manually_handled_dict)

    yelp_categories_dict = turn_words_singular(categories_dict)

    yelp_categories = list({category for sublist in yelp_categories_dict.values() for category in sublist})

    return yelp_categories, yelp_categories_dict


def clean_schema_categories():
    schema_categories = list(map(lambda x: space_words_lower(x), schema["label"].tolist()))
    schema_categories_dict = dict(zip(schema_categories, schema["label"].tolist()))

    return schema_categories, schema_categories_dict


def cos_sim_2d(x, y):
    norm_x = x / np.linalg.norm(x, axis=1, keepdims=True)
    norm_y = y / np.linalg.norm(y, axis=1, keepdims=True)
    return np.matmul(norm_x, norm_y.T)


def category_mappings(threshold):
    yelp_categories, yelp_categories_dict = clean_yelp_categories()
    schema_categories, schema_categories_dict = clean_schema_categories()

    swapped_yelp_categories = {sub_value: key for key, value in yelp_categories_dict.items() for sub_value in value}

    yelp_embeddings = model.encode(yelp_categories)
    schema_embeddings = model.encode(schema_categories)

    co_sim_matrix = pd.DataFrame(data=cos_sim_2d(yelp_embeddings, schema_embeddings),
                                 index=yelp_categories,
                                 columns=schema_categories
                                 ).apply(pd.to_numeric)

    mappings = pd.DataFrame(data={"mapped_schema": co_sim_matrix.idxmax(axis=1), "similarity": co_sim_matrix.max(axis=1)}, index=co_sim_matrix.index).sort_values(by="similarity", ascending=False).reset_index(names="yelp_category")

    # Getting correct names
    mappings["mapped_schema"] = mappings["mapped_schema"].apply(lambda x: schema_categories_dict.get(x))
    mappings["yelp_category"] = mappings["yelp_category"].apply(lambda x: swapped_yelp_categories.get(x))

    mappings = mappings[mappings['similarity'] >= threshold]
    mappings['mapped_schema'][mappings['mapped_schema'] == "None"] = None
    mappings.set_index('yelp_category', inplace=True)

    mapping_dictionary = mappings["mapped_schema"].squeeze().to_dict()

    return mapping_dictionary


if __name__ == "__main__":
    category_mappings(0.68)
