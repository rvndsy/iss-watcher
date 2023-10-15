import logging
import logging.config
import requests
import json
import sys
import time
import yaml

from datetime import datetime
from configparser import ConfigParser

# Check if internet connection exists on device
def check_internet_connection():
    r = None
    while True:
        try:
            r = requests.get('https://www.google.com/').status_code
            break
        except:
            logger.debug(f"https://www.google.com/ - status code: {r}")
            logger.info("No internet connection!")
            time.sleep(5)
            pass

# Prepares and requests URL to get visual passes from n2yo
def get_n2yo_response(N2YO_API_URL, NORAD_ID, LAT, LON, ALT, DAYS, VISIBILITY, N2YO_API_KEY):
    url = f"{N2YO_API_URL}visualpasses/{NORAD_ID}/{LAT}/{LON}/{ALT}/{DAYS}/{VISIBILITY}&apiKey={N2YO_API_KEY}"
    logger.info(f"N2YO get_request url: {url}")
    response = requests.get(url)
    logger.debug(f"get_n2yo_response() got response {response}")
    return response

def get_osm_search_response(place_name):
    url = f"{OSM_API_URL}search.php?q={place_name}&format={OSM_JSON_VER}"
    logger.info(f"OSM get_request url: {url}")
    response = requests.get(url)
    logger.debug(f"get_osm_search_response() got response {response}")
    return response

# Check if URL response returned without error and return the json of response
def check_n2yo_response(response):
    if response.status_code != 200:
        logger.info(f"Error code {response.status_code} from N2YO API URL")
        sys.exit(1)
    logger.debug(f"check_n2yo_response() retrieved json of length: {len(response.json())}")
    return response.json()

def check_osm_response(response):
    if response.status_code != 200:
        logger.info(f"Error code {response.status_code} from OSM API URL")
        sys.exit(1)
    logger.debug(f"check_osm_response() retrieved json of length: {len(response.json())}")
    return response.json()

def get_osm_search_coords(response_json):
    display_name = None
    lat = None
    lon = None
    if len(response_json) > 0:
        data = response_json[0]
        lat_str = data.get('lat', 'null')
        lon_str = data.get('lon', 'null')
        # Convert the lat & lon strings to floats
        try:
            lat = float(lat_str)
        except ValueError:
            logger.debug("get_osm_search_coords() failed to convert lat to float, overwriting value as None")
            lat = None
        try:
            lon = float(lon_str)
        except ValueError:
            logger.debug("get_osm_search_coords() failed to convert lon to float, overwriting value as None")
            lon = None
        display_name = data.get('display_name', 'null')
        # In case of no longitude or no lattitude values provided. Default config values are used.
        if lat == None or lon == None:
            logger.info("No latitude or longitude value gotten. Defaulting to 'Valmiera' coordinates")
            lat=LAT
            lon=LON
            display_name="Valmiera (defaulted)"
        return (lat, lon, display_name)
    else:
        logger.info("OSM response is empty")
    
# Print out a list of satellite passes in a human readable format
def print_passes(response_json, full_place_name):
    # Check for 0 visual passes at location
    if 'info' in response_json and response_json['info']['passescount'] == 0:
        print(f"No visual passes found at location {full_place_name} for now!")
        return
    # Print all visible passes
    print(f"ISS will be visible at \"{full_place_name}\" at these times:")
    for event in response_json['passes']:
        date_and_time = datetime.fromtimestamp(event['startUTC']).strftime('%d.%m.%Y %H:%M:%S')
        print(date_and_time, "for", event['endUTC']-event['startUTC'], "seconds")

if __name__ == "__main__":

    # Loading logging configuration
    with open('./log_main.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
    logging.config.dictConfig(config)
    logger = logging.getLogger('root')
    logger.info("ISS flyover times at your location of choice!")

    # Reading required values from config file
    logger.info("Loading configuration from file")
    try:
        config = ConfigParser()
        config.read('config.ini')
        
        N2YO_API_KEY = config.get('n2yo', 'api_key')
        N2YO_API_URL = config.get('n2yo', 'api_url')

        OSM_API_URL = config.get('osm', 'api_url')
        OSM_JSON_VER = config.get('osm', 'api_json_ver')
        # Norad id for satellite. 25544 = ISS
        NORAD_ID = config.get('user', 'norad_id')
        # Observer data: decimal degrees - LATitude, LONgitude; meters - elevation. Default is ViA university.
        LAT = config.get('user', 'latitude')
        LON = config.get('user', 'longitude')
        ALT = config.get('user', 'altitude')
        # In seconds - length of time while satellite is visible in the sky
        VISIBILITY = config.get('user', 'visibility')
        # In days - how far into the future to predict ISS passovers, MAX = 10.
        DAYS = config.get('user', 'prediction_days')
    except:
        logger.info('Exception error in loading config')
    logger.info('DONE')

    check_internet_connection()
    ## Get visual passes for ISS. Print out received information.
    # response = get_response()
    # print(response, "\n")

    place_name = "Valmiera"
    
    if place_name == "":
        logger.info(f"No place name provided for OSM. Using defaults.")
        place_name = "The default coordinates"
        coords = (LAT, LON, place_name)
    else:
        logger.info(f"Getting data from OSM for {place_name}")
        osm_search_response = get_osm_search_response(place_name)
        osm_response_json = check_osm_response(osm_search_response)
        coords = get_osm_search_coords(osm_response_json)
        logger.info("DONE")

    logger.info(f"Getting data from N2YO for {place_name}")
    n2yo_response = get_n2yo_response(N2YO_API_URL, NORAD_ID, coords[0], coords[1], ALT, DAYS, VISIBILITY, N2YO_API_KEY)
    n2yo_response_json = check_n2yo_response(n2yo_response)
    logger.info("DONE")

    print("\n\nVisual Passes Response:")
    print_passes(n2yo_response_json, coords[2])
    # print(coords, place_name)
