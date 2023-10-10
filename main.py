import requests
import json
import sys
import datetime, time
from datetime import datetime
from configparser import ConfigParser

# Reading required values from config file
print("Loading configuration from file")
try:
    config = ConfigParser()
    config.read('config.ini')
    
    API_KEY = config.get('n2yo', 'api_key')
    API_URL = config.get('n2yo', 'api_url')

    # Norad id for satellite. 25544 = ISS
    NORAD_ID = config.get('user', 'norad_id')
    # Observer data: decimal degrees - latitude, longitude; meters - elevation. Default is ViA university.
    LAT = config.get('user', 'latitude')
    LON = config.get('user', 'longitude')
    ALT = config.get('user', 'altitude')
    # In seconds - length of time while satellite is visible in the sky
    VISIBILITY = config.get('user', 'visibility')
    # In days - how far into the future to predict ISS passovers, MAX = 10.
    DAYS = config.get('user', 'prediction_days')
except:
    print('Exception error in loading config')
print('DONE')

# Check if internet connection exists on device
def check_internet_connection():
    while True:
        try:
            requests.get('https://www.google.com/').status_code
            break
        except:
            print("No internet connection!")
            time.sleep(5)
            pass

# Prepares and requests URL to get visual passes from n2yo
def get_n2yo_response():
    url = f"{API_URL}visualpasses/{NORAD_ID}/{LAT}/{LON}/{ALT}/{DAYS}/{VISIBILITY}&apiKey={API_KEY}"
    response = requests.get(url)
    return response

# Check if URL response returned without error and return the json of response
def check_response():
    response = get_response()
    if response.status_code != 200:
        print("Error code", response.status_code, "from API URL")
        sys.exit(1)
    return response.json()

# Print out a list of satellite passes in a human readable format
def print_passes():
    visual_pass_response_json = check_response()
    # Check for 0 visual passes at location
    if visual_pass_response_json['info']['passescount'] == 0:
        print("No visual passes found at location for now!")
        return
    # Print all visible passes
    print("ISS will be visible at:")
    for event in visual_pass_response_json['passes']:
        date_and_time = datetime.fromtimestamp(event['startUTC']).strftime('%d.%m.%Y %H:%M:%S')
        print(date_and_time, "for", event['endUTC']-event['startUTC'], "seconds")

if __name__ == "__main__":
    check_internet_connection()
    ## Get visual passes for ISS. Print out received information.
    # response = get_response()
    print("\nVisual Passes Response:")
    # print(response, "\n")
    print_passes()
