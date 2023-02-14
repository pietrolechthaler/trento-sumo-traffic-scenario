# OpenCellID Database
"""
This script generates hypothetical position of the LTE BSs located in a given area from OpenCellID's raw data.

Usage:
    $ python antenna.py
OpenCellId:     https://opencellid.org/
Database:       http://opencellid.org/downloads.php
Documentation:  http://wiki.opencellid.org/wiki/Main_Page
Repository:     https://github.com/pietrolechthaler/
Author: Pietro Lechthaler
"""

import csv
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2
import numpy as np
import folium
import logging
import time

#log file setup
filename=__file__
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

#Default MAX and MIN Latitude and Longitude 
LAT_MIN = 11.07308106855686
LAT_MAX = 11.175828989727933
LON_MIN = 46.02298019910151
LON_MAX = 46.120872278604594

#type of filtered antennas
ANTENNA_TYPE = ['LTE']

#maximum distance between points
RADIUS = 300

#minimum number of each measurament
SAMPLES_LIMIT = 30

#file names
DATABASE = "./database/222.csv"
FOLDER = "trento"
RAW = "./trento/tn_lte_raw.csv"
FILTERED = "./trento/tn_lte_filtered.csv"
MEAN = "./trento/mean_points.csv"
HTML = "./trento/BS.html"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371 # radius of the earth in km
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c
    return d

def extract():
    #create folder
    if not(os.path.exists("./"+FOLDER) and os.path.isdir("./"+FOLDER)):
        os.makedirs("./"+FOLDER)
        print("Created folder: "+FOLDER)

    #database file
    with open(DATABASE, 'r') as file:
        csvreader = csv.reader(file)
        counter = 0 #number of antenna
       
        for row in csvreader:
            if ((float(row[6]) >= LAT_MIN and float(row[6]) <= LAT_MAX) and (float(row[7]) >= LON_MIN and float(row[7])<= LON_MAX) and (str(row[0]) in ANTENNA_TYPE)):
                counter +=1
                
                #Creation of a file containing the antennas present in the chosen area
                with open(RAW, 'a+', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(row)
        
        if(counter != 0):
            print("Number of antennas: {}".format(counter))
            print("Created new database: {}".format(RAW))
            
def processing(groups):
    #Loading database filtered
    df = pd.read_csv(RAW, index_col=False, header=None)

    #remove rows with less than 30 samples
    samples = pd.to_numeric(df.iloc[:,9])
    filtered = df[samples > SAMPLES_LIMIT]

    #save csv with filtered data
    filtered.to_csv(FILTERED, index=False, header=False)
    print("Created new database: {}".format(FILTERED))


    df = pd.read_csv(FILTERED)

    for index, row in df.iterrows():
        lat1 = row[7]
        lon1 = row[6]
        
        #flag to track if the current point has been added to a group
        added_to_group = False
        
        #Iterate over each existing group
        for group in groups:
            lat2 = group[0][7]
            lon2 = group[0][6]
            #distance between the current point and the first point in the group
            distance = haversine(lat1, lon1, lat2, lon2) * 1000 #convert to meters

            if distance < RADIUS:
                group.append(row)
                added_to_group = True
                break
        #If the current point has not been added to a group, create a new group with the current point
        if not added_to_group:
            groups.append([row])
    
    #Debug: print the groups of points
    # for i, group in enumerate(groups):
    #     logging.debug("--------------------------------------")
    #     logging.debug("Group", i + 1)
    #     logging.debug(pd.DataFrame(group))
    #     lat_mean = np.mean([row[7] for row in group])
    #     lon_mean = np.mean([row[6] for row in group])
    #     logging.debug("Mean Latitude:",lat_mean)
    #     logging.debug("Mean Longitude:", lon_mean)

def map(groups):
    m = folium.Map(location=[46.026214,11.121575], zoom_start=13)
    mean_data = []

    # Plot the points for each group
    for i, group in enumerate(groups):
        group_df = pd.DataFrame(group)
        mean_lat = np.mean([row[7] for row in group])
        mean_lon = np.mean([row[6] for row in group])
        mean_data.append([mean_lat, mean_lon])

        # Plot the points in the group
        for index, row in group_df.iterrows():
            folium.Marker(
                location=[row[7], row[6]],
                icon=folium.Icon(color='blue', icon="tower-cell", prefix='fa'),
            ).add_to(m)
        # Plot the mean location for the group
        folium.Marker(
            location=[mean_lat, mean_lon],
            icon=folium.Icon(color='red', icon="tower-cell", prefix='fa'),
            fill=True,
            fill_color="red",
        ).add_to(m)
        folium.Circle(location=[mean_lat, mean_lon],
                        radius= RADIUS,
                        color='#2596be',
                        fill=True,
                        fill_color='#2596be',
                        fillOpacity= 0.00001
        ).add_to(m)

    mean_df = pd.DataFrame(mean_data, columns=["lat", "lon"])
    # Save the data frame to a CSV file
    mean_df.to_csv(MEAN, header=False, index=False)
    print("Created new database: {}".format(MEAN))

    m.save(HTML)
    print("Created new html: {}".format(HTML))




if __name__ == "__main__":
    groups = []
    start_time = time.time()
    extract()
    processing(groups)
    map(groups)
    logging.debug("[Task executed in {} s]".format(round(time.time() - start_time),2))


