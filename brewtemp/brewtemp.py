import configparser
import os
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Configuration Defaults
config_file = "brewtemp.ini"

def main():
    config = parse_config()
    sensor_ids = determine_sensors()
    sensor_data = take_readings(sensor_ids)
    upload_readings(sensor_data)

def determine_sensors():
    return ["0000000001", "0000000002", "0000000003"]

def take_readings(ids):
    sensor_readings = {}
    for id in ids:
        sensor_name = config.get('Main', id, fallback = id)
        sensor_readings[sensor_name] = read_sensor(id)
    return sensor_readings

def read_sensor(id):
    return 75 + int(id)

def upload_readings(sensor_data):

    # Construct the full reading using the sensor data
    sensor_data['timestamp'] = int(time.time())

    # Use a service account
    cred = credentials.Certificate(config['Main']['ServiceAccountFile'])
    firebase_admin.initialize_app(cred)

    # Push the sample to firebase
    collection = firestore.client().collection(config.get('Main', 'ProjectName', fallback = "default"))
    collection.document().set(sensor_data)

def parse_config():
    # Define a global for the configuration file, so it can be referenced by
    # the rest of the program
    global config
    global project_name
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Maybe do some validation here ?

    return config

if __name__ == "__main__":
    main()