import sys
import pandas as pd

from Code.UtilityFunctions.get_data_path import get_path
from Code.create_nt_files import create_nt_files, create_tip_nt_file
from Code.KnowledgeGraphEnrichment.yelp_wiki_category_mappings import create_wiki_category_nt_files
from Code.KnowledgeGraphEnrichment.location_from_wikidata import create_locations_nt

sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])

create_nt_files()
create_tip_nt_file()
create_wiki_category_nt_files()
create_locations_nt()