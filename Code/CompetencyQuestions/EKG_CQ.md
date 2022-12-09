
# CQ: What is the population of New York City?

## Wikidata
```sparql
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
Yago does not contain population data.

# CQ: How many cities are in state of California?

## Wikidata
P31 = instance of  
P279 = subclass of  
Q1093829 = city in the United States  
Q4946305 = borough in the United States  
Q515 = city  
Q15127012 = town in the United States  
P131 = located in the administrative territorial entity  
Q99 = California

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
| **number of cities** |
|:--------------------:|
| 484                  |
## DBpedia
```sparql
SELECT COUNT(DISTINCT ?city)
WHERE {
    ?city a dbo:City .
    ?city dct:subject ?location .
    ?location rdfs:label ?var
    VALUES ?var {"Cities in New York (state)"@en}
}
```
Result:
| **number of cities** |
|:--------------------:|
| 474                  |

# CQ: What drinks exist that are beverages?

## Wikidata
```sparql
SELECT DISTINCT ?beverage ?beverageLabel
WHERE {
?beverage wdt:P279+ wd:Q40050 .
FILTER NOT EXISTS{
  FILTER (!REGEX(?beverageLabel,"^Q","i"))
}
SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . }
}
```
NOT WORKING AS IT SHOULD

## DBpedia
```sparql
SELECT COUNT DISTINCT ?beverage
WHERE {
?beverage rdf:type dbo:Beverage
}
```