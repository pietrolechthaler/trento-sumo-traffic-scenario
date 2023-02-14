# Purpose:      netconvert imports digital road networks from different sources and generates road networks that can be used by other tools from the package.
# System:       portable (Linux/Windows is tested); runs on command line
# Input:        Definition of a road network
# Output:       A generated SUMO-road network; optionally also other outputs
# Language:     C++
# Document:     https://sumo.dlr.de/docs/netconvert.html
# Author:       Pietro Lechthaler

import os
import time
import subprocess
import logging

#I/O files
ORIGINAL_FILE = "../database/trento.osm"
OUTPUT_FILE = "../trento.net.xml"

#Configure the logging
logging.basicConfig(filename='process.log', level=logging.DEBUG, format='%(filename)s %(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

netconvert_cmd = ["netconvert", "--osm-files", ORIGINAL_FILE, "-o", OUTPUT_FILE, "--no-warnings"]

start_time = time.time()
subprocess.run(netconvert_cmd)

print("[Created file: {}]".format(OUTPUT_FILE))
logging.debug("[Task executed in {:.2f} s]".format(time.time() - start_time))
