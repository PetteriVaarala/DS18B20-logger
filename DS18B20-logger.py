#!/usr/bin/python
import glob
import os
import subprocess
import time
import ConfigParser
import inspect
from influxdb import InfluxDBClient

# Get path for this script
script_filename = inspect.getfile(inspect.currentframe())   # get filename (usually with path)
script_path = os.path.dirname(script_filename)              # get relative path
path = os.path.realpath(script_path) + "/"                  # get real path

# Get configs
config = ConfigParser.ConfigParser()
config.read(path + 'DS18B20-logger.conf')
influx_host = config.get('influxdb', 'host')
influx_port = config.get('influxdb', 'port')
influx_database = config.get('influxdb', 'database')
influx_username = config.get('influxdb', 'username')
influx_password = config.get('influxdb', 'password')
location = config.get('tags', 'location')
address = config.get('tags', 'address')

hostname = os.uname()[1]
# Device directories
devices = glob.glob('/sys/bus/w1/devices/28-*')
#print(devices)

# https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing?view=all#software
def read_temp_raw(device):
    device_file = device + '/w1_slave'
    catdata = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out,err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines

def read_temp(device):
    # get raw data from device
    lines = read_temp_raw(device)

    # temperature is in second line, after "t="
    temp_pos = lines[1].find('t=')
    if temp_pos != -1:
        temp = lines[1][temp_pos+2:] # read temp
        temp = float(temp)/1000.0    # convert to float and to celsius
        return temp

for device in devices:
    # get device ID for sensor
    sensor = device.split('/')[-1]

    # get temperature from sensor
    temp = read_temp(device)

    # get time
    unixtime = int(time.time())
    date = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    # print log
    # Oct 25 15:24:36 raspberry1 DS18B20-logger: 28-00000729d3be 23.812 C
    print '{0} {1}: {2} {3} C'.format(date,hostname,sensor,temp)

    client = InfluxDBClient(host=influx_host, port=influx_port, database=influx_database, username=influx_username, password=influx_password)
    data = [
        {
            "measurement": "temp",
            "tags": {
                'device':hostname,
                'sensor':sensor,
		'location':location,
		'address':address
            },
            "fields": {
                'temp':temp
            }
        }
    ]
    client.write_points(data)

