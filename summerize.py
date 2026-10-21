import os
import sqlite3 
import pandas as pd 
from openai import OpenAI 
from build_db import build 

#build()
def make_summary():
    conn=sqlite3.connect("project.db")
    last_day=conn.execute("SELECT date(MAX(time)) from WEATHER").fetchone()[0]

    df=pd.read_sql_query("""
        SELECT location_id,
        ROUND(AVG(temperature_c),1 )AS avg_temp,
        ROUND(MIN(temperature_c),1)AS high,
        ROUND(MAX(temperature_c),1)AS low
        FROM weather 
        WHERE time>=date((SELECT MAX(time) FROM WEATHER),'-7 days')
        GROUP BY location_id""",conn)
    conn.close()

    df["location_name"]=df["location_id"].map({1:"Richmond",2:"Williamsburg"})
    numbers=df.to_string(index=False)

    print(numbers)

    client=OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"],
    )

    instructions=("You are a weather reporter. Summarize the following weather data for the last 7 days in a short paragraph. Convert Celsius to Fahrenheit. "
        "Include the average temperature, high and low temperatures for each location. "
        "Format the output as a news report. Tell me what clothes to wear based on the weather. "
        "Do not include any other information. "
    )
    try:
        response=client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role":"system","content":instructions},
                {"role":"user","content":numbers}
            ],
            reasoning_effort="low",
        )
        summary=response.choices[0].message.content

        print("\nWeather Summary:\n")
        return summary
    except Exception as e:
        print("Error generating summary:", e)   

if __name__=="__main__":
    build()
    make_summary()