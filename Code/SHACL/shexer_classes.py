from rdflib.namespace import RDFS
from shexer.shaper import Shaper
from shexer.consts import NT, SHEXC, SHACL_TURTLE
import time
start = time.time()

target_classes = [
    "https://schema.org/LocalBusiness",
    "https://schema.org/Person",
    "https://schema.org/UserReview",
    "https://purl.archive.org/purl/yelp/ontology#Tip"
]

# target_classes = [
#     "http://example.org/Person",
#     "http://example.org/Gender"
# ]

namespaces_dict = {"https://schema.org/": "schema",
                   "http://example.org/": "example",
                   "https://www.w3.org/2004/02/skos/core#": "skos",
                   "http://www.w3.org/2001/XMLSchema#": "xsd",
                   "https://www.yelp.com/biz/": "business_uri",
                   "https://www.yelp.com/user_details?userid=": "user_uri",
                   "https://www.yelp.com/category/": "category_uri",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                   "http://www.w3.org/2000/01/rdf-schema#": "rdfs"
                   }

input_nt_file = "/home/ubuntu/vol1/virtuoso/import/yelp_business.nt"
# input_nt_file = "/home/ubuntu/DVML-P7/Code/Development/target_graph.nt"

idx = 1
input_files = ["/home/ubuntu/vol1/virtuoso/import/yelp_business.nt",
               "/home/ubuntu/vol1/virtuoso/import/yelp_user.nt",
               "/home/ubuntu/vol1/virtuoso/import/yelp_review.nt",
               "/home/ubuntu/vol1/virtuoso/import/yelp_tip.nt"]
classes = ["business", "user", "review", "tip"]
thresholds = [0.25, 0.2, 0.1, 0.05, 0.01]

shaper = Shaper(target_classes=target_classes, graph_file_input=input_files[idx], namespaces_dict=namespaces_dict, input_format=NT,
                instantiation_property="http://www.w3.org/2000/01/rdf-schema#Class")  # The predicate which is used to assign the target_classes to the subjects

output_file_shex = f"/home/ubuntu/DVML-P7/Code/SHACL/shaper_{classes[idx]}_{thresholds[idx]}.shex"

shaper.shex_graph(output_file=output_file_shex, acceptance_threshold=thresholds[idx])

# output_file_ttl = "/home/ubuntu/DVML-P7/Code/Development/shaper_yelp_business.ttl"
# shaper.shex_graph(output_file=output_file_ttl, acceptance_threshold=0.9, output_format=SHACL_TURTLE)

print("Done!")
print(f'In total it took', time.time()-start, 'seconds.')
