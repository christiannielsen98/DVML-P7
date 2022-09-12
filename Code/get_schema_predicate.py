from rdflib import Namespace, URIRef, Literal, XSD


def return_predicate(predicate):
    match predicate:
        case "name":
            return "name", XSD.string
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
