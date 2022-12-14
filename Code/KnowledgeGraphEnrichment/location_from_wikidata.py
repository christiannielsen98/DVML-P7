import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import os
import pandas as pd
from rdflib import Namespace, Graph, URIRef, Literal, XSD
from rdflib.namespace import RDFS
import gzip
from Code.UtilityFunctions.wikidata_functions import get_city_of_location_with_long_lat, get_county_of_location_with_long_lat, wikidata_query, city_population_query, county_query, state_query, country_query
from Code.UtilityFunctions.get_data_path import get_path
from discord_webhook import DiscordWebhook
import datetime


def create_location_mappings_csv():
    """
    This function creates a csv file with the location mappings from yelp to wikidata
    """
    # Load the business data from yelp
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

    # Create a dataframe of all the unique, rounded to 2nd decimal, coordinates
    coordinates = (biz["longitude"].apply(round, args=(2,)).astype(str) + "," + biz["latitude"].apply(round, args=(2,)).astype(str)).unique()
    coordinates_df = pd.DataFrame(coordinates, columns=['coordinates'])

    # Query the nearest city for each coordinate and add it to a dataframe
    location_mappings_df = pd.DataFrame(columns=['coordinates', 'city_qid', 'cityLabel'])
    for i in coordinates_df.itertuples():
        location_mappings_df = pd.concat([location_mappings_df,pd.DataFrame([i.coordinates] + list(get_city_of_location_with_long_lat(i.coordinates)), index=location_mappings_df.columns).T], ignore_index=True)
        print(i.coordinates, i.Index, len(coordinates_df))
    
    # Save the dataframe to a csv
    location_mappings_df.to_csv(path_or_buf=get_path('location_mappings_with_boroughrAndCencus.csv'),index=False)


def expand_location_mappings(location_mappings: pd.DataFrame):
    """
    This function expands the location mappings dataframe with the county, state, and country of each city
    :param location_mappings:
    :return:
    """
    # Create a list of all the US states and Canada provinces
    list_of_us_states = list(wikidata_query(sparql_query="SELECT ?state WHERE{?state wdt:P31 wd:Q35657.}")['state.value'].apply(lambda x: x[31:]))
    list_of_canada_provinces = list(wikidata_query(sparql_query="SELECT ?province WHERE{?province wdt:P31 wd:Q11828004.}")['province.value'].apply(lambda x: x[31:]))
    list_canada_provinces_us_states = list_of_us_states + list_of_canada_provinces
    
    # Add the population of the city
    location_mappings['population'] = location_mappings.apply(lambda x: city_population_query(x.city_qid), axis=1)
    
    # Add the county of the city if it exists, otherwise query the county of the location with the long lat (because the city might not have a county in wikidata)
    location_mappings[['county_qid', 'countyLabel']] = location_mappings.apply(lambda x: pd.Series(county_query(x.city_qid)) if pd.Series(county_query(x.city_qid))[0] not in list_canada_provinces_us_states else pd.Series(get_county_of_location_with_long_lat(x.coordinates)), axis=1)
    
    # Add the state of the county if it exists, otherwise query the state of the city (because the city might not have a county)
    location_mappings[['state_qid', 'stateLabel']] = location_mappings.apply(lambda x: pd.Series(state_query(x.county_qid)) if x.county_qid is not None else pd.Series(state_query(x.city_qid)), axis=1)
    
    # Add the country of the state or province
    location_mappings[['country_qid', 'countryLabel']] = location_mappings.apply(lambda x: pd.Series(country_query(x.state_qid)), axis=1)
    return location_mappings


def yelp_wiki_location_mappings(location_mappings):
    """
    This function merge the mappings to the original Yelp businesses.
    :return:
    """
    
    # Load the business data from yelp
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

    # Add "long_lat_round" column to the dataframe for mapping to wikidata
    biz['long_lat_round'] = (biz["longitude"].apply(round, args=(2,)).astype(str) + "," + biz["latitude"].apply(round, args=(2,)).astype(str))
    # Select only the columns we need
    biz2 = biz[['business_id','long_lat_round', 'address', 'city', 'state']]
    # Merge the business data with the location data on the "long_lat_round" column
    biz_location_mapping_merge = biz2.merge(location_mappings, left_on='long_lat_round', right_on='coordinates', how='left')
    return biz_location_mapping_merge


