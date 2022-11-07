import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal
from rdflib.namespace import RDFS, XSD

from Code.UtilityFunctions.get_data_path import get_path

WIKIDATA_ENTITY_NS = Namespace("http://www.wikidata.org/entity/")
WIKIDATA_PREDICATE_NS = Namespace("https://www.wikidata.org/wiki/Property:")


def wikidata_predicate_lookup(column_name: str) -> str:
    match column_name:
        case "Population":
            pass
        case "City":
            return WIKIDATA_PREDICATE_NS + "P1448", XSD.string
        case "State":
            pass
        case "Province":
            pass


def wikidata_locations(csv_file: str):
    df = pd.read_csv(get_path(f"{csv_file}.csv"))
    G = Graph()
    for row_tuple in df.itertuples:
        G.add(
            triple=(
                URIRef(row_tuple.CityCode),
                URIRef(wikidata_predicate_lookup("City")[0]),
                Literal(row_tuple.City, datatype=wikidata_predicate_lookup("City")[1])
            )
        )

    G.serialize("test.nt")


if __name__ == "__main__":
    wikidata_locations("usCity.csv")

