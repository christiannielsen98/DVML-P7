import sys
sys.path.append(sys.path[0][:sys.path[0].find('DVML-P7') + len('DVML-P7')])
import pandas as pd
from Code.UtilityFunctions.wikidata_functions import get_name_of_location_with_long_lat
from Code.UtilityFunctions.get_data_path import get_path
from discord_webhook import DiscordWebhook
import datetime
begin_time = datetime.datetime.now()

biz = pd.read_json(get_path("yelp_academic_dataset_business.json"), lines=True)

coordinates = (biz["longitude"].apply(round, args=(2,)).astype(str) + "," + biz["latitude"].apply(round, args=(2,)).astype(str)).unique()
coordinates_df = pd.DataFrame(coordinates, columns=['coordinates'])
location_mappings_df = pd.DataFrame(coordinates_df['coordinates'].apply(lambda x: [x] + list(get_name_of_location_with_long_lat(x))).tolist(), columns=['coordinates','city', 'cityLabel', 'cityPopulation', 'county', 'countyLabel', 'state', 'stateLabel', 'country', 'countryLabel'])
# ["1,2", Q123, "New York", Q456, "New York county", Q789, "New York State", Q101, "United States"]

if __name__ == "__main__":    
    location_mappings_df.to_csv(path_or_buf='/home/ubuntu/OneDrive/DVML-P7/Data/location_mappings.csv',index=False)
    
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/918876596763525150/d1aGYekdsL64QP0Dbx4zuaOrs_opUpFuTYkj1sHjYBJ8oUXOrruXhshP_cIFSq5phW-e', content=f'Done in hh:mm:ss {datetime.datetime.now() - begin_time}').execute()