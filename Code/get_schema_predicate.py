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
            return schema + "category", XSD.string
        case "hours":  # SPECIAL CASE
            return schema + "openingHours", XSD.string
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
            return example + "hasTV", XSD.boolean
        case "RestaurantsReservations":
            return example + "takesReservations", XSD.boolean
        case "DogsAllowed":
            return example + "allowsDogs", XSD.boolean
        case "Alcohol":
            return example + "servesAlcohol", XSD.boolean
        case "GoodForKids":
            return example + "kidFriendly", XSD.boolean
        case "RestaurantsAttire":
            return example + "Attire", XSD.string
        case "Ambience":
            return None #is a dict
        case "RestaurantsTableService":
            return example + "hasTableService", XSD.boolean
        case "RestaurantsGoodForGroups":
            return example + "groupFriendly", XSD.boolean
        case "DriveThru":
            return example + "hasDriveThru", XSD.boolean
        case "NoiseLevel":
            return example + "noiseLevel", XSD.string
        case "GoodForMeal":
            return None #is a dict
        case "BusinessAcceptsBitcoin":
            return example + "acceptBitcoin", XSD.boolean
        case "Smoking":
            return example + "smokingAllowed", XSD.boolean
        case "Music":
            # dict
            return None
        case "GoodForDancing":
            return example + "goodForDancing", XSD.boolean
        case "AcceptsInsurance":
            return example + "acceptsInsurance", XSD.boolean
        case "BestNights":
            # dict
            return None
        case "BYOB":
            return example + "isBringYourOwnBeverage", XSD.boolean
        case "Corkage":
            return example + "hasCorkage", XSD.boolean
        case "BYOBCorkage":
            return example + "hasBYOBCorkage", XSD.string
        case "HairSpecializesIn":
            # dict
            return None
        case "Open24Hours":
            return example + "isOpen24Hours", XSD.boolean
        case "RestaurantsCounterService":
            return example + "hasRestaurantsCounterService", XSD.boolean
        case "AgesAllowed":
            return schema + "suggestedMinAge", XSD.string
        case "DietaryRestrictions":
            # dict
            return schema + "dietFeatures", XSD.string
        case _:
            return "Error :'("


if __name__ == "__main__":
    print(return_predicate(_))
