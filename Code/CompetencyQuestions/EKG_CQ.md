# EKG Competency Question Example Queries
SPARQL Endpoints for the different EKGs are available at the following locations:
| **EKG**  | **SPARQL Endpoint**               |
| -------- | --------------------------------- |
| Wikidata | https://query.wikidata.org/       |
| DBPedia  | https://dbpedia.org/sparql        |
| YAGO     | https://yago-knowledge.org/sparql |

## CQ 1: How many people live in the city of top ten most prevelent cities in Yelp?

### Wikidata
Explanation of P codes:
- P1082: population
- P585: point in time

```python
list_of_cities = "wd:Q1345 wd:Q18575 wd:Q49255 wd:Q6346 wd:Q23197 wd:Q34404 wd:Q49225 wd:Q2096 wd:Q38022 wd:Q159288"
```

```sparql
SELECT ?city ?population ?cityLabel 
WHERE {{
  ?city p:P1082 ?statement .
  ?statement ps:P1082 ?population .
  ?statement pq:P585 ?date .
  FILTER NOT EXISTS {{
    ?city p:P1082/pq:P585 ?date2 .
    FILTER(?date2 > ?date)
  }}
  VALUES ?city {{{list_of_cities}}} .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
```
| **?city**  | **?cityLabel** | **?population** |
| :--------- | :------------- | :-------------- |
| wd:Q6346   | Indianapolis   | 887642          |
| wd:Q159288 | Santa Barbara  | 88665           |
| wd:Q23197  | Nashville      | 684410          |
| wd:Q18575  | Tucson         | 542629          |
| wd:Q49255  | Tampa          | 384959          |
| wd:Q34404  | New Orleans    | 383997          |
| wd:Q38022  | St. Louis      | 301578          |
| wd:Q49225  | Reno           | 264165          |
| wd:Q1345   | Philadelphia   | 1603797         |
| wd:Q2096   | Edmonton       | 1010899         |
### DBpedia

```python
list_of_cities = '"Philadelphia"@en "Tucson, Arizona"@en "Tampa, Florida"@en "Indianapolis"@en "Nashville, Tennessee"@en "New Orleans"@en "Reno, Nevada"@en "Edmonton"@en "St. Louis"@en "Santa Barbara, California"@en'
```
```sparql
SELECT DISTINCT ?city ?population ?cityname
WHERE {
    ?city a dbo:City .
    ?city dbo:populationTotal ?population .
    ?city rdfs:label ?cityname .
    VALUES ?cityname{list_of_cities}
}
```

	
| **?city**                 | **?cityname**             | **?population** |
| :------------------------ | :------------------------ | :-------------- |
| dbo:Indianapolis          | Indianapolis              | 887642          |
| dbo:Santa_Barbara,_Cal... | Santa Barbara, California | 88665           |
| dbo:Nashville,_Tennessee  | Nashville, Tennessee      | 715884          |
| dbo:Tucson,_Arizona       | Tucson, Arizona           | 542629          |
| dbo:Tampa,_Florida        | Tampa, Florida            | 384959          |
| dbo:New_Orleans           | New Orleans               | 383997          |
| dbo:St._Louis             | St. Louis                 | 301578          |
| dbo:Reno,_Nevada          | Reno, Nevada              | 264165          |
| dbo:Philadelphia          | Philadelphia              | 1603797         |
| dbo:Edmonton              | Edmonton                  | 1010899         |


### Yago
**Yago does not contain population data.**



## CQ 2: How many of 10 random cities from the yelp dataset are in both Wikidata and DBpedia?
### How many of these cities have a population? 
\
sample_dict_updated is a dictionary of 10 random cities from the yelp dataset. The keys are the city names and the values are the states.
- Q486972: Human settlement
- P131: located in the administrative territorial entity
- P279: subclass of
- P31: instance of

