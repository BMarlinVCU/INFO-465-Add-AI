import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

conn=sqlite3.connect("project.db")
df_weather=pd.read_sql_query("""SELECT * FROM WEATHER""", conn)
df_weather["time"] = pd.to_datetime(df_weather["time"])
print(df_weather.head(10))

ax = df_weather.plot(x="time",y="temperature_c")
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
plt.savefig("temps.png")

ax = df_weather[df_weather["location_id"]==1].plot(x="time",y="temperature_c")
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
plt.savefig("richmond_temps.png")

df_qual=pd.read_sql_query("""SELECT * FROM AIR_QUALITY""", conn)
df_qual["time"] = pd.to_datetime(df_qual["time"])
df_qual.head()

ax = df_qual[df_qual["location_id"]==1].plot(x="time",y="pm2_5")
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
plt.savefig("richmond_air.png")