def create_wikidata_location_triples():
    """
    This function creates the triples for the location of the businesses in wikidata
    :return:
    """
    biz_location_mapping_merge = yelp_wiki_location_mappings()
    ## If file exists, delete it ##
    remove_files="/home/ubuntu/vol1/virtuoso/import/wikidata_location_mappings.nt.gz"
    if os.path.isfile(remove_files):
        os.remove(remove_files)
    else:    ## Show an error ##
        print("Error: %s file not found" % remove_files)

    schema = Namespace("https://schema.org/")
    wiki = Namespace("https://www.wikidata.org/entity/")
    yelpont = Namespace("https://purl.archive.org/purl/yelp/ontology#")
    location_predicate = wiki + "P131"  # P131 = located in the administrative territorial entity
    population_predicate = wiki + "P1082"  # P1082 = population
    instance_of_predicate = wiki + "P31"  # P31 = instance of
    city_object = wiki + "Q515"  # Q515 = city
    county_object = wiki + "Q28575"  # Q28575 = county
    state_object = wiki + "Q35657"  # Q35657 = U.S. state
    province_object = wiki + "Q11828004"  # Q11828004 = province of Canada
    country_object = wiki + "Q6256"  # Q6256 = country

    list_of_us_states = list(wikidata_query(sparql_query="SELECT ?state WHERE{?state wdt:P31 wd:Q35657.}")['state.value'].apply(lambda x: x[31:]))
    list_of_canada_provinces = list(wikidata_query(sparql_query="SELECT ?province WHERE{?province wdt:P31 wd:Q11828004.}")['province.value'].apply(lambda x: x[31:]))

    triple_file = gzip.open(filename="/home/ubuntu/vol1/virtuoso/import/wikidata_location_mappings.nt.gz", mode="at", encoding="utf-8")

    G = Graph()
    for i in biz_location_mapping_merge.itertuples():
        if not pd.isna(i.city_qid):
            G.add((URIRef(yelpont[i.business_id]), URIRef(schema['location']), URIRef(wiki[i.city_qid])))
            G.add((URIRef(wiki[i.city_qid]), URIRef(RDFS.label), Literal(i.cityLabel, datatype=XSD.string)))
            G.add((URIRef(wiki[i.city_qid]), URIRef(instance_of_predicate), URIRef(city_object)))
            if not pd.isna(i.population):
                G.add((URIRef(wiki[i.city_qid]), URIRef(population_predicate), Literal(i.population, datatype=XSD.integer)))
        if not pd.isna(i.county_qid):
            G.add((URIRef(wiki[i.city_qid]), URIRef(location_predicate), URIRef(wiki[i.county_qid])))
            G.add((URIRef(wiki[i.county_qid]), URIRef(RDFS.label), Literal(i.countyLabel, datatype=XSD.string)))
            G.add((URIRef(wiki[i.county_qid]), URIRef(instance_of_predicate), URIRef(county_object)))
        if not pd.isna(i.state_qid):
            G.add((URIRef(wiki[i.county_qid]), URIRef(location_predicate), URIRef(wiki[i.state_qid])))
            G.add((URIRef(wiki[i.state_qid]), URIRef(RDFS.label), Literal(i.stateLabel, datatype=XSD.string)))
            if i.state_qid in list_of_us_states:
                G.add((URIRef(wiki[i.state_qid]), URIRef(instance_of_predicate), URIRef(state_object)))
            elif i.state_qid in list_of_canada_provinces:
                G.add((URIRef(wiki[i.state_qid]), URIRef(instance_of_predicate), URIRef(province_object)))
        if not pd.isna(i.country_qid):
            G.add((URIRef(wiki[i.state_qid]), URIRef(location_predicate), URIRef(wiki[i.country_qid])))
            G.add((URIRef(wiki[i.country_qid]), URIRef(RDFS.label), Literal(i.countryLabel, datatype=XSD.string)))
            G.add((URIRef(wiki[i.country_qid]), URIRef(instance_of_predicate), URIRef(country_object)))
        
    triple_file.write(G.serialize(format="nt"))
    triple_file.close()


if __name__ == "__main__":
    begin_time = datetime.datetime.now()
    try:
        create_location_mappings_csv()
        location_mappings = pd.read_csv(get_path('location_mappings_with_boroughrAndCencus.csv'))
        expand_location_mappings(location_mappings).to_csv(path_or_buf=get_path('location_mappings_with_boroughrAndCencus_expanded.csv'), index=False)
        os.system("onedrive --synchronize --single-directory DVML-P7") if "Linux" in os.uname() else None
        # location_mappings = pd.read_csv(get_path('location_mappings_expanded.csv'))
        # create_wikidata_location_triples(location_mappings)
        
        message = f"Location_from_wikidata execution is done - Time in hh:mm:ss - {datetime.datetime.now() - begin_time} \nbegan {begin_time} \nended {datetime.datetime.now()}"
    except Exception as e:
        message = "Location_from_wikidata broke with this error: " + str(e)
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1051908340772515860/2jd9XbteomjiPwZCuoiZ7WN4LGe-xJzUPC8P1xPBBpbyECu00PSIIfs8tARmkI78t88v', content=message)
    response = webhook.execute()
    print(message)