# Basic Statistics
## (s,p,o)-Counts

### Number of Triples
```sparql
SELECT COUNT(*) as ?countTriples
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s ?p ?o .
}

>>> 242,247,823
```

### Number of Unique Subjects
```sparql
SELECT (COUNT(DISTINCT ?s) as ?countSubjects)
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s ?p ?o .
}

>>> 10,495,829
```

### Number of Unique Predicates
```sparql
SELECT (COUNT(DISTINCT ?p) as ?countPredicates)
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s ?p ?o .
}

>>> 144
```

### Number of Unique Objects
```sparql
SELECT COUNT(DISTINCT ?o) as ?countObjects
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s ?p ?o .
}

>>> 61,450,383
```

### Top 5 Most Prevalent Predicates
```sparql
SELECT ?predicate COUNT(?p) as ?countPredicate
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s ?predicate ?o .
}
GROUP BY ?predicate
ORDER BY DESC(?predicateCount)
LIMIT 5
```

|   |        **?p**                              |   **?predicateCount** |
|:-:|:-------------------------------------------|------------:|
| 0 | https://schema.org/knows                   | 105,225,474 |
| 1 | https://schema.org/checkinTime             |  13,353,332 |
| 2 | http://www.w3.org/2000/01/rdf-schema#Class |  10,342,179 |
| 3 | https://schema.org/dateCreated             |   9,887,092 |
| 4 | https://schema.org/url                     |   9,128,523 |


### Top 5 Most Prevalent Classes
```sparql
SELECT ?class (COUNT(DISTINCT ?s) as ?countClass)
FROM <http://www.yelpkg.com/yelp_kg>
WHERE {
  ?s rdfs:Class ?class .
}
GROUP BY ?class
ORDER BY DESC(?numSubjects)
LIMIT 5
```

|   | ?class                                          | ?numSubjects |
|:-:|:------------------------------------------------|-------------:|
| 0 | https://schema.org/UserReview                   |    6,990,280 |
| 1 | https://schema.org/Person                       |    1,987,897 |
| 2 | https://purl.archive.org/purl/yelp/ontology#Tip |      908,915 |
| 3 | https://schema.org/LocalBusiness                |      150,346 |
| 4 | https://schema.org/OpeningHoursSpecification    |      127,123 |



## In- and Outdegree
### Average Indegree
```sparql
SELECT AVG(?indegree) as ?avgIndegree
WHERE {
    SELECT ?o (COUNT(?p) as ?indegree)
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?s ?p ?o .
    }
    GROUP BY ?o
}

>>> 3.35
```

### Average Outdegree
```sparql
SELECT AVG(?outdegree) as ?avgOutdegree
WHERE {
    SELECT ?s COUNT(?p) as ?outdegree
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?s ?p ?o .
    }
    GROUP BY ?s
}

>>> 12.20
```



## Hop Diagram
