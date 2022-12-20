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
  VALUES ?city {{{list_of_cities}}} .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
}}
"""
wikidata_query(sparql_query=sparql_query)
```
Results:
|     | city.value | cityLabel.value | population.value |
| :-- | :--------- | :-------------- | ---------------: |
| 0   | wd:Q6346   | Indianapolis    | 887642           |
| 1   | wd:Q159288 | Santa Barbara   | 88665            |
| 2   | wd:Q23197  | Nashville       | 684410           |
| 3   | wd:Q18575  | Tucson          | 542629           |
| 4   | wd:Q49255  | Tampa           | 384959           |
| 5   | wd:Q34404  | New Orleans     | 383997           |
| 6   | wd:Q38022  | St. Louis       | 301578           |
| 7   | wd:Q49225  | Reno            | 264165           |
| 8   | wd:Q1345   | Philadelphia    | 1603797          |
| 9   | wd:Q2096   | Edmonton        | 1010899          |
### DBpedia

```python
list_of_cities = '"Philadelphia"@en "Tucson, Arizona"@en "Tampa, Florida"@en "Indianapolis"@en "Nashville, Tennessee"@en "New Orleans"@en "Reno, Nevada"@en "Edmonton"@en "St. Louis"@en "Santa Barbara, California"@en'
query = f"""
SELECT DISTINCT ?city ?population ?cityname
WHERE {{
    ?city a dbo:City .
    ?city dbo:populationTotal ?population .
    ?city rdfs:label ?cityname .
    VALUES ?cityname{{{list_of_cities}}}
}}
"""
Results:
dbpedia_query(query)
```
|     | city.value                | cityLabel.value           | population.value |
| :-- | :------------------------ | :------------------------ | ---------------: |
| 0   | dbo:Indianapolis          | Indianapolis              |           887642 |
| 1   | dbo:Santa_Barbara,_Cal... | Santa Barbara, California |            88665 |
| 2   | dbo:Nashville,_Tennessee  | Nashville, Tennessee      |           715884 |
| 3   | dbo:Tucson,_Arizona       | Tucson, Arizona           |           542629 |
| 4   | dbo:Tampa,_Florida        | Tampa, Florida            |           384959 |
| 5   | dbo:New_Orleans           | New Orleans               |           383997 |
| 6   | dbo:St._Louis             | St. Louis                 |           301578 |
| 7   | dbo:Reno,_Nevada          | Reno, Nevada              |           264165 |
| 8   | dbo:Philadelphia          | Philadelphia              |          1603797 |
| 9   | dbo:Edmonton              | Edmonton                  |          1010899 |


### Yago
**Yago does not contain population data. This knowledge graph is not investigated further, because it does not satisfy our requirenments**

## CQ 2: How many of 10 random cities from the yelp dataset are in the external KG?
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
    SELECT DISTINCT ?city ?cityLabel ?state ?stateLabel
    WHERE{{
    FILTER(CONTAINS(?cityLabel, "{key}"@en)).
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
df[['city.value', 'cityLabel.value', 'state.value', 'stateLabel.value']]
```
Results:
|     | city.value  | cityLabel.value                  | state.value | stateLabel.value |
| :-- | :---------- | :------------------------------- | :---------- | ---------------- |
| 0   | wd:Q5337787 | Edgemont                         | wd:Q1400    | Pennsylvania     |
| 1   | wd:Q952992  | Safety Harbor                    | wd:Q812     | Florida          |
| 2   | wd:Q1083022 | Folsom                           | wd:Q1408    | New Jersey       |
| 3   | wd:Q1133576 | Fort Washington                  | wd:Q1400    | Pennsylvania     |
| 4   | wd:Q1994608 | Avondale                         | wd:Q1588    | Louisiana        |
| 5   | wd:Q1072819 | Willingboro Township, New Jersey | wd:Q1408    | New Jersey       |
| 6   | wd:Q1375820 | Glen Carbon, Illinois            | wd:Q1204    | Illinois         |
| 7   | wd:Q1072657 | Mount Laurel                     | wd:Q1408    | New Jersey       |
| 8   | wd:Q986631  | Plainfield                       | wd:Q1415    | Indiana          |
| 9   | wd:Q2375799 | Land O' Lakes                    | wd:Q812     | Florida          |

## And how many of these cities have a population? 
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
Results:
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
    SELECT ?city ?cityName ?state ?stateName
    WHERE {{
        ?city dbo:subdivision ?state.
        ?city dbp:name ?cityName.
        ?state dbp:name ?stateName. 
        FILTER(contains(str(?cityName), "{key}") && contains(str(?stateName), "{value}")).
    }}

    """
    df2 = dbpedia_query(sparql_query=sparql_query)
    df = pd.concat([df, df2], ignore_index=True)
