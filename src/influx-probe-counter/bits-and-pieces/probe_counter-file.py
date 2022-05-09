#!/usr/bin/env python3
#
#
import sys
import argparse
import subprocess
import shlex
import influxdb_client
import pytz
from influxdb_client.client.write_api import SYNCHRONOUS
import uuid
import random
import time
import datetime
from collections import Counter

probe_batch = [] 
ssid_counter = Counter()
batch_size = 1
batch_counter = Counter()

bucket = "test"
org = "nottingham-u"

# this is just a random guid
token = "1oBltdsE3JdKcu4zOQQusNs0NxaQdv7zqn1ZCCAEeKioJ4niv_6hE43ow1Jx3kuDmlN-CjYYx_cHMFlhLEkUCQ=="
# Store the URL of your InfluxDB instance
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(
   url=url,
   precision = 'ns',
   token=token,
   org=org,
   debug=True
)


def unix_time_point(date_time):
    # make nanosecond time with date from clock (!) and time from probe
    #datetime.datetime(2020, 4, 20, 6, 30, tzinfo=datetime.timezone.utc), WritePrecision.S
    dt_obj = datetime.datetime.strptime(f'{datetime.datetime.now().date()} {date_time}','%Y-%m-%d %H:%M:%S.%f')
    nanoseconds = dt_obj.timestamp() * 1e09

    return nanoseconds



def invoke_process_popen_poll_live(command, client, shellType=False, stdoutType=subprocess.PIPE):
    """runs subprocess with Popen/poll so that live stdout is shown"""
    try:
        process = subprocess.Popen(
            shlex.split(command), shell=shellType, stdout=stdoutType)
    except:
        print("ERROR {} while running {}".format(sys.exc_info()[1], command))
        return None
    while True:
        output = process.stdout.readline()
        # used to check for empty output in Python2, but seems
        # to work with just poll in 2.7.12 and 3.5.2
        # if output == '' and process.poll() is not None:
        if process.poll() is not None:
            break
        if output:
            #print(output.strip().decode())
            formatted_output = output.strip().decode()
            probe_fields = formatted_output.split()
            batch_and_send(probe_fields, client)
    rc = process.poll()
    return rc


'''
Here's the probe response, split into fields

['10:08:24.983951',
 '1.0', 'Mb/s', '2437', 'MHz', '11b', '-96dBm', 
 'signal', 'antenna', '0', 'BSSID:Broadcast', 'DA:Broadcast', 'SA:76:7f:b8:55:73:62', 
 '(oui', 'Unknown)', 'Probe', 'Request', '()', 
 '[1.0', '2.0', '5.5', '11.0', '6.0', '9.0', '12.0', '18.0', 'Mbit]']
 
 
1 20:33:46.790369 -84dBm SA:5a:43:77:19:6c:6a
 
'''


# maybe we shouldn't have these globals, but...

def batch_and_send(probe_fields, client):
 
    global probe_batch
    global ssid_counter
    global batch_counter
        
    # change dBm to rough positive value, review later, dBm value is negative, from -90dBm to about -60dBm
    rssi = abs((100 + int(probe_fields[6].strip('dBm'))) * 10)

    # mockup location, but boxes at scale will need longitude/latitude as a management issue
    location = "51.52451563451121 -0.0731216997195253"
    
    # list of points into list for multiple asynchronous writes
    data = []
    nanoseconds = int(unix_time_point(probe_fields[0]))
    
    # don't need this, just a debug facility, watch input go in
    #time.sleep(1)

    # count discrete macs using a Python Counter
    ssid_counter[probe_fields[12]] += 1

    # count for batch size for writing
    batch_counter['count'] += 1
    
    # don't need this, just debug for data
    print(nanoseconds, probe_fields[0], rssi, probe_fields[12], ssid_counter[probe_fields[12]] )
    
    # make an Influx data point, why does only nanosecs work?
    p = influxdb_client.Point("probe").tag("location", location).field("signal", rssi).time(nanoseconds)

    # alternate version but need to anonymise probing mac, for example
    #p = influxdb_client.Point("probe").tag("mac", probe_fields[12]).tag("location", location).field("signal", rssi)

    # append the data point to the batch for writing
    probe_batch.append(p)
        
    # write it into the test bucket for nottingham-u organisation
    if (batch_counter['count'] >= batch_size):
		
		# maybe initialise this further up, is there an overhead? ask Influx folks?
        write_api = client.write_api(write_options=SYNCHRONOUS, precision='ns')
        
        # write the batch into the test bucket
        write_api.write(bucket='test', org='nottingham-u', record=probe_batch)
        
        # clear everything after writing
        batch_counter.clear()
        ssid_counter.clear()
        probe_batch = []

def main(argv):

    f = open("test-data.txt", "r")

    while(True):
		
	#read next line
        output = f.readline()
                
        #if line is empty, you are done with all lines in the file
        if not output:
            break

        formatted_output = output.strip()    
        probe_fields = formatted_output.split()
        batch_and_send(probe_fields, client)

	#you can access the line
        print(output.strip())

    #close file
        f.close


if __name__ == '__main__':
    main(sys.argv)
