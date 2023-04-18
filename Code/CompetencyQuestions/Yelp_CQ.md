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

>> 52,268
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

| numberRestaurants.value |
| :---------------------- |
| 52268                   |


**Correct Answer**
```python
review_unique_business = reviews.drop_duplicates(subset=['business_id'])
mask = review_unique_business['categories'].apply(lambda x: x is not None and "Restaurants" in x)
len(review_unique_business[mask])

>> 52,268
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
|  **?businessCount**  |
|----------------------|
|        150,346       |

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

|  **?count**  |
|--------------|
|    27,181    |

**Correct Answer**
```python
business[business['stars'] == 4.5].groupby('stars')['stars'].count()

>>
stars
4.5    27181
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
SELECT COUNT(DISTINCT(?s)) AS ?count_business
WHERE {
    ?s yelpont:locatedInCity 'Santa Barbara'^^xsd:string.
}
```

|  **?count_business**  |
|-----------------------|
|         3,829         |


**Correct Answer**
```python
business_santa_barbara = business[business['city'] == "Santa Barbara"]
len(business_santa_barbara)

>> 3829
```

## CQ 8: What business has the highest number of visists in one day?
**SPARQL Query**
```sparql
SELECT ?business ?year ?month ?day COUNT(?visit) as ?numberOfVisits
WHERE {
    ?business schema:checkinTime ?visit .
    BIND (day(?visit)  as ?day)
    BIND (month(?visit) as ?month)
    BIND (year(?visit) as ?year)
}
GROUP BY ?business ?year ?month ?day
ORDER BY DESC(COUNT(?visit))
LIMIT 5
```

| business.value                                    | year.value | month.value | day.value | numberOfVisits.value |
|---------------------------------------------------|-----------:|------------:|----------:|---------------------:|
| https://purl.archive.org/purl/yelp/yelp_entiti... |       2016 |           6 |        25 |                  457 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |       2015 |           8 |        30 |                  285 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |       2016 |           8 |        28 |                  268 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |       2016 |           8 |        28 |                  263 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |       2017 |           7 |        29 |                  251 |

**Correct Answer**
```python
checkins["Day"] = checkins["date"].apply(lambda x: x.split("-")[2][:2])
checkins["Month"] = checkins["date"].apply(lambda x: x.split("-")[1])
checkins["Year"] = checkins["date"].apply(lambda x: x.split("-")[0])

checkins.value_counts(subset=["business_id", "Day", "Month", "Year"], sort=True, ascending=False).head(5)

>>
business_id             Day  Month  Year    count
CySqUcNz8oPiQTu4EXTnig  25   06     2016    465
g50ImmCX3WY3koEDIzoKxg  30   08     2015    287
qfWWx0dVo1UuAhRfh03Dyw  28   08     2016    270
g50ImmCX3WY3koEDIzoKxg  28   08     2016    264
FBBeJO50xZiNIo3oFhAFRA  29   07     2017    254
dtype: int64
```
NOTE: The difference in the counts here are because identical triples are not allowed in RDF. That means if a business has two check-in times at identical times only one triple will be included in the graph.

## CQ 9: Which is the most visisted business overall?
**SPARQL Query**
```sparql
SELECT ?business COUNT(?visit) AS ?count_visits
WHERE {
    ?business schema:checkinTime ?visit .
}
GROUP BY ?business 
ORDER BY DESC(COUNT(?visit))
LIMIT 10
```

|                                    business.value | count_visits.value |
|--------------------------------------------------:|-------------------:|
| https://purl.archive.org/purl/yelp/yelp_entiti... |              52129 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              40092 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              37553 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              37511 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              31163 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              29599 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              28917 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              21527 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              21478 |
| https://purl.archive.org/purl/yelp/yelp_entiti... |              18604 |

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

NOTE: The same applies here as for the previous CQ.

## CQ 10: How many people have written a review on Yelp?
**SPARQL Query**
```sparql
SELECT COUNT(DISTINCT(?user)) AS ?countUsers
WHERE {
    ?review schema:author ?user .
}
```
|  **?countUsers**  |
|-------------------|
|     1,987,929     |

**Correct Answer**
```python
reviews.drop_duplicates(subset=['user_id']).shape[0]

