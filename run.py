#Trento Sumo Simulation
"""
Usage:
    $ python3 run.py
Repository:     https://github.com/pietrolechthaler/
Author: Pietro Lechthaler
"""

import logging
import time
import os, sys
import csv
import subprocess
import pandas as pd
import math


#menu settings
DAYS = ['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIME_RANGE = [(i, i + 15) for i in range(0, 1440, 15)]
OUTPUT_RANGE = ['No','Yes']

#sumo settings
SUMO_BINARY = "/opt/homebrew/Cellar/sumo/1.15.0/bin/sumo-gui"
SUMO_CFG = "sumo/trento.sumo.cfg"
DB_BS = "opencellid/trento/mean_points.csv"

#output
EMISSION = "trento_allXY_output.png"
AVG_BS = "trento_avg_time.csv"

#log file setup
filename=__file__
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def in_circle(lat1, lon1, lat2, lon2, radius):
    R = 6371000  # radius of the earth in m
    x = (math.radians(lon2) - math.radians(lon1)) * math.cos(0.5 * (math.radians(lat2) + math.radians(lat1)))
    y = math.radians(lat2) - math.radians(lat1)
    distance = R * math.sqrt(x*x + y*y)
    return distance <= radius

def format_time(minutes):
    return f"{minutes // 60:02}:{minutes % 60:02}"

def select_day():
    #menu
    print("\nChoose a day:")
    for i, day in enumerate(DAYS):
        print(f"{i + 1}. {day}")
    
    #collecting input
    day_choice = int(input("\nEnter the number corresponding to your choice: ")) - 1
    while(day_choice not in range(len(DAYS))):
        print("Invalid choice. Please try again.")
        day_choice = int(input("Enter the number corresponding to your choice: ")) - 1

    return day_choice

def print_time_range():
    rows, residue = divmod(len(TIME_RANGE), 4)
    if residue:
        rows += 1
    for row in range(rows):
        for col in range(4):
            index = row + col * rows
            if index >= len(TIME_RANGE):
                break
            start, end = TIME_RANGE[index]
            print(f"{index + 1}. {format_time(start)}-{format_time(end)}".ljust(20), end="")
        print("")

def select_time_range():
    #menu
    print("\nChoose a time range:")
    print_time_range()

    #collecting input
    time_range_choice = int(input("\nEnter the number corresponding to your choice: ")) - 1
    while(time_range_choice not in range(len(TIME_RANGE))):
        print("Invalid choice. Please try again.")
        time_range_choice = int(input("Enter the number corresponding to your choice: ")) - 1

    return TIME_RANGE[time_range_choice]

def select_output():

    print("\nDo you want to generate output files?")
    print("1. No")
    print("2. Yes")
   
    #collecting input
    output_choice = int(input("\nEnter the number corresponding to your choice: ")) - 1
    while(output_choice not in range(len(OUTPUT_RANGE))):
        print("Invalid choice. Please try again.")
        output_choice = int(input("Enter the number corresponding to your choice: ")) - 1

    return output_choice


def setup():
    logo="""                                  
     ████████ ███    ██ ███████ ████████ 
        ██    ████   ██ ██         ██    
        ██    ██ ██  ██ ███████    ██    
        ██    ██  ██ ██      ██    ██    
        ██    ██   ████ ███████    ██    
                                             
    """
    print(logo)
    print("Trento SUMO Traffic (TuST) Scenario")

    day = select_day()
    selected_time_range = select_time_range()
    output = select_output()

    start, end = selected_time_range
    return start, end, day, output


if __name__ == "__main__":

    #choosind day and hour
    start, end, day, output = setup()
    start_time = time.time()
    
    if(output==0):
        sumo_cmd = [SUMO_BINARY, "-c", SUMO_CFG]
    else:
        sumo_cmd = [SUMO_BINARY, "-c", SUMO_CFG, "--emission-output", "emissions.xml", "--fcd-output", "fcd.xml", "--quit-on-end"] #

    print(f"[You have selected {DAYS[day]} from {format_time(start)} to {format_time(end)} - Output: {OUTPUT_RANGE[output]}]")
    print("\nLoading scenario..\n")

    #loading scenario
    subprocess.call(["python3", "sumo/script/scenario.py", str(format_time(start)), str(format_time(end)), str(day)])

    #importing traci
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    import traci
    
    traci.start(sumo_cmd)

    lte_bs = pd.read_csv(DB_BS, header=None, names=["latitude", "longitude"])
    step = traci.simulation.getDeltaT()

    #counter initialization
    time_spent_counter = [0] * len(lte_bs)
    vehicle_antenna_counter = [[] for _ in range(len(lte_bs))]
    avg_time_antenna = [0] * len(lte_bs)


    #main loop
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        for i, vehicle in enumerate(traci.vehicle.getIDList()):
            x, y = traci.vehicle.getPosition(vehicle)
            lon, lat = traci.simulation.convertGeo(x, y)

            for antenna, coord in lte_bs.iterrows():
                if in_circle(float(coord["latitude"]), float(coord["longitude"]), lat, lon, 2000):                
                    time_spent_counter[antenna] += step
                    if vehicle not in vehicle_antenna_counter[antenna]:
                        vehicle_antenna_counter[antenna].append(vehicle)
            

    for i, count in enumerate(time_spent_counter):
        if(len(vehicle_antenna_counter[i])!=0):
            avg_time_antenna[i] = time_spent_counter[i]/len(vehicle_antenna_counter[i])
        else:
            avg_time_antenna[i] = 0
    traci.close()

    #output
    if(output==1):
        print("------------ Output ------------")
        #emission
        #output_1 = ["python3 $SUMO_HOME/tools/visualization/plotXMLAttributes.py", "-x", "x", "-y", "y", "-s", "-o", EMISSION, "fcd.xml", "--scatterplot"]
        output_1 = "python $SUMO_HOME/tools/visualization/plotXMLAttributes.py -x x -y y -s -o allXY_output.png fcd.xml --scatterplot"
        
        subprocess.run(output_1, shell=True)
        print("Created file:\t{}".format(EMISSION))

        #avg time basestations
        df = pd.read_csv(DB_BS, header=None, names=["latitude", "longitude"])
        df["avg_time"] = avg_time_antenna
        df.to_csv(AVG_BS, header=False, index=False)
        print("Created file:\t{}".format(AVG_BS))

    logging.debug("[Task executed in {} s]".format(round(time.time() - start_time),2))