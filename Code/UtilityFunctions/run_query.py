from SPARQLWrapper import SPARQLWrapper, JSON
from pandas import json_normalize


def run_query(query, as_dataframe=False, do_print=False):
    endpoint = SPARQLWrapper("http://localhost:8890/sparql")
    endpoint.setReturnFormat(JSON)
    endpoint.setTimeout(1200)
    endpoint.method = 'POST'
    
    PREFIX= """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
    """
    
    endpoint.setQuery(PREFIX+query)
    results = endpoint.query().convert()['results']
    if len(results['bindings']) <= 0:
        print("Empty resultset")
        
    if not as_dataframe:
        if do_print:
            for binding in results['bindings']:    
                print("; ".join([var+": "+ binding[var]['value']  for var in binding.keys()  ]))
        return results['bindings']
    
    else:
        # pdata = pd.DataFrame.from_dict(results['bindings'], orient="index")
        pdata = json_normalize(results['bindings'])
        if do_print:
            print(pdata)
        return pdata