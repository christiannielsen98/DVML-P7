from rdflib.namespace import RDFS
from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE, GZ
import time

start = time.time()

target_classes = [
    "https://schema.org/LocalBusiness",
    "https://schema.org/Person",
    "https://schema.org/UserReview",
    "https://purl.archive.org/purl/yelp/ontology#Tip"
]

namespaces_dict = {"https://schema.org/": "schema",
                   "http://example.org/": "example",
                   "https://www.w3.org/2004/02/skos/core#": "skos",
                   "http://www.w3.org/2001/XMLSchema#": "xsd",
                   "https://www.yelp.com/biz/": "business_uri",
                   "https://www.yelp.com/user_details?userid=": "user_uri",
                   "https://www.yelp.com/category/": "category_uri",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                   "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
                   "https://purl.archive.org/purl/yelp/ontology#": "yont"
                   }

input_nt_files = ["/home/ubuntu/vol1/virtuoso/import/yelp_business.nt.gz",
                  "/home/ubuntu/vol1/virtuoso/import/yelp_user.nt.gz",
                  "/home/ubuntu/vol1/virtuoso/import/yelp_review.nt.gz",
                  "/home/ubuntu/vol1/virtuoso/import/yelp_tip.nt.gz"]

threshold = 0.01

shaper = Shaper(target_classes=target_classes,
                graph_list_of_files_input=input_nt_files,
                namespaces_dict=namespaces_dict,
                input_format=NT,
                compression_mode=GZ,
                instantiation_property="http://www.w3.org/2000/01/rdf-schema#Class")  # The predicate which is used to assign the target_classes to the subjects

output_file_ttl = "/home/ubuntu/DVML-P7/Code/SHACL/shacl_shapes.ttl"

shaper.shex_graph(output_file=output_file_ttl,
                  acceptance_threshold=threshold,
                  output_format=SHACL_TURTLE)

print("Done!")
print(f'In total it took', time.time()-start, 'seconds.')
