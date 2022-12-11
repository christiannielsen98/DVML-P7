# Yelp KG Competency Question Example Queries

## CQ 1: How many different types of businesses are defined in Yelp?
**SPARQL Query**:
```sparql
SELECT COUNT(DISTINCT(?category)) AS ?uniqueCategories
WHERE {
    ?business schema:category ?category .
}
```

| **?uniqueCategories** |
|-----------------------|
|         1,311         |

**Correct Answer**:
```python
unique_categories = {category for sublist in business['categories'] if sublist for category in sublist}
print(len(unique_categories))

>> 1,311
```

## CQ 2: How many businesses of type "Restaurants" exist?
**SPARQL Query**:
```sparql
SELECT COUNT(?business) AS ?numRestaurants
WHERE {
    ?business schema:category yelp_category:Restaurants .
}
```
|  **?numRestaurants**  |
|-----------------------|
|         52,268        |

** Correct Answer**:
```python
counter = 0
for row in business['categories']:
    if row is not None and "Restaurants" in row:
        counter += 1
print(counter)

>> 52,268
```

## CQ 3: How many businesses of type "Restaurants" have been reviwed?



## CQ 4: How many businesses have been reviewed?



## CQ 5: How many businesses have, on average, a rating of 4.5?



## CQ 6: What is the average rating across businesses?



## CQ 7: How many businesses have been reviewed in New York, NY?



## CQ 8: Which business is the most visited on day X?



## CQ 9: Which are the top 10 most visisted businesses?



## CQ 10: How many of the Yelp categories are also mapped to schema.org?



## CQ 11: How many people have written a review or tip on Yelp?



## CQ 12: How many users have 10 friends?



## CQ 13: How many friends does a user have on average?



## CQ 14: How many users have authored 10 reviews or tips?



## CQ 15: How many reviews or tips does a user make on average every month?


