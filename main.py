#
#   This python program (constructor) is for getting the times and dates when the International Space Station (ISS)
#   will visibly fly over your provided location. Location can be provided as a place name in the config file, or
#   as a set of coordinates. API's used are provided by - https://www.openstreetmap.org/ and https://www.n2yo.com/.
#   The DB is in MySQL (or in my case MariaDB, the SQL should be cross-compatible).
#   The objective of this program is not to be a full-fledged product. It was made for a university course to 
#   practice code testing, database migrations, logging, using config files, automatization.
# 
import logging
import logging.config
import mysql.connector
import requests
import json
import sys
import time
import yaml

from datetime import datetime
from configparser import ConfigParser
from mysql.connector import Error

# Disable logger in tests
def disable_logging_during_tests():
    logger = logging.getLogger('root')
    logging.getLogger(__name__).disabled = True

#
#   DB stuff:   The program can theoretically work without a database but it is not made for that right now. 
#               It was deemed necessary to use a database for the course, so here it is.
#

# Is used in getting the cursor and checking if database is available
def init_db():
	global connection
	connection = mysql.connector.connect(host=mysql_config_mysql_host, database=mysql_config_mysql_db, user=mysql_config_mysql_user, password=mysql_config_mysql_pass)

# Need a db cursor to do all the queries on the database
def get_cursor():
	global connection
	try:
		connection.ping(reconnect=True, attempts=1, delay=0)
		connection.commit()
	except mysql.connector.Error as err:
		logger.error("No connection to db " + str(err))
		connection = init_db()
		connection.commit()
	return connection.cursor()

# Using place_name and start_utc values to check for duplicate ISS passover entries in db.
def mysql_check_if_iss_pass_exists_in_db(pass_start_utc, place_name):
    records = []
    cursor = get_cursor()
    try:
        cursor = connection.cursor()
        result  = cursor.execute("SELECT count(*) FROM iss_pass_records WHERE `start_utc` = " + str(pass_start_utc) + " AND `place_name` = '" + str(place_name) + "'")
        logger.debug("SELECT count(*) FROM iss_pass_records WHERE `start_utc` = " + str(pass_start_utc) + " AND `place_name` = '" + str(place_name) + "'")
        records = cursor.fetchall()
        connection.commit()
    except Error as e :
        logger.error("SELECT count(*) FROM iss_pass_records WHERE `start_utc` = " + str(pass_start_utc) + " AND `place_name` = '" + str(place_name) + "'")
        logger.error('Problem checking if iss pass exists: ' + str(e))
        pass
    return records[0][0]

# Storing ISS passes into databases. Not required for core functionality.
def mysql_insert_iss_pass_into_db(place_name, place_lat, place_lon, start_utc, end_utc, duration, norad_id):
	cursor = get_cursor()
	try:
		cursor = connection.cursor()
		result  = cursor.execute( "INSERT INTO `iss_pass_records` (`place_name`, `place_lat`, `place_lon`, `start_utc`, `end_utc`, `duration`, `norad_id`) VALUES ('" + str(place_name) + "', '" + str(place_lat) + "', '" + str(place_lon) + "', '" + str(start_utc) + "', '" + str(end_utc) + "', '" + str(duration) + "', '" + str(norad_id) + "')")
		connection.commit()
	except Error as e :
		logger.error( "INSERT INTO `iss_pass_records` (`place_name`, `place_lat`, `place_lon`, `start_utc`, `end_utc`, `duration`, `norad_id`) VALUES ('" + str(place_name) + "', '" + str(place_lat) + "', '" + str(place_lon) + "', '" + str(start_utc) + "', '" + str(end_utc) + "', '" + str(duration) + "', '" + str(norad_id) + "')")
		logger.error('Problem inserting ISS pass values into DB: ' + str(e))
		pass

# Push ISS pass records into DB, while checking if they already do exist
def push_iss_pass_to_db(place_name, pass_array):
    for iss_pass in pass_array:
        if mysql_check_if_iss_pass_exists_in_db(pass_array[2], place_name) == 0:
            logger.debug("ISS pass NOT in db")
            mysql_insert_iss_pass_into_db(place_name, pass_array[0], pass_array[1], pass_array[2], pass_array[3], pass_array[4], pass_array[5])
        else:
            logger.debug("ISS pass already IN DB")

#
#   URL getting and JSON processing:
#

# Check if internet connection exists on device
def check_internet_connection():
    r = None
    while True:
        try:
            r = requests.get('https://www.google.com/').status_code
            break
        except:
            logger.info(f"https://www.google.com/ - status code: {r}")
            logger.error("No internet connection!")
            time.sleep(5)
            pass

# Returned response includes information about visible ISS flyovers in the near future (about a month?).
# The response is in JSON. The response can be 'empty' - as in no flyovers will happen in the near future.
def get_n2yo_response(N2YO_API_URL, NORAD_ID, LAT, LON, ALT, DAYS, VISIBILITY, N2YO_API_KEY):
    url = f"{N2YO_API_URL}visualpasses/{NORAD_ID}/{LAT}/{LON}/{ALT}/{DAYS}/{VISIBILITY}&apiKey={N2YO_API_KEY}"
    logger.info(f"N2YO get_request url: {url}")
    response = requests.get(url)
    logger.debug(f"get_n2yo_response() got response {response}")
    return response

