import json
import requests

import pandas as pd

from Code.UtilityFunctions.wikidata_functions import wikidata_query
from Code.UtilityFunctions.get_data_path import get_path
from Code.KnowledgeGraphEnrichment.location_dicts import states, q_codes


def return_city_q_ids(search_string):
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search={search_string}"

    response = requests.get(url)
    data = json.loads(response.text)

    q_ids = [Q["id"] for Q in data["search"]]

    if not q_ids:  # Empty – no result given
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search={search_string.partition(',')[0]}"

        response = requests.get(url)
        data = json.loads(response.text)

        q_ids = [Q["id"] for Q in data["search"]]

    str_q_ids = " ".join(["wd:" + qid for qid in q_ids])

    return str_q_ids


def return_state_q_ids(search_string):
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&continue=0&search={search_string}"

    response = requests.get(url)
    data = json.loads(response.text)

    q_ids = [Q["id"] for Q in data["search"]]

    str_q_ids = " ".join(["wd:" + qid for qid in q_ids])

    return str_q_ids


def city_query(q_ids, location):
    query = f"""
    SELECT DISTINCT ?qid ?qidLabel
    WHERE {{
        VALUES ?qid {{{q_ids}}}
        {{?qid wdt:P31/wdt:P279* wd:Q486972.}} # Human Settlement
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}

        SERVICE wikibase:around {{
            ?qid wdt:P625 ?location .
            bd:serviceParam wikibase:center "Point({location})"^^geo:wktLiteral   .
            bd:serviceParam wikibase:radius "100" .
            bd:serviceParam wikibase:distance ?distance .}} .
    }}
    ORDER BY ?distance
    LIMIT 1
    """
    return query


def qid_city(q_ids: str, location: str):
    if not q_ids:
        return None, None

    returned = wikidata_query(city_query(q_ids, location))

    if returned.empty:
        returned_qid = None
        returned_label = None
    else:
        returned_qid = returned["qid.value"].str.removeprefix("http://www.wikidata.org/entity/").values[0]
        returned_label = returned["qidLabel.value"].values[0]

    return returned_qid, returned_label


def state_query(q_ids):
    query = f"""
    SELECT ?qid ?qidLabel
    WHERE
    {{
      VALUES ?Q {{{q_ids}}}

      ?Q wdt:P131* ?qid .
      {{?qid wdt:P31/wdt:P279* wd:{q_codes["state"]}.}}
      UNION
      {{?qid wdt:P31/wdt:P279* wd:{q_codes["province"]}.}}

      FILTER NOT EXISTS {{
        ?qid wdt:P31/wdt:P279* wd:{q_codes["country"]}.
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}
    }}
    """
    return query


def qid_state(row: str):
    returned_table = wikidata_query(state_query(row["state_q_ids"]))
    q_ids_list = [x[3:] for x in row["state_q_ids"].split(" ")]
    if returned_table.empty:
        returned_qids = []
    else:
        returned_qids = returned_table["qid.value"].str.removeprefix("http://www.wikidata.org/entity/").tolist()

    try:
        first_common_qid = next(og_list for og_list in q_ids_list if og_list in returned_qids)
    except StopIteration:
        first_common_qid = None

    returned_label = None if not first_common_qid else \
        returned_table[returned_table["qid.value"] == f"http://www.wikidata.org/entity/{first_common_qid}"][
            "qidLabel.value"].values[0]

    return first_common_qid, returned_label


def county_query(q_id):
    query = f"""
    SELECT ?qid ?qidLabel
    WHERE
    {{
      wd:{q_id} wdt:P131* ?qid .
      ?qid wdt:P31/wdt:P279* wd:{q_codes["county"]}.

      FILTER NOT EXISTS {{
        ?qid wdt:P31/wdt:P279* wd:{q_codes["state"]}.
      }}
      FILTER NOT EXISTS {{
        ?qid wdt:P31/wdt:P279* wd:{q_codes["country"]}.
      }}
      FILTER NOT EXISTS {{
        ?qid wdt:P31/wdt:P279* wd:Q3301053. # consolidated city-county
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}

    }}
    """
    return query


def qid_return_county(q_id):
    returned_qid = wikidata_query(county_query(q_id))
    if returned_qid.empty:
        return None, None
    else:
        return (returned_qid["qid.value"][0].removeprefix("http://www.wikidata.org/entity/"),
                returned_qid["qidLabel.value"][0])


def country_query(q_id):
    query = f"""
    SELECT ?qid ?qidLabel
    WHERE
    {{
      wd:{q_id} wdt:P131* ?qid .
      ?qid wdt:P31/wdt:P279* wd:{q_codes["country"]}.

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}
    }}
    """
    return query


def qid_return_country(q_id):
    returned_qid = wikidata_query(country_query(q_id))
    if returned_qid.empty:
        return None, None
    else:
        return (returned_qid["qid.value"][0].removeprefix("http://www.wikidata.org/entity/"),
                returned_qid["qidLabel.value"][0])


def city_population_query(city_qid: str):
    try:
        query = f"""
        SELECT DISTINCT ?population
        WHERE {{
            ?city p:P1082 ?statement .
            VALUES ?city {{wd:{city_qid}}}
            ?statement ps:P1082 ?population .
            ?statement pq:P585 ?date .
            FILTER NOT EXISTS {{
                ?city p:P1082/pq:P585 ?date2 .
                FILTER(?date2 > ?date)
	        }}
        }}
        """
        a = wikidata_query(query)
        return int(a['population.value'][0])
    except:
        return None