```python
sample_dict_updated = {'Edgemont': 'Pennsylvania',
 'Safety Harbor': 'Florida',
 'Folsom': 'New Jersey',
 'Fort Washington': 'Pennsylvania',
 'Avondale': 'Louisiana',
 'Willingboro': 'New Jersey',
 'Glen Carbon': 'Illinois',
 'Mount Laurel': 'New Jersey',
 'Plainfield': 'Indiana',
 "Land O' Lakes": 'Florida'}

df = pd.DataFrame()
for key, value in sample_dict_updated.items():
    sparql_query = f"""
    SELECT DISTINCT ?val ?val2 ?city ?cityLabel ?state ?stateLabel
    WHERE{{
    VALUES ?cityLabel {{"{key}"@en}}
    VALUES ?stateLabel {{"{value}"@en}}
    ?city rdfs:label ?cityLabel.
    ?city wdt:P131/wdt:P131 | wdt:P131 ?state .
    ?city wdt:P31/wdt:P279* wd:Q486972 .
    ?state rdfs:label ?stateLabel .
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} 
    }}
    LIMIT 1
    """
    df2 = wikidata_query(sparql_query=sparql_query)
    df = pd.concat([df, df2], ignore_index=True)
df[['val.value', 'val2.value', 'city.value', 'cityLabel.value', 'state.value', 'stateLabel.value']]
```

| val.value       | val2.value   | city.value  | cityLabel.value                  | state.value | stateLabel.value |
| :-------------- | :----------- | :---------- | :------------------------------- | :---------- | :--------------- |
| Edgemont        | Pennsylvania | wd:Q5337787 | Edgemont                         | wd:Q1400    | Pennsylvania     |
| Safety Harbor   | Florida      | wd:Q952992  | Safety Harbor                    | wd:Q812     | Florida          |
| Folsom          | New Jersey   | wd:Q1083022 | Folsom                           | wd:Q1408    | New Jersey       |
| Fort Washington | Pennsylvania | wd:Q1133576 | Fort Washington                  | wd:Q1400    | Pennsylvania     |
| Avondale        | Louisiana    | wd:Q1994608 | Avondale                         | wd:Q1588    | Louisiana        |
| Willingboro     | New Jersey   | wd:Q1072819 | Willingboro Township, New Jersey | wd:Q1408    | New Jersey       |
| Glen Carbon     | Illinois     | wd:Q1375820 | Glen Carbon (Illinois)           | wd:Q1204    | Illinois         |
| Mount Laurel    | New Jersey   | wd:Q1072657 | Mount Laurel                     | wd:Q1408    | New Jersey       |
| Plainfield      | Indiana      | wd:Q986631  | Plainfield                       | wd:Q1415    | Indiana          |
| Land O' Lakes   | Florida      | wd:Q2375799 | Land O' Lakes                    | wd:Q812     | Florida          |

And how many of these cities have a population? 
```python
sparql_query = f"""
SELECT ?city ?population ?cityLabel 
WHERE {{
  ?city p:P1082 ?statement .
  ?statement ps:P1082 ?population .
  ?statement pq:P585 ?date .
  FILTER NOT EXISTS {{
    ?city p:P1082/pq:P585 ?date2 .
    FILTER(?date2 > ?date)
  }}
  VALUES ?city {{{list_city_qid}}} .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""

wikidata_query(sparql_query=sparql_query)[['city.value','cityLabel.value', 'population.value']]
```
| city.value  | cityLabel.value      | population.value |
| :---------- | :------------------- | --------------: |
| wd:Q952992  | Safety Harbor        |      17072       |
| wd:Q986631  | Plainfield           |      34625       |
| wd:Q1072657 | Mount Laurel         |      44633       |
| wd:Q1072819 | Willingboro Township |      31889       |
| wd:Q1083022 | Folsom               |       1811       |
| wd:Q1133576 | Fort Washington      |       5910       |
| wd:Q1375820 | Glen Carbon          |      13842       |
| wd:Q1994608 | Avondale             |       4582       |
| wd:Q2375799 | Land O' Lakes        |      35929       |

Edgemont is not in the list because it does not have a population.

## DBPedia
```python

df = pd.DataFrame()
for key, value in sample_dict_updated.items():
    sparql_query = f"""
    SELECT ?val ?city ?cityName ?county ?state ?stateName
    WHERE {{
    VALUES ?val {{"{key}"}}
    VALUES ?val2 {{"{value}"}}
    ?city a dbo:City ;
            dbp:name ?cityName  .
            ?county dbo:county ?city .
    ?county dbo:state ?state .
    ?state dbp:name ?stateName .
    FILTER(contains(str(?cityName), ?val) && contains(str(?stateName), ?val2)).
    }}

    """
    df2 = dbpedia_query(sparql_query=sparql_query)
    df = pd.concat([df, df2], ignore_index=True)
```

