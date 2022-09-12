from rdflib import Namespace, URIRef, Literal, XSD

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")


def return_predicate(predicate):
    match predicate:
        case "name":
            return schema + "name", XSD.string
        case "address":
            return schema + "address", XSD.string
        case "city":
            return schema + "location", XSD.string
        case "state":
            return schema + "location", XSD.string
        case "postal_code":
            return schema + "postalCode", XSD.string  # integer?
        case "latitude":
            return schema + "latitude", XSD.float
        case "longitude":
            return schema + "longitude", XSD.float
        case "stars":
            return schema + "starRating", XSD.integer
        case "review_count":
            return schema + "reviewCount", XSD.integer
        case "is_open":
            return schema + "publicAccess", XSD.string
        case "attributes":  # SPECIAL CASE
            return None
        case "categories":  # SPECIAL CASE
            return None
        case "hours":  # SPECIAL CASE
            return "openingHours"
        # ??? (T/F)
        case "ByAppointmentOnly":
            return example + "byAppointmentOnly", XSD.boolean
            # return schema + "conditionsOfAccess", XSD.string  obj = "by appointment only"
        case "BusinessAcceptsCreditCards":
            return example + "businessAcceptsCreditCards", XSD.boolean
            # return schema + "paymentAccepted", XSD.string     obj = "credit card"
        case "BikeParking":
            return example + "bikeParking", XSD.boolean
        case "RestaurantsPriceRange2":
            return schema + "priceRange", XSD.string
        case "CoatCheck":
            return example + "coatCheck", XSD.boolean
        case "RestaurantsTakeOut":
            return example + "restaurantsTakeOut", XSD.boolean
        case "RestaurantsDelivery":
            return example + "restaurantsDelivery", XSD.boolean
        case "Caters":
            return example + "caters", XSD.boolean
        case "WiFi":
            return example + "hasWiFi", XSD.boolean
        case "BusinessParking":
            # Dictionary
            return None
        case "WheelchairAccessible":
            return example + "wheelcharAccessible", XSD.boolean
            # return schema + "accessibilityFeature", XSD.string
        case "HappyHour":
            return example + "happyHour", XSD.boolean
        case "OutdoorSeating":
            return example + "hasOutdoorSeating", XSD.boolean
        case "HasTV":
            return None
        case "RestaurantsReservations":
            return None
        case "DogsAllowed":
            return None
        case "Alcohol":
            return None
        case "GoodForKids":
            return None
        case "RestaurantsAttire":
            return None
        case "Ambience":
            return None
        case "RestaurantsTableService":
            return None
        case "RestaurantsGoodForGroups":
            return None
        case "DriveThru":
            return None
        case "NoiseLevel":
            return None
        case "GoodForMeal":
            return None
        case "BusinessAcceptsBitcoin":
            return None
        case "Smoking":
            return None
        case "Music":
            return None
        case "GoodForDancing":
            return None
        case "AcceptsInsurance":
            return None
        case "BestNights":
            return None
        case "BYOB":
            return None
        case "Corkage":
            return None
        case "BYOBCorkage":
            return None
        case "HairSpecializesIn":
            return None
        case "Open24Hours":
            return None
        case "RestaurantsCounterService":
            return None
        case "AgesAllowed":
            return "suggestedMinAge"
        case "DietaryRestrictions":
            return "dietFeatures"
        case _:
            return "Error :'("


if __name__ == "__main__":
    print(return_predicate("Yo"))
