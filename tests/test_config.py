import os
import requests
import mysql.connector

# Dont need datetime
from configparser import ConfigParser

print("Configuration file test")

# Testing if configuration file exists on disk in the current working directory
print("----------")
print("Checking if config file exists -->")
assert os.path.isfile("config.ini") == True
print("OK")
print("----------")

# Opening the configuration file
config = ConfigParser()
config.read('config.ini')

# Checking if all OSM related config options are present in the config file
print("Checking if config has NASA related options -->")
assert config.has_option('osm', 'api_url') == True
assert config.has_option('osm', 'api_json_ver') == True
print("OK")
print("----------")

# Checking if all N2YO related config options are present in the config file
print("Checking if config has NASA related options -->")
assert config.has_option('n2yo', 'api_key') == True
assert config.has_option('n2yo', 'api_url') == True
print("OK")
print("----------")

# Checking if all default user related config options are present in the config file
print("Checking if config has NASA related options -->")
assert config.has_option('user', 'place_name') == True
assert config.has_option('user', 'norad_id') == True
assert config.has_option('user', 'latitude') == True
assert config.has_option('user', 'longitude') == True
assert config.has_option('user', 'altitude') == True
assert config.has_option('user', 'visibility') == True
assert config.has_option('user', 'prediction_days') == True
print("OK")
print("----------")


# Checking if all MYSQL related config options are present in the config file
print("Checking if config has MYSQL related options -->")
assert config.has_option('mysql_config', 'mysql_host') == True
assert config.has_option('mysql_config', 'mysql_db') == True
assert config.has_option('mysql_config', 'mysql_user') == True
assert config.has_option('mysql_config', 'mysql_pass') == True
print("OK")
print("----------")

# Checking if possible to connect to OSM with the existing config options
print("Checking if it is possible to connect to OSM API with the given config options -->")
osm_api_url = config.get('osm', 'api_url')
osm_api_json_ver = config.get('osm', 'api_json_ver')
r = requests.get(f"{osm_api_url}search.php?q=Riga&format={osm_api_json_ver}")
assert r.status_code == 200
print("OK")
print("----------")

# Checking if possible to connect to N2YO with the existing config options
print("Checking if it is possible to connect to N2YO API with the given config options -->")
n2yo_api_url = config.get('n2yo', 'api_url')
n2yo_api_key = config.get('n2yo', 'api_key')
n2yo_norad_id = config.get('user', 'norad_id')
n2yo_lat = config.get('user', 'latitude')
n2yo_lon = config.get('user', 'longitude')
n2yo_alt = config.get('user', 'altitude')
n2yo_visibility = config.get('user', 'visibility')
n2yo_predict_days = config.get('user', 'prediction_days')
r = requests.get(f"{n2yo_api_url}visualpasses/{n2yo_norad_id}/{n2yo_lat}/{n2yo_lon}/{n2yo_alt}/{n2yo_predict_days}/{n2yo_visibility}&apiKey={n2yo_api_key}")
assert r.status_code == 200
print("OK")
print("----------")

# Checking if possible to connect to MySQL with the existing config options
print("Checking if it is possible to connect to MYSQL with the given config options -->")
mysql_config_mysql_host = config.get('mysql_config', 'mysql_host')
mysql_config_mysql_db = config.get('mysql_config', 'mysql_db')
mysql_config_mysql_user = config.get('mysql_config', 'mysql_user')
mysql_config_mysql_pass = config.get('mysql_config', 'mysql_pass')
connection = mysql.connector.connect(host=mysql_config_mysql_host, database=mysql_config_mysql_db, user=mysql_config_mysql_user, password=mysql_config_mysql_pass)
assert connection.is_connected() == True
print("OK")
print("----------")

# Checking if log config files exist for log config
print("Checking if DB migration component log config file exists log_migrate_db.yaml -->")
assert os.path.isfile("log_migrate_db.yaml") == True
print("OK")
print("----------")
print("Checking if main.py component log config file exists log_worker.yaml -->")
assert os.path.isfile("log_main.yaml") == True
print("OK")
print("----------")
print("Checking if log destination directory exists -->")
assert os.path.isdir("log") == True
print("OK")
print("----------")
print("Checking if migration source directory exists -->")
assert os.path.isdir("migrations") == True
print("OK")
print("----------")
print("Configuration file test DONE -> ALL OK")
print("----------------------------------------")