# Returns coordinates of a provided place name. The response is in JSON. JSON version is indeed a requirement for this API request.
def get_osm_search_response(OSM_API_URL, place_name, OSM_JSON_VER):
    url = f"{OSM_API_URL}search.php?q={place_name}&format={OSM_JSON_VER}"
    logger.info(f"OSM get_request url: {url}")
    response = requests.get(url)
    logger.debug(f"get_osm_search_response() got response {response}")
    return response

# Checking if the N2YO API response returned without any errors.
def check_n2yo_response(response):
    if response.status_code != 200:
        logger.info(f"Error code {response.status_code} from N2YO API URL")
        sys.exit(1)
    logger.debug(f"check_n2yo_response() retrieved json of length: {len(response.json())}")
    return response.json()

# Checking if the OSM API response returned without any errors.
def check_osm_response(response):
    if response.status_code != 200:
        logger.info(f"Error code {response.status_code} from OSM API URL")
        sys.exit(1)
    logger.debug(f"check_osm_response() retrieved json of length: {len(response.json())}")
    return response.json()

# Extracting useable coordinates from OSM API response. If the response is invalid - then the program reverts to default values.
# Take note of the returned values if the response is empty.
def get_osm_search_coords(response_json):
    display_name = None
    lat = None  
    lon = None
    if len(response_json) > 0:
        data = response_json[0]
        lat_str = data.get('lat', 'null')
        lon_str = data.get('lon', 'null')
        # Convert the lat & lon strings to floats individually.
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
        # In case of no longitude or no latitude values provided. Default config values are used.
        if lat == None or lon == None:
            logger.info("No latitude or longitude value gotten. Using the default coordinates")
            lat=LAT
            lon=LON
            display_name="Valmiera (defaulted)"
        return (lat, lon, display_name)
    else:
        logger.info("OSM response is empty")
        return (-200, -200, "null")
    
# Print out a list of satellite passes in a human readable format.
# Displaying a separate message if there are no passes visible at location!
def print_passes(response_json, full_place_name):
    if 'info' in response_json and response_json['info']['passescount'] == 0:
        print(f"No visual passes found at location {full_place_name} for now!")
        return
    print(f"ISS will be visible at \"{full_place_name}\" at these times:")
    for event in response_json['passes']:
        date_and_time = datetime.fromtimestamp(event['startUTC']).strftime('%d.%m.%Y %H:%M:%S')
        print(date_and_time, "for", event['endUTC']-event['startUTC'], "seconds")    

# Take values from json response and the coords list and push into db. 
# The 3 values in coords list are separated in case default values are used.
def db_insert_values_from_json(response_json, place_lat, place_lon, place_name):
    if 'info' in response_json and response_json['info']['passescount'] == 0:
        return
    else:
        norad_id = response_json['info']['satid']
        for event in response_json['passes']:
            pass_array = (place_lat, place_lon, event['startUTC'], event['endUTC'], event['duration'], norad_id)
            push_iss_pass_to_db(place_name, pass_array)

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

        mysql_config_mysql_host = config.get('mysql_config', 'mysql_host')
        mysql_config_mysql_db = config.get('mysql_config', 'mysql_db')
        mysql_config_mysql_user = config.get('mysql_config', 'mysql_user')
        mysql_config_mysql_pass = config.get('mysql_config', 'mysql_pass')
        
        N2YO_API_KEY = config.get('n2yo', 'api_key')
        N2YO_API_URL = config.get('n2yo', 'api_url')

        OSM_API_URL = config.get('osm', 'api_url')
        OSM_JSON_VER = config.get('osm', 'api_json_ver')
        # Place for which to get coords from OSM
        PLACE_NAME = config.get('user', 'place_name')
        # Norad id for satellite. 25544 = ISS
        NORAD_ID = config.get('user', 'norad_id')
        # Default observer data: LATitude and LONgitude are float values; ALT - elevation in meters as int value.
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

    # Initiate DB connection
    init_db()
    
    # If no place provided - use config default coordinates. Else get coords from OSM.
    if PLACE_NAME == "":
        logger.info(f"No place name provided for OSM. Using defaults.")
        PLACE_NAME = "The default coordinates"
        coords = (LAT, LON, PLACE_NAME)
    else:
        logger.info(f"Getting data from OSM for {PLACE_NAME}")
        osm_search_response = get_osm_search_response(OSM_API_URL, PLACE_NAME, OSM_JSON_VER)
        osm_response_json = check_osm_response(osm_search_response)
        coords = get_osm_search_coords(osm_response_json)
        logger.info("DONE")

    # Getting request from N2YO
    logger.info(f"Getting data from N2YO for {PLACE_NAME}")
    n2yo_response = get_n2yo_response(N2YO_API_URL, NORAD_ID, coords[0], coords[1], ALT, DAYS, VISIBILITY, N2YO_API_KEY)
    n2yo_response_json = check_n2yo_response(n2yo_response)
    logger.info("DONE")

    # Inserting the gotten values from N2YO into the DB.
    db_insert_values_from_json(n2yo_response_json, coords[0], coords[1], coords[2])

    # Finally print the visible passes of the satellite
    print("\n\nVisual Passes Response:")
    print_passes(n2yo_response_json, coords[2])
