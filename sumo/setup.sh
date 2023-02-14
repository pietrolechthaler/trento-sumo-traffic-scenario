#!/bin/bash
#Trento Sumo Traffic Scenario 
#Author: Pietro Lechthaler

echo "[SETUP] Trento Sumo Traffic Scenario"

echo "- Export and convert area from large dataset"
(cd script; python3 extract_area.py)
(osmconvert database/trento.osm.pbf > database/trento.osm; echo "[Created file: ../database/trento.osm]")

echo "- Generate road networks"
(cd script; python3 convert_osm_xml.py)

echo "- Import geometrical shapes"
(cd script; python3 convert_polygon.py)