def create_locations_csv():
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

    biz["city_og"] = biz["city"]
    biz["state_og"] = biz["state"]
    biz["city"] = biz["city"].apply(lambda x: x.partition(",")[0])
    biz["state"] = biz["state"].apply(lambda x: states[x])

    city_state_keys = biz[["city", "state", "city_og", "state_og"]].drop_duplicates()

    df = biz.groupby(["city", "state"])[["latitude", "longitude"]].mean().reset_index()
    df["location"] = df["longitude"].round(decimals=2).astype(str) + "," + df["latitude"].round(decimals=2).astype(str)

    df["search_string"] = df.apply(lambda x: x[0] + ", " + x[1], axis=1).str.replace(" ", "%20")

    df["city_q_ids"] = df["search_string"].apply(return_city_q_ids)

    df["state_q_ids"] = df["state"].apply(return_state_q_ids)

    df[["city_qid", "city_label"]] = df.apply(lambda x: qid_city(x["city_q_ids"], x["location"]), result_type='expand',
                                              axis=1)

    df[["state_qid", "state_label"]] = df.apply(qid_state, result_type='expand', axis=1)

    unique_cities = pd.Series(df["city_qid"].unique())

    county_qids, county_labels = zip(*unique_cities.apply(qid_return_county))

    df = df.merge(pd.DataFrame(data={"city_qid": unique_cities,
                                     "county_qid": county_qids,
                                     "county_label": county_labels}), how="left", on="city_qid")

    unique_states = pd.Series(df["state_qid"].unique())
    country_qids, country_labels = zip(*unique_states.apply(qid_return_country))

    df = df.merge(pd.DataFrame(data={"state_qid": unique_states,
                                     "country_qid": country_qids,
                                     "country_label": country_labels}), how="left", on="state_qid")

    df["population"] = df["city_qid"].apply(city_population_query)

    df = city_state_keys.merge(df, how="left", on=["city", "state"])
    df.drop(
        columns=["latitude", "longitude", "location", "search_string", "city_q_ids", "state_q_ids", "city", "state"],
        inplace=True)
    df.rename(columns={"city_og": "city", "state_og": "state"}, inplace=True)

    df.to_csv(path_or_buf=get_path('location_mappings_search_location.csv'), index=False)


# ## CREATE NT

def add_to_graph(row, lower_level, higher_level, higher_instance):
    from rdflib import Graph, URIRef, Literal, XSD
    from rdflib.namespace import RDFS

    from Code.KnowledgeGraphEnrichment.location_namespaces import wiki, location_predicate, instance_of_predicate

    graph = Graph()

    graph.add((URIRef(wiki[eval(f"row.{lower_level}_qid")]), URIRef(location_predicate),
               URIRef(wiki[eval(f"row.{higher_level}_qid")])))
    graph.add((URIRef(wiki[eval(f"row.{higher_level}_qid")]), URIRef(RDFS.label),
               Literal(eval(f"row.{higher_level}_label"), datatype=XSD.string)))
    graph.add(
        (URIRef(wiki[eval(f"row.{higher_level}_qid")]), URIRef(instance_of_predicate), URIRef(wiki + higher_instance)))

    return graph


def create_locations_nt():
    import gzip

    from rdflib import Graph, URIRef, Literal, XSD
    from rdflib.namespace import RDFS

    from Code.KnowledgeGraphEnrichment.location_namespaces import schema, wiki, yelpont, population_predicate, \
        instance_of_predicate

    df = pd.read_csv(get_path("location_mappings_search_location.csv"))
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

    data = biz.merge(df, how="left", on=["city", "state"])

    G = Graph()
    for row in data.itertuples():
        if row.city_qid:
            G.add((URIRef(yelpont[row.business_id]), URIRef(schema['location']), URIRef(wiki[row.city_qid])))
            G.add((URIRef(wiki[row.city_qid]), URIRef(RDFS.label), Literal(row.city_label, datatype=XSD.string)))
            if row.population:
                G.add((URIRef(wiki[row.city_qid]), URIRef(population_predicate),
                       Literal(row.population, datatype=XSD.integer)))

            if row.county_qid:
                G += add_to_graph(row, "city", "county", "Q28575")
                if row.state_qid:
                    G += add_to_graph(row, "county", "state", "Q7275")
                    if row.country_qid:
                        G += add_to_graph(row, "state", "country", "Q6256")  # to state
                elif row.country_qid:
                    G += add_to_graph(row, "county", "country", "Q6256")  # to county
            elif row.state_qid:
                G += add_to_graph(row, "city", "state", "Q7275")  # to city
                if row.country_qid:
                    G += add_to_graph(row, "state", "country", "Q6256")  # to state
            elif row.country_qid:
                G += add_to_graph(row, "city", "country", "Q6256")  # to city
        elif row.state_qid:
            G.add((URIRef(yelpont[row.business_id]), URIRef(schema['location']), URIRef(wiki[row.state_qid])))
            G.add((URIRef(wiki[row.state_qid]), URIRef(RDFS.label), Literal(row.state_label, datatype=XSD.string)))
            G.add((URIRef(wiki[row.state_id]), URIRef(instance_of_predicate), URIRef(wiki[row.state_id])))
            if row.country_qid:
                G += add_to_graph(row, "state", "country", "Q6256")  # to state

    with gzip.open(filename="/home/ubuntu/vol1/virtuoso/import/wikidata_location_mappings.nt.gz", mode="at",
                   encoding="utf-8") as file:
        file.write(G.serialize(format="nt"))


if __name__ == "__main__":
    # create_locations_csv()
    create_locations_nt()

    # import os
    #
    # os.system("onedrive --synchronize --single-directory DVML-P7") if "Linux" in os.uname() else None
