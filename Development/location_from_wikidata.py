from operator import index
import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import pandas as pd
from Code.UtilityFunctions.wikidata_functions import get_name_of_location_with_long_lat, wikidata_query
from Code.UtilityFunctions.get_data_path import get_path
from discord_webhook import DiscordWebhook
import datetime
begin_time = datetime.datetime.now()

def create_location_mappings_csv():
    biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

    coordinates = (biz["longitude"].apply(round, args=(2,)).astype(str) + "," + biz["latitude"].apply(round, args=(2,)).astype(str)).unique()
    coordinates_df = pd.DataFrame(coordinates, columns=['coordinates'])

    location_mappings_df = pd.DataFrame(columns=['coordinates','city', 'cityLabel'])
    for i in coordinates_df.itertuples():
        location_mappings_df = pd.concat([location_mappings_df,pd.DataFrame([i.coordinates] + list(get_name_of_location_with_long_lat(i.coordinates)), index=location_mappings_df.columns).T], ignore_index=True)
        print(i.coordinates, i.Index, len(coordinates_df))
    
    location_mappings_df.to_csv(path_or_buf='/home/ubuntu/OneDrive/DVML-P7/Data/location_mappings.csv',index=False)

def county_query(city_qid: str):
    try:
        county_query = f"""SELECT ?county ?countyLabel
        WHERE
        {{
        wd:{city_qid} wdt:P131 ?county .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}}}"""
        a = wikidata_query(county_query)
        return (a['county.value'][0][31:], a['countyLabel.value'][0])
    except:
        return (None, None)

def state_query(county_qid: str):
    try:
        state_query = f"""SELECT ?state ?stateLabel
        WHERE
        {{
        wd:{county_qid} wdt:P131 ?state .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}}}"""
        a = wikidata_query(state_query)
        return (a['state.value'][0][31:], a['stateLabel.value'][0])
    except:
        return (None, None)

def country_query(state_qid: str):
    try:
        country_query = f"""SELECT ?country ?countryLabel
        WHERE
        {{
        wd:{state_qid} wdt:P17 ?country .
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }}}}"""
        a = wikidata_query(country_query)
        return (a['country.value'][0][31:], a['countryLabel.value'][0])
    except:
        return (None, None)

def expand_location_mappings(location_mappings: pd.DataFrame):
    location_mappings[['county', 'countyLabel']] = location_mappings.apply(lambda x: pd.Series(county_query(x.city)), axis=1)
    location_mappings[['state', 'stateLabel']] = location_mappings.apply(lambda x: pd.Series(state_query(x.county)), axis=1)
    location_mappings[['country', 'countryLabel']] = location_mappings.apply(lambda x: pd.Series(country_query(x.state)), axis=1)
    return location_mappings

if __name__ == "__main__":    
    create_location_mappings_csv()
    # location_mappings = pd.read_csv(get_path('location_mappings.csv'))
    # expand_location_mappings(location_mappings).to_csv(path_or_buf=get_path('location_mappings_expanded.csv'), index=False)
    
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/918876596763525150/d1aGYekdsL64QP0Dbx4zuaOrs_opUpFuTYkj1sHjYBJ8oUXOrruXhshP_cIFSq5phW-e', content=f'Location_from_wikidata done in hh:mm:ss {datetime.datetime.now() - begin_time}').execute()