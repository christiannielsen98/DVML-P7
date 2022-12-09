
# CQ 1: What is the population of New York City?

## Wikidata
Explanation of Q and P codes:
- P1082: population
- P585: point in time
- Q159288: Santa Barbara
```sparql
SELECT ?city ?cityLabel ?population
WHERE {
  ?city p:P1082 ?statement .
  ?statement ps:P1082 ?population .
  ?statement pq:P585 ?date .
  FILTER NOT EXISTS {
    ?city p:P1082/pq:P585 ?date2 .
    FILTER(?date2 > ?date)
  }
  VALUES ?city {wd:Q159288} .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
```

## DBpedia
```sparql
SELECT DISTINCT ?city ?population ?cityname
WHERE {
    ?city a dbo:City .
    ?city dbo:populationTotal ?population .
    ?city rdfs:label ?cityname .
    VALUES ?cityname{"Santa Barbara, California"@en}
}
```
| **city** | **population** | **cityname** |
|----------|----------------|--------------|
| dbo:Santa_Barbara,_California | "88665"^^xsd:nonNegativeInteger | "Santa Barbara, California"@en|
	

## Yago
**Yago does not contain population data.**

# CQ 2: How many cities are in state of California?

## Wikidata
Explanation of Q and P codes:
- P31: instance of  
- P279: subclass of
- Q1093829: city in the United States
- Q4946305: borough in the United States
- Q515: city
- Q15127012: town in the United States
- P131: located in the administrative territorial entity
- Q99: California

```sparql
SELECT (COUNT(DISTINCT ?city) as ?count)
WHERE
{
  {?city wdt:P31/wdt:P279* wd:Q1093829.}
  UNION
  {?city wdt:P31/wdt:P279* wd:Q4946305.}
  UNION
  {?city wdt:P31/wdt:P279* wd:Q515.}
  UNION
  {?city wdt:P31/wdt:P279* wd:Q15127012.}
  ?city wdt:P131/wdt:P131 wd:Q99.
}
```
Result:
| **?count** |
|------------|
| 484        |
## DBpedia
```sparql
SELECT (COUNT(DISTINCT ?city) AS ?count)
WHERE {
    ?city a dbo:City .
    ?city dct:subject ?location .
    ?location rdfs:label ?var
    VALUES ?var {"Cities in New York (state)"@en}
}
```
| **?count** |
|------------|
| 474        |

# CQ 3: What drinks exist that are beverages?

## Wikidata
Explanation of Q and P codes:
- P279: subclass of
- Q40050: Drink

```sparql
SELECT (COUNT (DISTINCT ?beverage) AS ?count)
WHERE {
  ?beverage wdt:P279+ wd:Q40050 .
}
```
| **?count** |
|------------|
| 6140       |

## DBpedia
```sparql
SELECT (COUNT (DISTINCT ?beverage) AS ?count)
WHERE {
  ?beverage rdf:type dbo:Beverage
}
```
| **?count** |
|------------|
| 1884       |
