from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE
import time
start = time.time()

target_classes = [
    # "https://example.org/SchemaClass",
    # "https://example.org/YelpCategory",
    # "https://example.org/ExampleClass",
    "https://schema.org/Restaurant"
]


input_nt_file = "/home/ubuntu/vol1/virtuoso/import/yelp_business.nt"

shaper = Shaper(target_classes=target_classes,
                raw_graph=input_nt_file,
                input_format=NT,
                instantiation_property="http://www.w3.org/1999/02/22-rdf-syntax-ns#type")  # Default rdf:type

output_file = "shaper_yelp_business.shex"

shaper.shex_graph(output_file=output_file,
                  acceptance_threshold=0.5,)

print("Done!")
print(f'In total it took', time.time()-start, 'seconds.')