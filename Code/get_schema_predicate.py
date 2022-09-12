from rdflib import Namespace, URIRef, Literal, XSD

schema = Namespace("https://schema.org/")
example = Namespace("https://example.org/")


def return_predicate(predicate):
    match predicate:
        case "name":
            return schema + "name", XSD.string
        case "address":
            return "address", XSD.string
        case "city":
            return "location", XSD.string
        case "state":
            return "location", XSD.string
        case "postal_code":
            return "postalCode", XSD.string
        case "latitude":
            return "latitude", XSD.float
        case "longitude":
            return "longitude", XSD.float
        case "stars":
            return "starRating", XSD.integer
        case "review_count":
            return "reviewCount", XSD.integer
        case "is_open":
            return "publicAccess", XSD.string
        case "attributes":  # SPECIAL CASE
            return None
        case "categories":  # SPECIAL CASE
            return None
        case "hours":  # SPECIAL CASE
            return "openingHours"
        # ??? (T/F)
        case "ByAppointmentOnly":
            return None
        case "BusinessAcceptsCreditCards":
            return None
        case "BikeParking":
            return None
        case "RestaurantsPriceRange2":
            return "priceRange"
        case "CoatCheck":
            return None
        case "RestaurantsTakeOut":
            return None
        case "RestaurantsDelivery":
            return None
        case "Caters":
            return None
        case "WiFi":
            return None
        case "BusinessParking":
            return None
        case "WheelchairAccessible":
            return None
        case "HappyHour":
            return None
        case "OutdoorSeating":
            return None
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
            return "dietFeatures"
        case _:
            return "Error :'("


if __name__ == "__main__":
    print(return_predicate("Yo"))
