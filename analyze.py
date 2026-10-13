import sqlite3

conn=sqlite3.connect("project.db")

#print(conn.execute(""" SELECT * FROM WEATHER a WHERE temperature_c>30""").fetchall())
print(conn.execute("""SELECT a.*,b.city FROM WEATHER a 
JOIN LOCATIONS b on a.location_id=b.location_id where city="Richmond" """).fetchall())

conn.close()
