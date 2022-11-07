import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD

import Code.UtilityFunctions.get_data_path as adsga
from Code.UtilityFunctions.get_data_path import get_path

wd_entity_ns = Namespace("http://www.wikidata.org/entity/")
wd_predicate_ns = Namespace("https://www.wikidata.org/wiki/Property:")


def wikidata_predicate_lookup(column_name: str) -> tuple[str, XSD.anyURI]:
    match column_name:
        case "Population":
            return wd_predicate_ns + "P1082", XSD.integer
        case "City":
            pass
        case "County":
            pass
        case "State":
            pass
        case "Province":
            pass


def wikidata_locations(csv_file: str) -> None:
    country_Qid = [("usa" "Q30"), ("canada", "Q16")]
    granularity_Qid = [("States", "Q7275"), ("Counties", "Q28575"), ("Cities", "Q515")]
    G = Graph()
    for country, Qid in country_Qid:

        G.add(triple=(
            URIRef(wd_entity_ns + Qid),  # e.g., USA
            URIRef(wd_predicate_ns + "P31"),  # Instance of
            URIRef(wd_entity_ns + "Q6256")  # Country
        ))

        for granularity, Qid in granularity_Qid:
            df = pd.read_csv(f"{country}{granularity}")
            for tuple in df.itertuples():
                pass
            pass
        pass


    df = pd.read_csv(adsga.get_path(f"{csv_file}"))
    print(df)
    G = Graph()
    for tuple in df.itertuples():
        predicate, object_type = wikidata_predicate_lookup("Population")
        G.add(
            triple=(
                URIRef(tuple.CityCode),
                URIRef(predicate),
                Literal(tuple.Population, datatype=object_type)
            )
        )

    G.serialize("test.nt", format="nt")


if __name__ == "__main__":
    wikidata_locations("usCities.csv")
