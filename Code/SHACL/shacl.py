from rdflib.namespace import RDFS
from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE, GZ
import time

target_classes = [
    "https://schema.org/LocalBusiness"
]

namespaces_dict = {"https://schema.org/": "schema",
                   "https://www.w3.org/2004/02/skos/core#": "skos",
                   "http://www.w3.org/2001/XMLSchema#": "xsd",
                   "https://www.yelp.com/biz/": "business_uri",
                   "https://www.yelp.com/user_details?userid=": "user_uri",
                   "https://www.yelp.com/category/": "category_uri",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                   "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
                   "https://purl.archive.org/purl/yelp/ontology#": "yont",
                   "https://purl.archive.org/purl/yelp/business_categories#>": "yelpcat"
                   }

input_nt_files = ["/home/ubuntu/vol1/virtuoso/import/yelp_business.nt.gz"]

thresholds = [0]

for threshold in thresholds:
    start = time.time()
    shaper = Shaper(
                target_classes=target_classes,
                graph_list_of_files_input=input_nt_files,
                namespaces_dict=namespaces_dict,
                input_format=NT,
                compression_mode=GZ,
                instantiation_property="http://www.w3.org/2000/01/rdf-schema#Class"  # The predicate which is used to assign the target_classes to the subjects
            )
    
    output_file_ttl = f"/home/ubuntu/DVML-P7/Code/SHACL/business_shapes_{threshold}.ttl"
    shaper.shex_graph(output_file=output_file_ttl,
                  acceptance_threshold=threshold,
                  output_format=SHACL_TURTLE)
    
    print(f"Done for threshold {threshold}!")
    print(f'In total it took {time.time() - start} seconds.')
    
    del start, shaper, output_file_ttl