>> 1987929
```

## CQ 11: How many users have 10 friends?
**SPARQL Query**
```sparql
SELECT COUNT(*) as ?usersWith10Friends
WHERE {
    SELECT ?user COUNT(?friend) AS ?countUsers
    WHERE {
        ?user rdfs:Class schema:Person .
        ?user schema:knows ?friend .
    }
    GROUP BY ?user
    HAVING (COUNT(?friend) = 10)
}
```
|  **?usersWith10Friends**  |
|---------------------------|
|           13,579          |

**Correct Answer**
```python
users["amountFriends"] = users["friends"].apply(lambda x: len(x.split(",")))
users[users["amountFriends"] == 10].shape[0]

>> 13579
```

## CQ 12: How many friends does a user have on average?
**SPARQL Query**
```sparql
SELECT (xsd:double(?countFriends) / xsd:double(?countUser) AS ?averageFriends)
WHERE {
    {SELECT (COUNT(?user) AS ?countUser)
    WHERE {
        ?user rdfs:Class schema:Person .
        }}
    {SELECT (COUNT(?friend) AS ?countFriends)
    WHERE {
        ?user schema:knows ?friend .
        }}
}
```

| averageFriends.value |
| :------------------- |
| 52.9331              |

**Correct Answer**
```python
# Import the necessary libraries
import json
import numpy as np
# Open the file containing the user data
with open(file="/home/ubuntu/OneDrive/DVML-P7/Data/yelp_academic_dataset_user.json", mode="r") as file:
    # Initialize an empty list to store the number of friends for each user
    number_of_friends = []
    # Iterate over each line in the file
    for line in file:
        # Parse the data from the line as a JSON object
        data = json.loads(line)
        # Extract the list of friends for the current user
        friend_ids = data['friends']
        # If the user has friends, append the number of friends to the list
        if friend_ids != 'None':
            number_of_friends.append(len(friend_ids.split(', ')))
        # If the user does not have friends, append 0 to the list
        else:
            number_of_friends.append(0)
# Calculate the mean number of friends
np.mean(number_of_friends)

>> 52.93306142119033
```

## CQ 13: How many users have authored 10 reviews?
**SPARQL Query**
```sparql
SELECT COUNT(DISTINCT(?user)) AS ?countUsers
WHERE {
    SELECT ?user COUNT(?review) as ?numberOfReviews
    WHERE {
        ?user rdfs:Class schema:Person .
        ?review schema:author ?user .
    }
    GROUP BY ?user
    HAVING (COUNT(?review) = 10)
}
```

|  **?countUsers**   |
|--------------------|
|       14,119       |

**Correct Answer**
```python
reviews.groupby("user_id").size().reset_index(name="count").query("count == 10").shape[0]

>> 14119
```

## CQ 14: How many reviews did users make in May 2018?
**SPARQL Query**
```sparql
SELECT ?year ?month COUNT(?review) as ?countReviews
WHERE {
    ?review rdfs:Class schema:UserReview .
    ?review schema:dateCreated ?date .
    BIND (month(?date) as ?month) .
    BIND (year(?date) as ?year) .
    VALUES ?year {2018}
    VALUES ?month {5}
}
GROUP BY ?year ?month
```

| year.value | month.value | countReviews.value |
|-----------:|------------:|-------------------:|
|       2018 |           5 |              79434 |

**Correct Answer**
```python
from datetime import datetime
reviewers = 0
# Open JSON file for reading
with open(file=get_path("yelp_academic_dataset_review.json"), mode="r") as file:
    # Iterate through each line in the file
    for line in file:
        # Parse line as a dictionary
        data = json.loads(line)
        review_date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')
        if review_date.year == 2018 and review_date.month == 5:
            reviewers += 1
