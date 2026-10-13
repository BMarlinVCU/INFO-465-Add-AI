import json
import pathlib
import sqlite3

LOCATIONS=[
    {"location_id":1,"city":"Richmond","latitude":37.55,"longitude":-77.46},
    {"location_id":2,"city":"Williamsburg","latitude":37.27,"longitude":-76.71},
        
]


DATA_DIR=pathlib.Path("data")

def build():
    conn=sqlite3.connect("project.db")

    conn.execute("DROP TABLE IF EXISTS locations")
    conn.execute("DROP TABLE IF EXISTS weather")
    conn.execute("DROP TABLE IF EXISTS air_quality")

    conn.execute("CREATE TABLE locations(location_id INTEGER PRIMARY KEY,city text,latitude REAL,longitude REAL)")
    conn.execute("CREATE TABLE weather(location_id INTEGER, time TEXT, temperature_c REAL)")
    conn.execute("CREATE TABLE air_quality(location_id INTEGER, time text, pm2_5 REAL)")

    for place in LOCATIONS:
        loc_id=place["location_id"]
        city=place["city"]

        conn.execute("INSERT INTO locations VALUES (?,?,?,?)",
                    (loc_id,city,place["latitude"],place["longitude"]))

        for path in sorted(DATA_DIR.glob(f"weather-{city}-*.json")):
            hourly=json.load(open(path))["hourly"]
            for time,temp in zip(hourly["time"],hourly["temperature_2m"]):    
                conn.execute("INSERT INTO weather VALUES (?,?,?)",(loc_id,time,temp))

        for path in sorted(DATA_DIR.glob(f"air_quality-{city}-*.json")):
            hourly=json.load(open(path))["hourly"]
            for time,pm in zip(hourly["time"],hourly["pm2_5"]):
                conn.execute("INSERT INTO air_quality VALUES (?,?,?)",(loc_id,time,pm))
        
    conn.commit()
    conn.close()

if __name__=="__main__":
    build()