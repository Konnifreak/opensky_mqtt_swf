import requests
import sqlite3
import dotenv

con = sqlite3.connect("sky.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS airlines(iata_code , name, icao_code PRIMARY KEY)")

config = dotenv.dotenv_values(".env")

url = "https://iata-and-icao-codes.p.rapidapi.com/airlines"

headers = {
	"X-RapidAPI-Key": config["RAPIDAPI"],
	"X-RapidAPI-Host": "iata-and-icao-codes.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers)

print(response.text)
count = 0
insert_str = []

for test in response.json():
    count += 1
    if test["icao_code"] != "null":
        insert_str.append((test["iata_code"], test["name"], test["icao_code"]))




insert_str = insert_str[:-2]
cur.executemany("INSERT or IGNORE INTO airlines VALUES(?,?,?);",insert_str)
con.commit() 
print(count)