#!/usr/bin/python3
import logging
import io
import pynmea2
import serial
import json
import firebase_admin
from firebase_admin import db
import os
import subprocess
import time

#logging.basicConfig(filename='/home/pi/Documents/dev/example.log',format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
#ser = serial.Serial('/dev/ttyS0', 115200,timeout=1)
#stream reader for serial connection
#sio = io.TextIOWrapper(io.BufferedRWPair(ser,ser))
#Json file structure
coordinatesToSend = {}
coordinatesToSend['coordinates'] =[] 
#Firebase connection variables
cred_object = firebase_admin.credentials.Certificate('/home/pi/Documents/configs/navigationapp_service_account.json')
navigation_app = firebase_admin.initialize_app(cred_object, {
	'databaseURL':'https://navigationapp-67bcf-default-rtdb.europe-west1.firebasedatabase.app/'
	})

ref = db.reference("/Coordinates")
#calculates lattitude
def lat(t):
	return (float(t[0:2]) + (float(t[2:9])/60))
#calculates longtitude
def lon(t):
	return (float(t[0:3]) + (float(t[3:10])/60))
#prepares data for json file
def preparingJson(latitude,longtitude,speed):
	coordinatesToSend['coordinates'].append({'latitude':latitude,'longtitude': longtitude, 'speed': speed})
	with open('/home/pi/Documents/dev/coordinates.json','w') as outfile:
		json.dump(coordinatesToSend,outfile,indent=2)
#creates and sends JSON file to firebase
def sendingJsonToFirebase(filename):
	with open(filename,"r") as f:
		file_contents = json.load(f)
	for key, value in file_contents.items():
		ref.push().set(value)
	print("Coordinates sent")
#opens a cell network	
def openPPPD():
	print("starting cell connection")
	# Start the "provider" process
	subprocess.call("sudo pon provider", shell=True)
	time.sleep(2)

#close cell network	
def closePPPD():
	print("turning off cell connection")
	# Stop the "provider" process
	subprocess.call("sudo poff provider", shell=True)

#checking if signal quality is good and if there is fix on position
def checkForFix():
	print("checking for fix")
	# Start the serial connection
	ser=serial.Serial('/dev/ttyS0', 115200, timeout=1)
	sio = io.TextIOWrapper(io.BufferedRWPair(ser,ser))
	# Turn on the GPS and check if gps is working
	while True:
		line = sio.readline()
		# Check if a fix was found
		if "$GNGGA" in line:
			msg = pynmea2.parse(line)
			if msg.gps_qual >= 1: 
				print("fix found")
				return True
			else:
				print("no fix found retrying in 5s")
				time.sleep(5)
#this function reads coordinates and sends them to firebase with help of other functions
#to read outcome in readable format use #print(repr(msg))
def getCoordinates():
	print("getting coordinates")
	ser=serial.Serial('/dev/ttyS0', 115200, timeout=1)
	sio = io.TextIOWrapper(io.BufferedRWPair(ser,ser))
	i=10
	while i >= 0:
		try:
			line = sio.readline()
			if "$GNRMC" in line:
				msg = pynmea2.parse(line)
				if str(msg.status) == 'A':
					newLat = lat(str(msg.lat))
					newLon = lon(str(msg.lon))
					newSpeed = str(msg.spd_over_grnd)
					preparingJson(newLat,newLon,newSpeed)
					i=i-1
		except serial.SerialException as e:
			logging.error('Device error: {}'.format(e))
		except pynmea2.ParseError as e:
			logging.error('Parse error: {}'.format(e))

# program start
getCoordinates()
openPPPD()
time.sleep(3)
sendingJsonToFirebase("/home/pi/Documents/dev/coordinates.json")
os.remove("/home/pi/Documents/dev/coordinates.json")
time.sleep(1)
closePPPD()
"""
if openPPPD():
	time.sleep(3)
	while True:
		# Close the cellular connection
		if closePPPD():
			print("closing connection")
			time.sleep(1)
		# Make sure there's a GPS fix
		if checkForFix():
			getCoordinates()
			# Turn the cellular connection on every 10 reads
			print("opening connection")
			if openPPPD():
				time.sleep(3)
				print("sending data")
				sendingJsonToFirebase("coordinates.json")
				os.remove("coordinates.json")
				print("streaming complete")
	
"""	
	
	
	


