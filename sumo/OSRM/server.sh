#!/bin/bash
#Trento Sumo Traffic Scenario 
#Author: Pietro Lechthaler

echo "[DOCKER] Starting OSMR backend.."
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/trento.osrm