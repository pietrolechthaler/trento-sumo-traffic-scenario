# Connessione al database
import sqlite3
import pandas as pd
import os
import logging
import time


PATH_TO_RAW = "raw/" 
#log file setup
filename=__file__
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
conn = sqlite3.connect("database.db")
conn2 = sqlite3.connect("avg_database.db")
cursor2 = conn2.cursor()


def loading():
    cursor = conn.cursor()
    #Create database
    cursor.execute("""CREATE TABLE IF NOT EXISTS measuraments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id1 text,
                        id2 text,
                        car integer,
                        hour text,
                        day text
                    )""")

    all_files = [f for f in os.listdir(PATH_TO_RAW) if f.endswith('.csv')]
    for filename in all_files:
        with open(os.path.join(PATH_TO_RAW, filename), "r") as file:
            for line in file:
                id1, id2, car, timestamp = line.strip().split(";")
                if(car==""): car=0
                day, hour = timestamp.split(" ")[0], timestamp.split(" ")[1]
                cursor.execute("insert into measuraments (id1, id2, car, hour, day) values (?, ?, ?, ?, ?)",(id1, id2, car, hour, day))

    # Commit delle modifiche
    conn.commit()
    # Chiusura della connessione
    conn.close()

def result():
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id1, id2, hour, strftime('%w', day) AS day_of_week, ROUND(AVG(car), 0)
    FROM measuraments
    GROUP BY id1, id2, hour, day_of_week
    """)

    results = cursor.fetchall()

    cursor2.execute("""CREATE TABLE IF NOT EXISTS avg_measuraments (
                        id1 text,
                        id2 text,
                        hour text,
                        day_of_week integer,
                        avg_car integer
                    )""")

    cursor2.executemany("""
    INSERT INTO avg_measuraments (id1, id2, hour, day_of_week, avg_car)
    VALUES (?, ?, ?, ?, ?)
    """, results)

    # Commit delle modifiche
    conn.commit()
    conn2.commit()
    # Chiusura della connessione
    conn.close()
    conn.close()

if __name__ == "__main__":
    start_time = time.time()
    loading()
    result()
    logging.debug("[Task executed in {} s]".format(round(time.time() - start_time),2))
