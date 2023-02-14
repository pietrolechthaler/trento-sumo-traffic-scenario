# Purpose:      polyconvert imports geometrical shapes (polygons or points of interest) from different sources, converts them to a representation that may be visualized using sumo-gui.
# System:       portable (Linux/Windows is tested); runs on command line
# Input:        polygons or pois
# Output:       A generated SUMO-shape file
# Language:     C++
# Document:     https://sumo.dlr.de/docs/polyconvert.html
# Author:       Pietro Lechthaler

import os
import time
import subprocess
import logging

#I/O files
INPUT_FILE = "../trento.net.xml"
MAP_FILE ="../database/trento.osm"
TYPE_FILE = "../typemap.xml"
OUTPUT_FILE = "../map.poly.xml"

#Configure the logging
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

polyconvert_cmd = ["polyconvert", "--net-file", INPUT_FILE, "--osm-files", MAP_FILE, "--type-file", TYPE_FILE, "-o", OUTPUT_FILE]

start_time = time.time()

subprocess.run(polyconvert_cmd)
print("[Created file: {}]".format(OUTPUT_FILE))
logging.debug("[Task executed in {} s]".format(round(time.time() - start_time),2))

