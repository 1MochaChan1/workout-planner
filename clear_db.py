import sqlite3 as sql

con = sql.connect("Workout.db")
cur = con.cursor()

cur.execute("DELETE FROM Plans")
con.commit()
cur.close()
con.close()