# Connessione al database
import sqlite3
import pandas as pd
import os
import logging
import time


#log file setup
filename=__file__
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

conn = sqlite3.connect("avg_database.db")
cursor = conn.cursor()


def query():
    cursor = conn.cursor()
    hour="07:05:00.000"
    day_of_week="5"
    id1="Trento-v. Sanseverino-v. Montebaldo"
    id2="[3] v. Sanseverino - str. x Rovereto - dir. Nord"

    cursor.execute("""
    SELECT avg_car
    FROM avg_measuraments
    WHERE hour = ? AND day_of_week = ? AND id1 = ? AND id2 = ?
    """, (hour, day_of_week, id1, id2))
    #cursor.execute("SELECT avg_car FROM avg_measuraments")
    results = cursor.fetchall()
    print(results)
    
    # Commit delle modifiche
    conn.commit()
    # Chiusura della connessione
    conn.close()

if __name__ == "__main__":
    start_time = time.time()
    query()
    logging.debug("[Task executed in {} s]".format(round(time.time() - start_time),2))
