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

>> 1.311
```

## CQ 2: How many businesses of type "Restaurants" exist?
**SPARQL Query**:
```sparql
SELECT COUNT(DISTINCT(?business)) AS ?numberRestaurants
WHERE {
    ?business schema:category yelpcat:Restaurants .
}
```
|  **?numberRestaurants** |
|-------------------------|
|          52,268         |

**Correct Answer**:
```python
counter = 0
for row in business['categories']:
    if row is not None and "Restaurants" in row:
        counter += 1
print(counter)

>> 52.268
```

## CQ 3: How many businesses of type "Restaurants" have been reviwed?
**SPARQL Query**:
```sparql
SELECT DISTINCT (COUNT(?business) as ?businessCount)
WHERE {
    ?business schema:category yelpcat:Restaurants .
    ?review schema:about ?business .
}
```
|  **?businessCount**     |
|-------------------------|
|          52,268         |

**Correct Answer**
```python
review_unique_business = reviews.drop_duplicates(subset=['business_id'])
mask = review_unique_business['categories'].apply(lambda x: x is not None and "Restaurants" in x)
len(review_unique_business[mask])

>> 52268
```


## CQ 4: How many businesses have been reviewed?
**SPARQL Query**
```sparql
SELECT COUNT(DISTINCT(?business))
WHERE {
    ?review schema:about ?business .
    ?review rdfs:Class schema:UserReview .
}

```
|  **?businessCount**     |
|-------------------------|
|          150346         |

**Correct Answer**
```python
review_unique_business = reviews.drop_duplicates(subset=['business_id'])
len(review_unique_business)

>> 150346
```


## CQ 5: How many businesses have, on average, a rating of 4.5?
**SPARQL Query**
```sparql
SELECT COUNT(DISTINCT(?business)) AS ?count
WHERE {
    ?business schema:aggregateRating ?rating .
    FILTER (?rating = 4.5) .
}
```

|        **?count**       |
|-------------------------|
|           27181         |

**Correct Answer**
```python
business.groupby('stars')['stars'].count()

>>
stars
1.0     1986
1.5     4932
2.0     9527
2.5    14316
3.0    18453
3.5    26519
4.0    31125
4.5    27181
5.0    16307
Name: stars, dtype: int64
```


## CQ 6: What is the average rating across businesses?
**SPARQL Query**
```sparql
SELECT AVG(?rating) as ?averagerating
WHERE {
    ?business schema:aggregateRating ?rating .
}
```
|  **?averagerating**   |
|-----------------------|
|         3.5967        |

**Correct Answer**
```python
business['stars'].mean()

>> 3.5967
```


## CQ 7: How many businesses have been reviewed in Santa Barbara, CA?
**SPARQL Query**
```sparql
SELECT ?state ?city COUNT(?business) AS ?count_business
WHERE {
    ?business schema:category ?category .
    ?business schema:locatedInState ?state .
    ?business schema:locatedInCity ?city .
    FILTER(?city = "Santa Barbara")
}
GROUP BY ?state ?city
ORDER BY DESC(?count_business)
LIMIT 10
```
|  **Something**        |
|-----------------------|
|         Something     |


**Correct Answer**
```python
business_santa_barbara = business[business['city'] == "Santa Barbara"]
len(business_santa_barbara)

>> 3829
```

## CQ 8: What are the five most busy days, and for what business??
**SPARQL Query**
```sparql

```
|  **Something**        |
|-----------------------|
|         Something     |

**Correct Answer**
```python
checkins["Day"] = checkins["date"].apply(lambda x: x.split("-")[2][:2])
checkins["Month"] = checkins["date"].apply(lambda x: x.split("-")[1])
checkins["Year"] = checkins["date"].apply(lambda x: x.split("-")[0])

checkins.value_counts(subset=["business_id", "Day", "Month", "Year"], sort=True, ascending=False).head(5)

>>
business_id             Day  Month  Year
CySqUcNz8oPiQTu4EXTnig  25   06     2016    465
g50ImmCX3WY3koEDIzoKxg  30   08     2015    287
qfWWx0dVo1UuAhRfh03Dyw  28   08     2016    270
g50ImmCX3WY3koEDIzoKxg  28   08     2016    264
FBBeJO50xZiNIo3oFhAFRA  29   07     2017    254
dtype: int64
```


## CQ 9: Which are the top 10 most visisted businesses?
**SPARQL Query**
```sparql
SELECT ?business COUNT(?visit) AS ?countVisits
WHERE {
    ?business schema:checkinTime ?visit .
}
GROUP BY ?business 
ORDER BY DESC(COUNT(?visit))
LIMIT 10
```

|                     **?business**                      | ?countVisits |
|--------------------------------------------------------| ------------ |
| https://example.org/business_id/-QI8Qi8XWH3D8y8ethnajA |	  52,129    |
| https://example.org/business_id/FEXhWNCMkv22qG04E83Qjg |	  40,092    |
| https://example.org/business_id/Eb1XmmLWyt_way5NNZ7-Pw |	  37,553    |
| https://example.org/business_id/c_4c5rJECZSfNgFj7frwHQ |	  37,511    |
| https://example.org/business_id/4i4kmYm9wgSNyF1b6gKphg |	  31,163    |
| https://example.org/business_id/8O35ji_yOMVJmZ6bl96yhQ |	  29,599    |
| https://example.org/business_id/VQcCL9PiNL_wkGf-uF3fjg |	  28,917    |
| https://example.org/business_id/ac1AeYqs8Z4_e2X5M3if2A |	  21,527    |
| https://example.org/business_id/QTbahs-GVuWYL5yfdjH34A |	  21,478    |
| https://example.org/business_id/ytynqOUb3hjKeJfRj5Tshw |	  18,604    |

**Correct Answer**
```python
checkins.value_counts(subset=["business_id"], sort=True, ascending=False).head(10)

>>
business_id           
-QI8Qi8XWH3D8y8ethnajA    52144
FEXhWNCMkv22qG04E83Qjg    40109
Eb1XmmLWyt_way5NNZ7-Pw    37562
c_4c5rJECZSfNgFj7frwHQ    37518
4i4kmYm9wgSNyF1b6gKphg    31168
8O35ji_yOMVJmZ6bl96yhQ    29606
VQcCL9PiNL_wkGf-uF3fjg    28927
ac1AeYqs8Z4_e2X5M3if2A    21542
QTbahs-GVuWYL5yfdjH34A    21487
ytynqOUb3hjKeJfRj5Tshw    18615
dtype: int64
```

NOTE: The difference is caused by the fact that identical triples are not possible in RDF.

## CQ 10: How many people have written a review on Yelp?
**SPARQL Query**
```sparql

```

**Correct Answer**
```python
reviews.drop_duplicates(subset=['user_id']).shape[0]

>> 1987929
```

## CQ 11: How many users have 10 friends?
**SPARQL Query**
```sparql

```


**Correct Answer**
```python
users["amountFriends"] = users["friends"].apply(lambda x: len(x.split(",")))
users[users["amountFriends"] == 10].shape[0]

>> 13579
```

## CQ 12: How many friends does a user have on average?
**SPARQL Query**
```sparql

```

**Correct Answer**
```python
users["amountFriends"].mean()

>> 53.375
```



## CQ 13: How many users have authored 10 reviews or tips?
**SPARL Query**
```sparql

```

**Correct Answer**
```python
reviews.groupby("user_id").size().reset_index(name="count").query("count == 10").shape[0]

>> 14119
```



## CQ 14: How many reviews or tips does a user make on average every month?
**SPARL Query**
```sparql

```

**Correct Answer**
```python

```


