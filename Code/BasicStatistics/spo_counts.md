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
### Average Indegree (overall)
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

### Average Outdegree (overall)
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

### Average Indegree (business)
```sparql
SELECT AVG(?indegree) as ?avgIndegree
WHERE {
    SELECT ?o (COUNT(?p) as ?indegree)
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?o rdfs:Class schema:LocalBusiness .
        ?s ?p ?o .
    }
    GROUP BY ?o
}

>>> 46.49
```

### Average Outdegree (business)
```sparql
SELECT AVG(?outdegree) as ?avgOutdegree
WHERE {
    SELECT ?s COUNT(?p) as ?outdegree
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?s rdfs:Class schema:LocalBusiness .
        ?s ?p ?o .
    }
    GROUP BY ?s
}

>>> 114.02
```

### Average Indegree (user)
```sparql
SELECT AVG(?indegree) as ?avgIndegree
WHERE {
    SELECT ?o (COUNT(?p) as ?indegree)
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?o rdfs:Class schema:Person .
        ?s ?p ?o .
    }
    GROUP BY ?o
}

>>> 3.97
```

### Average Outdegree (user)
```sparql
SELECT AVG(?outdegree) as ?avgOutdegree
WHERE {
    SELECT ?s COUNT(?p) as ?outdegree
    FROM <http://www.yelpkg.com/yelp_kg>
    WHERE {
        ?s rdfs:Class schema:Person .
        ?s ?p ?o .
    }
    GROUP BY ?s
}

>>> 74.10
```

## Unique predicates in JSON-files
```python
import json
from Code.UtilityFunctions.get_data_path import get_path
predicates = set()
# Open JSON file for reading
files = [
        'yelp_academic_dataset_business.json',
        'yelp_academic_dataset_user.json',
        'yelp_academic_dataset_review.json',
        'yelp_academic_dataset_checkin.json',
        'yelp_academic_dataset_tip.json'
    ]
for i in files:
    with open(file=get_path(i), mode="r") as file:
        # Iterate through each line in the file
        for line in file:
            # Parse line as a dictionary
            data = json.loads(line)
            for keys in data.keys():
                if keys == 'attributes' and type(data[keys]) != type(None):
                    for key in data[keys].keys():
                        if key in ["BusinessParking", "GoodForMeal", "Ambience", "Music", "BestNights", "HairSpecializesIn", "DietaryRestrictions"]:
                            dictionaries = json.loads(data[keys][key].replace("'", '"').replace("None", "null").replace('u"', '"').replace("True", "true").replace("False", "false"))
                            if type(dictionaries) != type(None):
                                for k in dictionaries.keys():
                                    predicates.add(k)
                        predicates.add(key)
                if keys == 'hours' and type(data[keys]) != type(None):
                    for key in data[keys].keys():
                        predicates.add(key)
                predicates.add(keys)
len(predicates)

>>> 133
```
