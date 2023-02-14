import logging
import time
import osrm

import os
import sys
import json
import csv
import requests
import datetime
from lxml import etree
import numpy as np
import argparse
import sqlite3
import math

OSRM_DOCKER = "http://localhost:5000"
NETWORK_FILE = "sumo/trento.net.xml"
PATH_ROUTES ="sumo/route/"
VCLASS = "passenger"
PATH_CGF="sumo/"
LIST="sumo/script/list.csv"
DATABASE="measuraments/avg_database.db"
DURATION=900.00
CFG="trento.sumo.cfg"

def setup():
    #To use the library, the <SUMO_HOME>/tools directory must be on the python load path. 
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:   
        sys.exit("[Please declare environment variable 'SUMO_HOME']")

    #create route folder
    if not(os.path.exists(PATH_ROUTES) and os.path.isdir(PATH_ROUTES)):
        os.makedirs(PATH_ROUTES)
        print("[Created folder: route]")

def convert_coord_to_sumo(net, point):
    point = point.replace("\xa0", ".")
    lat, lon = point.split(",")
    radius = 1
    x, y = net.convertLonLat2XY(lon, lat)
    i=0

    IsPassenger = False
    while IsPassenger == False:
        edges = net.getNeighboringEdges(x, y, radius + i)
        i += 0.5

        if(len(edges) == 1 and edges[0][0].allows("passenger")):
            return edges[0][0]
        
        if(len(edges) > 1):
            distances_and_edges = sorted([(edge, dist) for edge, dist in edges], key=lambda e: e[1])
            for indexl, item in enumerate(distances_and_edges):
                closest_edge, dist = item
                if(closest_edge.allows("passenger")):
                    return closest_edge

def get_info_path(src, via, dst):
    #connection to apis
    client = osrm.Client(host=OSRM_DOCKER)

    src_lat, src_lon = src.split(",")
    via_lat, via_lon = via.split(",")
    dst_lat, dst_lon = dst.split(",")
    
    res = client.route(
        coordinates=[[float(src_lon), float(src_lat)], [float(dst_lon), float(dst_lat)]],
        geometries=osrm.geometries.geojson,
        overview=osrm.overview.full)

    distance = res['routes'][0]['distance']
    duration = res['routes'][0]['duration']
    return distance,duration

def get_cars_path(src_name, via_name, dst_name, start, end, day):
    
    #connection to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    #setting query values
    query_values = [
        (start, end, day, src_name[0], src_name[1]),
        (start, end, day, via_name[0], via_name[1]),
        (start, end, day, dst_name[0], dst_name[1])
    ]

    total = 0
    #executing queries
    for query_value in query_values:
        cursor.execute("""
            SELECT AVG(avg_car)
            FROM avg_measuraments
            WHERE hour >= ? AND hour < ? AND day_of_week = ? AND id1 = ? AND id2 = ?
            """, query_value)
        result = cursor.fetchone()
        total = total + int(result[0])
    
    #avarage car
    total = total/3

    return math.ceil(total)

def write_route_xml(route,filename, i, cars):
    #Creating XML route file
    root = etree.Element("routes")
    doc = etree.ElementTree(root)
    vType = etree.SubElement(root, "vType", attrib={"id": "type{}".format(i),"vClass": VCLASS})
    vehicle = etree.SubElement(root, "flow", attrib={"id": "route{}".format(i), "type": "type{}".format(i), "begin": "0.00", "end":"{}".format(DURATION), "number":"{}".format(cars)})
    route = etree.SubElement(vehicle, "route", attrib={"edges": ' '.join(route)})
    doc.write(PATH_ROUTES+filename, xml_declaration=True, encoding='utf-8', pretty_print=True) 
    print("Created file:\t{}\n".format(filename))
    return

def write_cfg_xml(rows, name):
    #Creating XML File
    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "noNamespaceSchemaLocation")
    nsmap = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    conf = etree.Element("configuration", {attr_qname: "http://sumo.dlr.de/xsd/routes_file.xsd"}, nsmap=nsmap)
    doc = etree.ElementTree(conf)

    input = etree.SubElement(conf, "input")
    net_file = etree.SubElement(input, "net-file", attrib={"value": "trento.net.xml"})
    
    list = []
    for i in range(rows+1):
        list.append("route/r{}.xml".format(i))

    route_files = etree.SubElement(input, "route-files", attrib={"value": "{}".format(', '.join(list))})
    additional_files = etree.SubElement(input, "additional-files", attrib={"value": "map.poly.xml"})

    time = etree.SubElement(conf, "time")
    begin = etree.SubElement(time, "begin", attrib={"value": "0"})
    end = etree.SubElement(time, "end", attrib={"value": "{}".format(DURATION)})
    step_length = etree.SubElement(time, "step-length", attrib={"value": "1"})
    delay = etree.SubElement(time, "delay", attrib={"value": "500"})


    doc.write(PATH_CGF+name, xml_declaration=True, encoding='utf-8', pretty_print=True) 

    print("Created file:\t{}\n".format(name))
    
def sumo(start, end, day):
    setup()
    import sumolib
    
    #loading network file
    net = sumolib.net.readNet(NETWORK_FILE)

    with open(LIST, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        #get header names
        header = next(reader)

        index = -1 #TODO: sistemare
        for row in reader:
            print("------------ Track [{}] ------------".format(row[0]))
            print("Name:\t\t{} to {}".format(row[1], row[7]))
            print("Coordinates:\t{} - {} - {}".format(row[3], row[6], row[9]))

            src = row[3]
            via = row[6]
            dst = row[9]

            #convert source, via (middle) and destination points to sumo coordinates
            src_sumo = convert_coord_to_sumo(net, src)
            via_sumo = convert_coord_to_sumo(net, via)
            dst_sumo = convert_coord_to_sumo(net, dst)
            print("Sumo:\t\t{} - {} - {}".format(src_sumo, via_sumo, dst_sumo))

            #get fastest path
            path_1 = net.getFastestPath(fromEdge=src_sumo, toEdge=via_sumo, vClass=VCLASS)
            path_2 = net.getFastestPath(fromEdge=via_sumo, toEdge=dst_sumo, vClass=VCLASS)


            route = []
 
            for j, junction in enumerate(path_1[0]):
                route.append(junction.getID())
            
            for j, junction in enumerate(path_2[0]):
                if(j!=0):
                    route.append(junction.getID())
            
            #getting path information using osmr apis
            distance, duration = get_info_path(src, via, dst)
            print("Distance:\t{} meters".format(distance))
            print("Duration:\t{} seconds".format(duration))

            #getting hypothetical number of cars
            src_name = (row[1], row[2]) 
            via_name = (row[4], row[5])
            dst_name = (row[7], row[8])
            cars = get_cars_path(src_name, via_name, dst_name, start, end, day)
            print("Cars:\t\t{} units".format(cars))
            
            index+=1
            write_route_xml(route, "r{}.xml".format(index), index, cars)

        
        write_cfg_xml(index, CFG)

    return 

#parsing argument
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('start', type=str, help='start')
parser.add_argument('end', type=str, help='end')
parser.add_argument('day', type=str, help='day')

args = parser.parse_args()

start = args.start
end = args.end
day = args.day

#creating scenario's files
sumo(start, end, day)



    

