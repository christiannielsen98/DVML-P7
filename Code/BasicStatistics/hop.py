import pandas as pd
import numpy as np
import plotly.graph_objects as go

from Code.UtilityFunctions.get_data_path import get_path
from Code.UtilityFunctions.run_query import run_query

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_colwidth', 500)


hops = 1
hop_string = f"?s ?p{hops} ?o{hops} ."
hop_hist = dict()

while True:    
    query = f"""
    SELECT AVG(?hopCount) AS ?avgHopCount
    WHERE {{
        SELECT ?s (COUNT(?o{hops}) AS ?hopCount)
        WHERE {{
            {hop_string}
        }}
        GROUP BY ?s
    }}
    """
    print(query)
    result = float(run_query(query, as_dataframe=True)["avgHopCount.value"][0])
    
    if result == 0:
        break
    
    hop_hist[hops] = result
    hops += 1
    hop_string += f"\n?o{hops-1} ?p{hops} ?o{hops} ."
    for i in range(1, hops):
        hop_string += f"\nFILTER (?o{hops} != ?o{i}) ."
        # hop_string += f"\n{{?o{hops}}} MINUS {{?o{i}}} ."
        
    print(hop_hist)
    print(hop_hist)

print("Done!")
