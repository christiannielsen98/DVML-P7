from time import sleep

import pandas as pd
from geopy.geocoders import Nominatim

from Code.UtilityFunctions.get_data_path import get_path


def update_business_locations(df: pd.DataFrame,
                              coordinate_rounding: int=2,
                              min_delay_seconds: int=2,
                              zoom_level: int=14,
                              report_missing: bool=False) -> pd.DataFrame:
    """
    Take a pd.dataframe with two columns ["latitude", "longitude"] and update the locations to the neighbourhood level
    using the geopy library to reverse search this coordinate set, rounded to the coordinate_rounding.

    Args:
        df (pd.DataFrame): A dataframe with two columns ["latitude", "longitude"]
        coordinate_rounding (int, optional): The number of decimal places to round the coordinates to. Defaults to 2.
        min_delay_seconds (int, optional): The minimum delay between requests to the geopy API. Defaults to 2.
        zoom_level (int, optional): The zoom level to use when reverse searching the coordinates. Defaults to 14.
        report_missing (bool, optional): Whether to report missing locations. Defaults to False.

    Returns:
        pd.DataFrame: The original dataframe with additional columns ["neighbourhood", "city", "county", "state", "country"]
    """
    
    # Preprocess the DataFrame
    df.drop(['city', 'state'], inplace=True, axis=1)
    round_lat = df["latitude"].apply(round, args=(coordinate_rounding,)).astype(str)
    round_lon = df["longitude"].apply(round, args=(coordinate_rounding,)).astype(str)
    df["coordinate_set"] = round_lat + ',' + round_lon
    
    # Create list of unique rounded coordinates
    unique_locations = list(df["coordinate_set"].unique())
    
    # Create geolocator using the Nominatim API
    geolocator = Nominatim(user_agent="YelpLocationMatching")

    # Create a dictionary with location as key and address as value
    location_dict = {}
    for location in unique_locations:
        try:
            location_dict[location] = geolocator.reverse(location, zoom=zoom_level).raw['address']
        except:
            location_dict[location] = None
        sleep(min_delay_seconds)  # Sleep to avoid API timeout
    
    desired_address_levels = ["neighbourhood", "city", "county", "state", "country"]
    address_dict = {}
    
    # Extract only desired address levels from location_dict into address_dict
    for location, address in location_dict.items():
        if address is not None:
            address_dict[location] = {level: address[level] for level in desired_address_levels if level in address}
    
    if report_missing:
        # Count entries in address_dict that have no key in desired_address_levels
        missing_count_dict = {}
        for location, address in address_dict:
            if set(list(address.keys()) != set(desired_address_levels)):
                for missing_location in set(desired_address_levels).difference(set(list(address.keys()))):
                    missing_count_dict[missing_location] += 1
        print(missing_count_dict)
    
    # Create address DataFrame from the address_dict
    address_df = pd.DataFrame.from_dict(address_dict, orient="index")

    # Merge the two DataFrames on the coordinate_set column of businesses and the index of address_df
    updated_businesses = df.merge(address_df, how="left", left_on="coordinate_set", right_index=True)

    # Remove the rounded coordinate set column
    updated_businesses.drop("coordinate_set", inplace=True, axis=1)
    
    return updated_businesses