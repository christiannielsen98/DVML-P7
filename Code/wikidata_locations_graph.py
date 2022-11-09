import sys

sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

import gzip

import Code.UtilityFunctions.get_data_path as adsga
import pandas as pd
from Code.UtilityFunctions.get_data_path import get_path
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS, XSD

wd_entity_ns = Namespace("http://www.wikidata.org/entity/")
wd_predicate_ns = Namespace("https://www.wikidata.org/wiki/Property:")


def wd_country_lookup(country: str) -> str:
    match country:
        case "USA": return "Q30"
        case "Canada": return "Q16"


def wd_locations() -> None:
    triple_file = gzip.open(filename="/home/ubuntu/vol1/virtuoso/import/wikidata_graph.nt.gz", mode="at",
                            encoding="utf-8")
    
    country_granularity_lookup = {"USA": ["Cities", "Counties", "States"], "Canada": ["Cities", "States"]}
    class_lookup = {"Cities": "Q515", "Counties": "Q28575", "States": "Q7275"}

    location_predicate = wd_predicate_ns + "P131"
    label_predicate = RDFS.label
    population_predicate = wd_predicate_ns + "P1082"
    instance_of_predicate = wd_predicate_ns + "P31"

    for country, granularity_list in country_granularity_lookup.items():
        outer_graph = Graph()

        outer_graph.add(triple=(
            URIRef(wd_entity_ns + wd_country_lookup(country)),  # e.g., "Q30"
            URIRef(RDFS.label),
            Literal(country, datatype=XSD.string)  # e.g., "USA"
        ))

        outer_graph.add(triple=(
            URIRef(wd_entity_ns + wd_country_lookup(country)),  # e.g., "Q30"
            URIRef(wd_predicate_ns + "P31"),  # instance of
            URIRef(wd_entity_ns + "Q6256")  # country
        ))

        triple_file.write(outer_graph.serialize(format='nt'))

        for granularity in granularity_list:
            inner_graph = Graph()
            file_path = get_path(f"{country}_{granularity}.csv")
            df = pd.read_csv(file_path)

            for tuple in df.itertuples():
                # 1 Subject IRI
                # 2 Subject Label LITERAL
                # 3 Superclass IRI
                # 4 Population LITERAL

                inner_graph.add(
                    triple=(
                        URIRef(tuple[1]),
                        URIRef(instance_of_predicate),
                        URIRef(wd_entity_ns + class_lookup[granularity])
                    )
                )

                inner_graph.add(
                    triple=(
                        URIRef(tuple[1]),
                        URIRef(label_predicate),
                        Literal(tuple[2], datatype=XSD.string)
                    )
                )

                inner_graph.add(
                    triple=(
                        URIRef(tuple[1]),
                        URIRef(location_predicate),
                        Literal(tuple[3], datatype=XSD.string)
                    )
                )

                if granularity == "Cities":
                    inner_graph.add(
                        triple=(
                            URIRef(tuple[1]),
                            URIRef(population_predicate),
                            Literal(tuple[4], datatype=XSD.integer)
                        )
                    )

                triple_file.write(inner_graph.serialize(format='nt'))
    
    triple_file.close()


if __name__ == "__main__":
    wd_locations()