reviewers

>> 79,434
```

## CQ 15: How many parking options can a business provide?
**SPARQL Query**
```sparql
SELECT DISTINCT ?p
WHERE {
    ?s rdfs:Class schema:ParkingFacility.
    ?s ?p ?parking .
    MINUS {
        ?s rdfs:Class ?parking.
        }
}
```

|     | p.value                                                  |
| --: | :------------------------------------------------------- |
|   0 | https://purl.archive.org/purl/yelp/ontology#hasgarage    |
|   1 | https://purl.archive.org/purl/yelp/ontology#haslot       |
|   2 | https://purl.archive.org/purl/yelp/ontology#hasstreet    |
|   3 | https://purl.archive.org/purl/yelp/ontology#hasvalet     |
|   4 | https://purl.archive.org/purl/yelp/ontology#hasvalidated |

**Correct Answer**
```python
# Initialize empty list to store business parking options
BusinessParking = []
# Open JSON file for reading
with open(file=get_path("yelp_academic_dataset_business.json"), mode="r") as file:
    # Iterate through each line in the file
    for line in file:
        # Parse line as a dictionary
        data = json.loads(line)
        try:
            # Extract 'BusinessParking' value from dictionary
            _dict = data['attributes']['BusinessParking']
            # If 'BusinessParking' value is a string, modify it and parse as a dictionary
            if isinstance(_dict, str):
                _dict = _dict.replace("'", '"').replace("None", "null").replace('u"', '"').replace("True", "true").replace("False", "false") 
                _dict = json.loads(_dict)
            # Store modified dictionary in 'parkingopt' variable
            parkingopt = _dict
            # Append 'parkingopt' to 'BusinessParking' list
            BusinessParking.append(parkingopt)
        # If any errors are raised (e.g. missing keys), do nothing and continue to next iteration
        except:
            pass
# Initialize empty list to store parking option names
num_parkingopt = []
# Iterate through each business parking option dictionary
for parkings in BusinessParking:
    # If the dictionary is not empty (i.e. is not 'None')
    if parkings is not None:
        # Iterate through each key (i.e. parking option name) in the dictionary
        for parkingopt in parkings.keys():
            # Append the parking option name to the list
            num_parkingopt.append(parkingopt)
# Convert list to a set to remove duplicate values, and assign to 'set(num_parkingopt)'
set(num_parkingopt)

>> {'garage', 'lot', 'street', 'valet', 'validated'}
```

## CQ 16: How many businesses has karaoke music?
**SPARQL Query**
```sparql
SELECT COUNT(DISTINCT ?business) AS ?businessesWithKaraoke
WHERE {
    ?business yelpont:hasMusic ?blank .
    ?blank yelpont:haskaraoke 1 .
}
```

| businessesWithKaraoke.value |
| :-------------------------- |
| 75                          |

**Correct Answer**
```python
from collections import Counter
# Initialize a list to store the karaoke values found in the input file
karaoke_values = []

# Open the input file for reading
with open(file=get_path("yelp_academic_dataset_business.json"), mode="r") as file:
    # Iterate over each line in the file
    for line in file:
        # Load the JSON data from the line
        data = json.loads(line)
        try:
            # Extract the Music dictionary from the data
            music_dict = data['attributes']['Music']
            # Check if the Music value is a string
            if isinstance(music_dict, str):
                # Replace various substrings in the Music string with their JSON equivalent
                music_dict = music_dict.replace("'", '"').replace("None", "null").replace('u"', '"').replace("True", "true").replace("False", "false") 
                # Parse the Music string as JSON
                music_dict = json.loads(music_dict)
            # Extract the karaoke value from the Music dictionary
            karaoke = music_dict['karaoke']
            # Add the karaoke value to the list
            karaoke_values.append(karaoke)
        except:
            # Catch any exceptions that may be raised and do nothing
            pass
# Count the number of True values in the list
dict(Counter(karaoke_values))[True]

>> 75
```
