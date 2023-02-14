# Purpose:      Extract, convert and process OpenStreetMap files. 
# System:       portable (Linux/Windows is tested); runs on command line
# Input:        OpenstreetMap file of large area
# Output:       A generated SUMO-road network; optionally also other outputs
# Language:     Python, C++
# Document:     https://sumo.dlr.de/docs/netconvert.html, https://wiki.openstreetmap.org/wiki/Osmconvert
# Author:       Pietro Lechthaler

import os
import time
import subprocess
import logging

#area
LAT_MIN = "11.07308106855686" 
LAT_MAX = "11.175828989727933"
LON_MIN = "46.022980199101512"
LON_MAX = "46.120872278604594"

#I/O files
INPUT_FILE = "../database/nord-est-latest.osm.pbf"
PBF_FILE = "../database/trento.osm.pbf"
OSM_FILE = "../database/trento.osm"

#Configure the logging
filename=__file__
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

start_time = time.time()

#extract area
extract_cmd = ["osmium", "extract", "-b", "{},{},{},{}".format(LAT_MIN,LON_MIN,LAT_MAX,LON_MAX), INPUT_FILE, "-o", PBF_FILE, "--overwrite"]
logging.debug(extract_cmd)
subprocess.run(extract_cmd)
print("[Created file: {}]".format(PBF_FILE))


logging.debug("[Task executed in {:.2f} s]".format(time.time() - start_time))

