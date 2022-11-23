from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE
import time
start = time.time()

target_classes = [
    "https://example.org/SchemaClass",
    "https://example.org/YelpCategory",
    "https://example.org/ExampleClass",
    # "https://schema.org/Restaurant"
]


input_nt_file = "/home/ubuntu/vol1/virtuoso/import/yelp_business.nt"

shaper = Shaper(target_classes=target_classes,
                graph_file_input=input_nt_file,
                input_format=NT,
                instantiation_property="http://www.w3.org/2000/01/rdf-schema#Class")  # Default rdf:type

output_file_shex = "shaper_yelp_business.shex"
output_file_ttl = "shaper_yelp_business.ttl"
shaper.shex_graph(output_file=output_file_shex,
                  acceptance_threshold=0.01,)

shaper.shex_graph(output_file=output_file_ttl,
                  acceptance_threshold=0.01,
                  output_format=SHACL_TURTLE
                  )

print("Done!")
print(f'In total it took', time.time()-start, 'seconds.')