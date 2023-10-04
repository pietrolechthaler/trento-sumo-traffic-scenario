<img src="main.png">

<p align="center">
  <h2 align="center">Trento Sumo Traffic Scenario</h2>
  <p align="center">
Simulation of Urban MObility using Open Data  <br>University of Trento - Thesis supervisor Prof. <a href="https://www.granelli-lab.org/staff/fabrizio-granelli">Fabrizio Granelli</a>
  </p>
</p>

## Table of contents
- [Description](#description)
- [Table of contents](#table-of-contents)
  - [Folder](#folder)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Contributors](#contributors)

### Description
Trento SUMO Traffic (TnST) is an application of the use of Open Data for the creation of a vehicular simulation within the city of Trento. In particular, in this project Open Data from the Municipality of Trento, about the traffic in the main arteries of the city, and OpenCellID, about the position of the LTE Radio Base Stations, are processed. The project aims to show that starting from open data it is possible to generate new information useful for urban traffic planning and environmental impact assessment, thus contributing to the diffusion of the culture of data sharing in city management. The document is divided in three sections, the first one is an introduction on the OpenSource concept, then in the central part the process of collection and elaboration of the information useful for the creation of the vehicular simulation is described, and finally the results and final considerations are illustrated.

### Folder
```
trento-sumo-traffic-scenario
├── sumo
├── measuraments
├── opencellid
```
- `sumo:` contains files for generating the vehicle simulation using SUMO simulator
- `measuraments:` contains the city's traffic measurement database, detector measurements, and explanatory documents
- `opencellid:` contains the database of LTE basestations of the city of Trento


### Requirements

For running each sample code:
- `Sumo:` https://sumo.dlr.de/docs/Installing/index.html
- `Docker:` https://docs.docker.com/engine/install/ubuntu/
- `Python` https://www.python.org/downloads/

### Setup

After installing the requirements needed to run the project. Clone this repo:
```
git clone https://github.com/pietrolechthaler/trento-sumo-traffic-scenario/
```

Start OSMR server:
```
$ cd trento-sumo-traffic-scenario/sumo/OSMR
$ chmod +x server.sh
$ ./server.sh
```
Processes OpenCellID data:
```
$ cd trento-sumo-traffic-scenario/opencellid
$ python3 antenna.py
```

Run the simulation:
```
cd trento-sumo-traffic-scenario
python3 run.py
```
### Usage

After starting the simulation, select a day of the week:

```
Choose a day:
1. Sunday
2. Monday
3. Tuesday
4. Wednesday
5. Thursday
6. Friday
7. Saturday

Enter the number corresponding to your choice:
```
Then, select a time range
```
Choose a time range:
1. 00:00-00:15      
2. 00:15-00:30      
3. 00:30-00:45 
...
Enter the number corresponding to your choice:
```
Finally, choose if you want to get outputs after the simulation is finished
```
Do you want to generate output files?
1. No
2. Yes

Enter the number corresponding to your choice:
```

To start the simulation, click on play.

### Contributors
| Name                 | Github                               |
|----------------------|--------------------------------------|
| Pietro Lechthaler    | pietro.lechthaler@studenti.unitn.it  |
