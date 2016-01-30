#!/usr/bin/python
import glob
import os
import subprocess
import time
from influxdb import InfluxDBClient

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

    client = InfluxDBClient(host='109.204.153.237', port=8086, database='Temperatures')
    data = [
        {
            "measurement": "temp",
            "tags": {
                'device':hostname,
                'sensor':sensor
            },
            "fields": {
                'temp':temp
            }
        }
    ]
    client.write_points(data)

