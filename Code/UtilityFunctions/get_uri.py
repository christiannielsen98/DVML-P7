from rdflib import Namespace
example = Namespace("https://example.org/")

def get_uri(filename):
    match filename:
        case 'yelp_academic_dataset_business.json':
            return example + 'business_id/'
        case 'yelp_academic_dataset_user.json':
            return example + 'user_id/'
        case 'yelp_academic_dataset_review.json':
            return example + 'review_id/'
        case 'yelp_academic_dataset_tip.json':
            return example + 'tip_id/'
        case 'yelp_academic_dataset_checkin.json':
            return example + 'business_id/'