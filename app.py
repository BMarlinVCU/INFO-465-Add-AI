import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

from build_db import build
build()

st.set_page_config(page_title="Weather Dashboard", layout="wide")

@st.cache_data #prevents data reload
def load_data():
    conn = sqlite3.connect("project.db")
    df_weather = pd.read_sql_query("SELECT * FROM WEATHER", conn)
    df_weather["time"] = pd.to_datetime(df_weather["time"])
    conn.close()
    return df_weather

df_weather=load_data()

location_names={1:"Richmond",2:"Williamsburg"}
df_weather["location_name"]=df_weather["location_id"].map(location_names)

st.title("Weather Dashboard😊😊")

#sidebar filter
choice=st.sidebar.selectbox("Location",["Both","Richmond","Williamsburg"])

if choice=="Both":
    filtered=df_weather
else:
    filtered=df_weather[df_weather["location_name"]==choice]

st.subheader("Temp over time")

fig=px.line(filtered,x="time",y="temperature_c",color="location_name")
fig.update_xaxes(tickformat="%b %d %H:%M")
st.plotly_chart(fig,use_container_width=True)

st.text("This is my dataframe")
st.dataframe(df_weather)#shows data frame