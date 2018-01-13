#!/usr/bin/python3

import configparser
import os
import time
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Configuration Defaults
config_file = "brewtemp.ini"

def main():
    print('Initiating temperature logging script')
    config = parse_config()
    fb_collection = initiate_db_connection()
    sensor_ids = determine_sensors()

    while 1:
        sensor_data = take_readings(sensor_ids)
        upload_readings(fb_collection, sensor_data)
        time.sleep(60)

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

def initiate_db_connection():
    # Use the credentials to connect to the database
    # Use a service account
    cred = credentials.Certificate(config['Main']['ServiceAccountFile'])
    firebase_admin.initialize_app(cred)
    collection = firestore.client().collection(config.get('Main', 'ProjectName', fallback = "default"))
    return collection

def upload_readings(collection, sensor_data):
    # Construct the full reading using the sensor data
    sensor_data['timestamp'] = int(time.time())

    # Push the sample to firebase
    collection.document().set(sensor_data)

    print('Uploaded sample to firebase: \n' + json.dumps(sensor_data))

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
