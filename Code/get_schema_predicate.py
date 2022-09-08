from rdflib import Namespace, URIRef, Literal


def return_predicate(predicate):
    match predicate:
        case "name":
            return "name"
        case "address":
            return "address"
        case "city":
            return "location"
        case "state":
            return "location"
        case "postal_code":
            return "postalCode"
        case "latitude":
            return "latitude"
        case "longitude":
            return "longitude"
        case "stars":
            return "starRating"
        case "review_count":
            return "reviewCount"
        case "is_open":
            return "publicAccess"
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