df[['city.value', 'cityName.value', 'state.value', 'stateName.value']]
```
Results:
|     | city.value                           | cityName.value                   | state.value    | stateName.value |
| :-- | :----------------------------------- | :------------------------------- | :------------- | --------------- |
| 0   | dbo:Safety_Harbor,_Florida           | Safety Harbor, Florida           | dbo:Florida    | Florida         |
| 1   | dbo:Folsom,_New_Jersey               | Folsom, New Jersey               | dbo:New_Jersey | New Jersey      |
| 2   | dbo:Avondale,_Louisiana              | Avondale, Louisiana              | dbo:Louisiana  | Louisiana       |
| 3   | dbo:Willingboro_Township,_New_Jersey | Willingboro Township, New Jersey | dbo:New_Jersey | New Jersey      |
| 4   | dbo:Glen_Carbon,_Illinois            | Glen Carbon                      | dbo:Illinois   | Illinois        |
| 5   | dbo:Mount_Laurel,_New_Jersey         | Mount Laurel, New Jersey         | dbo:New_Jersey | New Jersey      |

Not all cities are in the list because they are not labelled thoroughly in DBPedia.
## And how many of these cities have a population? 
```python
list_of_cities= '"Safety Harbor, Florida"@en "Folsom, New Jersey"@en "Avondale, Louisiana"@en "Willingboro Township, New Jersey"@en "Glen Carbon"@en "Mount Laurel, New Jersey"@en'

query = f"""
SELECT DISTINCT ?city ?population ?cityname
WHERE {{
    ?city dbo:populationTotal ?population .
    ?city rdfs:label ?cityname .
    VALUES ?cityname {{{list_of_cities}}}.
    FILTER (lang(?cityname) = "en")
}}
"""
dbpedia_query(query)[['city.value','cityname.value', 'population.value']]
```
Results:
|     | city.value                | cityname.value                   | population.value |
| :-- | :------------------------ | :------------------------------- | ---------------- |
| 0   | dbo:Avondale,_Louisiana   | Avondale, Louisiana              | 4582             |
| 1   | dbo:Safety_Harbor,_Flo... | Safety Harbor, Florida           | 17072            |
| 2   | dbo:Mount_Laurel,_New_... | Mount Laurel, New Jersey         | 41864            |
| 3   | dbo:Folsom,_New_Jersey    | Folsom, New Jersey               | 1885             |
| 4   | dbo:Willingboro_Townsh... | Willingboro Township, New Jersey | 31889            |

Missing population of Glen Carbon.

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
|     | stateLabel.value | numCities.value |
| :-- | :--------------- | --------------- |
| 0   | Alberta          | 20              |
| 1   | Florida          | 391             |
| 2   | Nevada           | 22              |
| 3   | Tennessee        | 342             |
| 4   | Missouri         | 682             |
| 5   | Indiana          | 511             |
| 6   | Arizona          | 91              |
| 7   | Louisiana        | 192             |
| 8   | New Jersey       | 92              |
| 9   | Pennsylvania     | 60              |

### DBpedia
```python
# Cities of list entities in DBpedia from https://dbpedia.org/page/Template:Cities_in_the_United_States
sparql_query = """
SELECT (COUNT(DISTINCT ?city) AS ?numCities) ?citiesInState
WHERE {
    ?city a dbo:City .
    ?city dct:subject ?location .
    ?location rdfs:label ?citiesInState
    VALUES ?citiesInState {
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
|     | citiesInState.value    | numCities.value |
| :-- | :--------------------- | --------------- |
| 0   | Cities in Pennsylvania | 57              |
| 1   | Cities in Florida      | 267             |
| 2   | Cities in Alberta      | 19              |
| 3   | Cities in Indiana      | 118             |
| 4   | Cities in Nevada       | 20              |
| 5   | Cities in Tennessee    | 181             |
| 6   | Cities in Missouri     | 671             |
| 7   | Cities in Louisiana    | 70              |
| 8   | Cities in Arizona      | 47              |

The number of cities of New Jersey is missing.

## CQ 4: What items exist in abstract concepts that are similar to categories in the Yelp Open Dataset? We randomly choose five concepts.

### Wikidata
Explanation of Q and P codes:
- P279: subclass of
- Q40050: Drink
- Q177: Pizza
- Q11707: Restaurant
- Q4830453: Business
- Q786803: Car dealership

```sparql
SELECT ?value ?valueLabel (COUNT (DISTINCT ?category) AS ?count)
    WHERE {
        VALUES ?value {wd:Q40050 wd:Q177 wd:Q11707 wd:Q4830453 wd:Q786803}
        ?category wdt:P279+ ?value .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    GROUP BY ?value ?valueLabel
```
Result:
|     | value.value | valueLabel.value | count.value |
| :-- | :---------- | :--------------- | ----------- |
| 0   | wd:Q11707   | restaurant       | 234         |
| 1   | wd:Q177     | pizza            | 60          |
| 2   | wd:Q40050   | drink            | 6662        |
| 3   | wd:Q786803  | car dealership   | 1           |
| 4   | wd:Q4830453 | business         | 3518        |

### DBpedia
```sparql
SELECT ?value (COUNT (DISTINCT ?category) AS ?count)
WHERE {
    VALUES ?value {dbo:Beverage dbo:Car_dealership dbo:Business dbo:Restaurant dbo:Pizza}
    ?category rdf:type ?value
}
GROUP BY ?value
```
Result:
|     | value.value    | count.value |
| :-- | :------------- | ----------- |
| 0   | dbo:Beverage   | 1884        |
| 1   | dbo:Restaurant | 2838        |

The number of pizza, business and car dealership is missing, because no entities in dbpedia seems to be an rdf:type of those entities.