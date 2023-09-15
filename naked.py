import requests
import json
from datetime import datetime

# Replace 'abcd-qwer-asdf' with your personal API key
API_KEY = 'abcd-qwer-asdf'

# Base URL for N2YO API
BASE_URL = 'https://api.n2yo.com/rest/v1/satellite/'
# Norad id for satellite. 25544 = ISS
SATELLITE_ID = 25544
# Observer data: decimal degrees - latitude, longitude; meters - elevation.
LAT = 57.54161
LON = 25.42826
ALT = 0
# In seconds - length of time while satellite is visible in the sky
VISIBILITY = 60
# In days - how far into the future to predict ISS passovers, MAX = 10.
DAYS = 10

# Prepares and requests URL to get visual passes
def get_visual_passes():
    url = f"{BASE_URL}visualpasses/{SATELLITE_ID}/{LAT}/{LON}/{ALT}/{DAYS}/{VISIBILITY}&apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

def print_passes():
    data = get_visual_passes()
    print("ISS will be visible at:")
    for event in data['passes']:
        date_and_time = datetime.fromtimestamp(event['startUTC']).strftime('%d.%m.%Y %H:%M:%S')
        print(date_and_time, "for", event['endUTC']-event['startUTC'], "seconds")

if __name__ == "__main__":
 
    # Get visual passes for ISS. Print out received information.
    visual_passes_response = get_visual_passes()
    print("\nVisual Passes Response:")
    print(visual_passes_response, "\n")
    print_passes()