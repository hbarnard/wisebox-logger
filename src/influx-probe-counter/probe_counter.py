#!/usr/bin/env python3
#
#FIXME: surely some of these aren't needed?
import sys
import argparse
import subprocess
import shlex
# maybe we don't need both of these?
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
# not used yet, convert macs into random guids, but still 1:1?
import uuid
import random
import time
import datetime
import json
import math
import csv

# this changes lat,lon to s2 cells for influxdb see: https://www.influxdata.com/blog/exploring-geo-temporal-flux/
import s2cell

from collections import Counter

ssid_counter = Counter()
batch_counter = Counter()
probe_batch = [] 
start_seconds = 0
locations = []

# should path be hardcoded? 
# json used rather than ini, since easier for api later on
def read_config():
    with open('/etc/wisebox/config.json', 'r') as f:
        return json.load(f)

# generate randoms round a centre, not used currently
def generate_random_latlon (lat, lon):
    hex1 = '%012x' % random.randrange(16**12)                
    flt = float(random.randint(0,100))
    lon = float(lon) + random.random()/100 
    lat = float(lat) + random.random()/100
    ###print (lat,lon)
    return (str(lat), str(lon) )


# list of 'constant' fake locations centered round the Nottingham campus
def read_fake_locations():
    locations = []
    with open('/etc/wisebox/locations.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            locations.append([row[0],row[1]])
    return locations

def unix_time_point(date_time):
    # make nanosecond time with date from clock (!) and time from probe
    #datetime.datetime(2020, 4, 20, 6, 30, tzinfo=datetime.timezone.utc), WritePrecision.S
    dt_obj = datetime.datetime.strptime(f'{datetime.datetime.now().date()} {date_time}','%Y-%m-%d %H:%M:%S.%f')

    return dt_obj.timestamp()


def invoke_process_popen_poll_live(command, client, config, locations, shellType=False, stdoutType=subprocess.PIPE):
    """runs subprocess with Popen/poll so that live stdout is shown"""
    try:
        process = subprocess.Popen(
            shlex.split(command), shell=shellType, stdout=stdoutType)
    except:
        print("ERROR {} while running {}".format(sys.exc_info()[1], command))
        return None
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            formatted_output = output.strip().decode()
            probe_fields = formatted_output.split()
            batch_and_send(probe_fields, client, config, locations)
    rc = process.poll()
    return rc
    
'''
['10:08:24.983951',
 '1.0', 'Mb/s', '2437', 'MHz', '11b', '-96dBm', 
 'signal', 'antenna', '0', 'BSSID:Broadcast', 'DA:Broadcast', 'SA:76:7f:b8:55:73:62', 
 '(oui', 'Unknown)', 'Probe', 'Request', '()', 
 '[1.0', '2.0', '5.5', '11.0', '6.0', '9.0', '12.0', '18.0', 'Mbit]']
 
1 20:33:46.790369 -84dBm SA:5a:43:77:19:6c:6a
'''

def batch_and_send(probe_fields, client, config, locations):
     
    global probe_batch  
    global start_seconds 

    # change dBm to rough positive value, review later, actual dBm value is negative, from -90dBm to about -60dBm
    rssi = abs((100 + int(probe_fields[6].strip('dBm'))) * 10)
    #print("rssi is", probe_fields[6], rssi)
    
    # this uses the clock time from probe, not Pi (or other) clock
    #FIXME: currently only nanoseconds works, ask influx folks
    nanoseconds = int(unix_time_point(probe_fields[0]) * 1e09)
    
    #print("nanoseconds are ",nanoseconds)
    
    #FIXME: don't need this, just a debug facility, watch input go in
    if (config['wisebox_delay'] > 0):
        time.sleep(config['wisebox_delay'])

    # count discrete macs using a Python Counter
    ssid_counter[probe_fields[12]] += 1

    # count for batch size for writing
    batch_counter['count'] += 1
    
    #FIXME: this should come from box configuration in a 'real' setting    
    #(lat,lon) = generate_random_latlon (config['lat'], config['lon'])
    (lat,lon) = random.choice(locations)
    ###print(lat,lon)
    
    #FIXME: need to anonymise probing mac, guid or hash?
    #FIXME: s2_cell_id possible, but leaflet.js not keen, so lat,lon
    p = influxdb_client.Point("probe").tag("lat", lat).tag("lon", lon).tag("mac", probe_fields[12]).field("signal", rssi).time(nanoseconds)

    # have a look at p
    print("line protocol point is ", p)

    # append the data point to the batch for writing
    probe_batch.append(p)
    
    # calculate elapsed in seconds    
    now_seconds = int(datetime.datetime.now().timestamp())
    elapsed_seconds = now_seconds - start_seconds
    
    #FIXME: think about batching up/downsampling etc. write it into the test bucket for nottingham-u organisation
    if ((batch_counter['count'] >= config['batch_size']) or (elapsed_seconds >= config['wisebox_interval'])):
        
        # maybe initialise this further up, is there an overhead? ask Influx folks?
        write_api = client.write_api(write_options=SYNCHRONOUS, precision=config['influx_precision'])
        # write the batch into the test bucket
        write_api.write(bucket=config['influx_bucket'], org=config['influx_org'], record=probe_batch)
        
        # clear everything after writing
        batch_counter.clear()
        ssid_counter.clear()
        probe_batch = []
        # reset batching clock
        start_seconds = now_seconds
        
def main(argv):
    
    config = read_config()
    client = influxdb_client.InfluxDBClient.from_config_file("/etc/wisebox/influx.ini")
    
    #FIXME: only do this *once* when live
    #[config['lat'], config['lon']] = config['wisebox_location'].split(',')
    
    # list of fake locations centered around the campus
    locations = read_fake_locations()
    
    #FIXME: not going to use s2 for the moment, Influxdb not ready, using leaflet.js
    #config['s2_cell_id'] = s2cell.lat_lon_to_token(float(lat), float(lon))
    
    start_seconds = int(datetime.datetime.now().timestamp())

    while True:        
        # I've left the command input here rather than within config, makes things clearer
        invoke_process_popen_poll_live(config['wisebox_command'], client, config, locations)

if __name__ == '__main__':
    main(sys.argv)
