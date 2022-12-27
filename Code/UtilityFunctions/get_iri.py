from rdflib import Namespace

yelpent = Namespace("https://purl.archive.org/purl/yelp/yelp_entities#")

def get_iri(filename):
    match filename:
        case 'yelp_academic_dataset_business.json':
            return yelpent + 'business_id/'
        case 'yelp_academic_dataset_user.json':
            return yelpent + 'user_id/'
        case 'yelp_academic_dataset_review.json':
            return yelpent + 'review_id/'
        case 'yelp_academic_dataset_tip.json':
            return yelpent + 'tip_id/'
        case 'yelp_academic_dataset_checkin.json':
            return yelpent + 'business_id/'
