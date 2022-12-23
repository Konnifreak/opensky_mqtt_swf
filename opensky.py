import requests
import json
import paho.mqtt.client as mqtt
import time
import sys
import dotenv
import sqlite3
from math import sqrt
from FlightRadar24.api import FlightRadar24API

class mqtt:
    mqtt_server = ""
    mqtt_client_id = ""

    def __init__(self):
        self.mqtt_server = ""
        self.mqtt_client_id = "opensky_script"
        self.client

    def connect_mqtt(self):
        self.client = mqtt.Client(client_id = client_id_name)
        self.client.connect(mqtt_server)

class opensky:
    def __init__(self,LAMAX,LAMIN,LOMAX,LOMIN):
        self.plane_data = []
        self.lamax = LAMAX
        self.lamin = LAMIN
        self.lomax = LOMAX
        self.lomin = LOMIN
        self.fr_api = FlightRadar24API()
        self.airlines = self.fr_api.get_airlines()
        self.airports = self.fr_api.get_airports()
        
    
    def set_user(self, username, password):
        if (username or password) is not None:
            self.auth = (username,password)
        else:
            self.auth = ()

    def get_timestamp(self,offset):
        plane_time = time.time() - offset
        return str(int(plane_time))
    
    def get_planes_area(self):
        plane_data_all = requests.get('https://opensky-network.org/api/states/all?lamin=50.955322&lomin=6.903259&lamax=51.031423&lomax=7.032349&time=' + self.get_timestamp(120), auth=self.auth).json()
        if plane_data_all["states"] is None:
            return None
        flights_list = self.fr_api.get_flights(bounds="51.541807,50.333576,6.306030,7.730377")
        for planes in plane_data_all["states"]:
            print(planes)
            details = self.get_details(planes[0], flights_list)
            self.plane_data.append({"icao24": planes[0],"airline": self.get_airline(planes[1]),"callsign": planes[1], "country": planes[2], "altitute": planes[13], "longitude": planes[5], "latitude": planes[6],"timestamp": planes[4], "Origin": details[1].get("iata"),"Dest": details[0].get("iata")})

        return self.plane_data
    
    def get_airline_sql(self,icao_code):
        icao_code = icao_code[:3]
                # Verbindung zur Datenbank herstellen
        connection = sqlite3.connect("sky.db")
        cursor = connection.cursor()

        # Abfrage ausführen und Ergebnis abrufen
        cursor.execute("SELECT name FROM airlines WHERE icao_code=?", (icao_code,))
        result = cursor.fetchone()

        # Verbindung schließen
        connection.close()

        # IATA-Code zurückgeben, falls vorhanden, ansonsten None
        if result:
            return result[0]
        else:
            return None

    def get_airline(self,icao_code):
        result = search_dictionaries("ICAO", icao_code[:3], self.airlines)
        if result:
            return result[0].get("Name")
        else:
            return None
    
    def get_details(self, icao_code,flights):
        #flight = search_dictionaries("icao_24bit", icao_code.upper(), flights)
        #flight = any(x for x in flights if x.icao_24bit == icao_code.upper())
        for flight in flights:
            print(flight.icao_24bit)
            result=[]
            if flight.icao_24bit == icao_code.upper():
                flight = [x for x in flights if x.icao_24bit == icao_code.upper()]
                result.append({"iata": flight[0].destination_airport_iata})
                result.append({"iata": flight[0].origin_airport_iata})

                #TODO add Airport name

            if result:
                return result
            else:
                result.append({})
                result.append({})
                return result
                
        

#----------------Functions-----------------

def inital_env():
    return dotenv.dotenv_values(".env")

def search_dictionaries(key, value, list_of_dictionaries):
    return [element for element in list_of_dictionaries if element[key] == value]

def distance(long,long_target, lat, lat_target):
    # Calculate the Euclidean distance between two coordinates
    return sqrt((long - long_target)**2 + (lat_target - lat_target)**2)

def closest_coordinates(planes, target_coord):
    closest_coord = (planes[0].get("icao24"))
    min_distance = distance(planes[0].get("longitude"), target_coord[1], planes[0].get("latitude"), target_coord[0])
    
    for plane in planes:
        curr_distance = distance(plane.get("longitude"), target_coord[1], plane.get("latitude"), target_coord[0])
        
        if curr_distance < min_distance:
            min_distance = curr_distance
            closest_coord = plane.get("icao24")

    return closest_coord

#----------------Main-----------------

if __name__ == '__main__':
    config = inital_env()
    sky = opensky(config["LAMAX"],config["LAMIN"],config["LOMAX"],config["LOMIN"])
    sky.set_user(config["OPENSKY_USER"], config["OPENSKY_PASSWORD"])

    while True:
        result = sky.get_planes_area()
        if result is not None:
            print(result)
            print(closest_coordinates(sky.plane_data, [50.938361,6.959974])) 
        else:
            print("No flight found :(")
        time.sleep(120)
