from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE

target_classes = [
    "http://schema.org/Restaurant"
]

namespaces_dict = {"http://example.org/": "ex"}

input_nt_file = "/home/ubuntu/vol1/virtuoso/import/yelp_business.nt.gz"

shaper = Shaper(target_classes=target_classes,
                graph_file_input=input_nt_file,
                input_format=NT,
                namespaces_dict=namespaces_dict,  # Default: no prefixes
                instantiation_property="http://www.w3.org/1999/02/22-rdf-syntax-ns#type")  # Default rdf:type

output_file = "shaper_example.ttl"

shaper.shex_graph(output_file=output_file,
                  acceptance_threshold=0.1,
                  output_format=SHACL_TURTLE)

print("Done!")
