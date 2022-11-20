import requests
import json
import paho.mqtt.client as mqtt
import time
import sys
import dotenv

class mqtt:
    mqtt_server = ""
    mqtt_client_id = ""

    def __init__(self):
        self.mqtt_server = "mqtt.kjasny.de"
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
        
    
    def set_user(self, username, password):
        if (username or password) is not None:
            self.auth = (username,password)
        else:
            self.auth = ()

    def get_timestamp(self,offset):
        plane_time = time.time() - offset
        return str(int(plane_time))
    
    def get_planes_area(self):
        plane_data_all = requests.get('https://opensky-network.org/api/states/all?lamin=6.899757&lomin=7.036228&lamax=50.928791&lomax=50.996472&time=' + self.get_timestamp(120), auth=self.auth).json()
        for planes in plane_data_all["states"]:
            self.plane_data.append({"callsign": planes[1], "country": planes[2], "altitute": planes[13], "on_ground": planes[8],"timestamp": planes[4]})

        return self.plane_data
#----------------Functions-----------------

def inital_env():
    return dotenv.dotenv_values(".env")

if __name__ == '__main__':
    config = inital_env()
    sky = opensky(config["LAMAX"],config["LAMIN"],config["LOMAX"],config["LOMIN"])
    sky.set_user(config["OPENSKY_USER"], config["OPENSKY_PASSWORD"])
    print(sky.get_planes_area())    