| val.value |
| :-------- |
| Empty     |
## CQ 3: How many cities are in the 10 most prevelent states/provinces in Yelp?

### Wikidata
Explanation of Q and P codes:
- P31: instance of  
- P279: subclass of
- Q1093829: city in the United States
- Q4946305: borough in the United States
- Q515: city
- Q15127012: town in the United States
- P131: located in the administrative territorial entity
- Q99: California

```python
wd_state_list = 'wd:Q1400 wd:Q812 wd:Q1509 wd:Q1415 wd:Q1581 wd:Q1588 wd:Q816 wd:Q1408 wd:Q1227 wd:Q1951'
sparql_query = f"""
SELECT DISTINCT ?stateLabel ?numCities
WHERE {{
VALUES ?state {{{wd_state_list}}}
{{?state wdt:P31 wd:Q35657 .}}
UNION
{{?state wdt:P31 wd:Q11828004 .}}

{{ SELECT ?state (COUNT(DISTINCT ?city) as ?numCities)
WHERE
{{
    {{?city wdt:P31/wdt:P279* wd:Q1093829.}}
    UNION
    {{?city wdt:P31/wdt:P279* wd:Q515.}}
    UNION
    {{?city wdt:P31/wdt:P279* wd:Q15127012.}}
    ?city wdt:P131/wdt:P131 | wdt:P131 ?state .
}}
GROUP BY ?state
}}
SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""

wikidata_query(sparql_query=sparql_query)[['stateLabel.value', 'numCities.value']]
```
Result:
| stateLabel.value | numCities.value |
| :--------------- | --------------: |
| Alberta          |              20 |
| Florida          |             391 |
| Nevada           |              22 |
| Tennessee        |             342 |
| Missouri         |             682 |
| Indiana          |             511 |
| Arizona          |              91 |
| Louisiana        |             192 |
| New Jersey       |              92 |
| Pennsylvania     |              60 |

### DBpedia
```python
# Cities of list entities in DBpedia from https://dbpedia.org/page/Template:Cities_in_the_United_States
sparql_query = """
SELECT (COUNT(DISTINCT ?city) AS ?count) ?var
WHERE {
    ?city a dbo:City .
    ?city dct:subject ?location .
    ?location rdfs:label ?var
    VALUES ?var {
      "Cities in Florida"@en  
      "Cities in Nevada"@en
      "Cities in Tennessee"@en
      "Cities in Missouri"@en
      "Cities in Indiana"@en
      "Cities in Arizona"@en
      "Cities in Louisiana"@en
      "Cities in New Jersey"@en
      "Cities in Pennsylvania"@en
      "Cities in Alberta"@en
    }
}
"""
dbpedia_query(sparql_query=sparql_query)
```
Result:
| var.value              | count.value |
| :--------------------- | ----------: |
| Cities in Pennsylvania | 57          |
| Cities in Florida      | 267         |
| Cities in Alberta      | 19          |
| Cities in Indiana      | 118         |
| Cities in Nevada       | 20          |
| Cities in Tennessee    | 181         |
| Cities in Missouri     | 671         |
| Cities in Louisiana    | 70          |
| Cities in Arizona      | 47          |

The number of cities of New Jersey is missing.

## CQ 4: What drinks exist that are beverages?

### Wikidata
Explanation of Q and P codes:
- P279: subclass of
- : Drink
- : Pizza
- : Restaurant
- : LocalBusiness
- : Autoshop

```sparql
SELECT ?value ?valueLabel (COUNT (DISTINCT ?beverage) AS ?count)
    WHERE {
        VALUES ?value {wd:Q40050 wd:Q2095}
        ?beverage wdt:P279+ ?value .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    GROUP BY ?value ?valueLabel
```
Result:
| value.value | valueLabel.value | count.value |
| :---------- | :--------------- | :---------- |
| wd:Q2095    | food             | 26741       |
| wd:Q40050   | drink            | 6661        |

### DBpedia
```sparql
SELECT ?value (COUNT (DISTINCT ?beverage) AS ?count)
WHERE {
    VALUES ?value {dbo:Beverage dbo:Food}
    ?beverage rdf:type ?value
}
GROUP BY ?value
```
Result:
| value.value  | count.value |
| :----------- | :---------- |
| dbo:Beverage | 1884        |
| dbo:Food     | 13111       |