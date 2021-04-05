#!/usr/bin/python

#Useful main libraries
from datetime import datetime
import pytz
import sys

#Libraries for serial communication with Linky
import serial

#Libraries for InfluxDB
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

#---------FUNCTIONS---------

#Transforms a byte array to a string and removes the last two characters
def clean_data(bytes_text):
	text = bytes_text.decode("utf-8")
	return text[:len(text)-2]

#Writes data to InfluxDB
def write_data(measurement, field, value, time, api):
	point = Point(measurement)\
	  .field(field, value)\
	  .time(time, WritePrecision.NS)
	api.write(bucket, org, point)

#---------EXECUTION---------

#Debug mode
debug = False
if len(sys.argv)>1:
	if str(sys.argv[1])=="debug":
		debug = True

#Initialize serial port ttyS0 on RaspberryPi zero
ser = serial.Serial(
	port='/dev/ttyS0',
	baudrate = 1200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.SEVENBITS,
	timeout=1
	)

#Pulling data from the serial port
#Clean the serial input
ser.flushInput()
while True:
	try:
		#Get a line from serial
		ser_bytes=ser.readline()
		#Convert the bytes to a string
		ser_string=ser_bytes.decode("utf-8")

		#Data block starts with ADCO
		if ser_string.startswith("ADCO"):
			#Retrieve each line and clean its content
			val_ADCO = clean_data(ser_bytes)
			val_OPTARIF = clean_data(ser.readline())
			val_ISOUSC = clean_data(ser.readline())
			val_BASE = clean_data(ser.readline())
			val_PTEC = clean_data(ser.readline())
			val_IINST = clean_data(ser.readline())
			val_IMAX = clean_data(ser.readline())
			val_PAPP = clean_data(ser.readline())
			val_HHPHC = clean_data(ser.readline())
			val_MOTDETAT = clean_data(ser.readline())
			ser.close()
			break
	except KeyboardInterrupt:
		print("Keyboard Interrupt")
		ser.close()
		break

#Debug mode: print the values
if debug:
	print("ADCO:", val_ADCO)
	print("OPTARIF:", val_OPTARIF)
	print("ISOUSC:", val_ISOUSC)
	print("BASE:", val_BASE)
	print("PTEC:", val_PTEC)
	print("IINST:", val_IINST)
	print("IMAX:", val_IMAX)
	print("PAPP:", val_PAPP)
	print("HHPHC:", val_HHPHC)
	print("MOTDETAT:", val_MOTDETAT)

#Configuration of InfluxDB v2 - Bucket "linky"
token = "_vvtDurXZJgFZCe1wpTXVopuw_BwUdBiuiBFaTMfhMYQYeICZTZB2OqIDwMpEfoEVf1IcVAkvmQ7HmzppTLEaw=="
org = "Kgibs"
bucket = "linky"
client = InfluxDBClient(url="http://192.168.0.150:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

#Set TimeZone and date
date_now = datetime.now(pytz.timezone('Europe/Paris'))

#Write data in InfluxDB
write_data("mem", "ADCO", val_ADCO.split()[1], date_now, write_api)
write_data("mem", "OPTARIF", val_OPTARIF.split()[1], date_now, write_api)
write_data("mem", "ISOUSC", int(val_ISOUSC.split()[1]), date_now, write_api)
write_data("mem", "BASE", int(val_BASE.split()[1])/1000, date_now, write_api)
write_data("mem", "PTEC", val_PTEC.split()[1], date_now, write_api)
write_data("mem", "IINST", int(val_IINST.split()[1]), date_now, write_api)
write_data("mem", "IMAX", int(val_IMAX.split()[1]), date_now, write_api)
write_data("mem", "PAPP", int(val_PAPP.split()[1]), date_now, write_api)
write_data("mem", "HHPHC", val_HHPHC.split()[1], date_now, write_api)
write_data("mem", "MOTDETAT", val_MOTDETAT.split()[1], date_now, write_api)
