#!/usr/bin/env python3

import io
import os
import struct
import sys
import zipfile
import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Union

import netifaces
import pytz
#import web
from jsonargparse import ActionConfigFile, ArgumentParser
import json
import glob
import time

import influxdb_client


from influxdb_client.client.write_api import SYNCHRONOUS
from fastapi import Depends, FastAPI, HTTPException, Request




VERSION = '1.0'
DESCRIPTION ='Compressed Log Files to InfluxDb'


# should path be hardcoded? 
# json used rather than ini, since easier for api later on
def read_config():
    with open('/etc/wisebox/config.json', 'r') as f:
        return json.load(f)


def batch_and_send(logfile, client, config):
     
    content = Logfile()
    probe_batch = []
    (startdate,status,entries,header) = content.GET(logfile)
    for entry in entries:
        nanoseconds = int(entry[0].timestamp()) 
        # lat and lon can come out of remote box or database?
        # database is probably simpler?
        p = influxdb_client.Point("probe").tag("lat", header['lat']).tag("lon", header['lon']) .field("count", entry[2]).time(nanoseconds)
        # have a look at p
        print("line protocol point is ", p)
        time.sleep(config['wisebox_delay'])
        # append the data point to the batch for writing
        probe_batch.append(p)
    
        # maybe initialise this further up, is there an overhead? ask Influx folks?
    #write_api = client.write_api(write_options=SYNCHRONOUS, precision=config['influx_precision'])
    # write the batch into the test bucket
    #write_api.write(bucket=config['influx_bucket'], org=config['influx_org'], record=probe_batch)
    return

class Index:
    def GET(self):
        d = Path("/home/pi/projects/wisebox-logfile-server/data/wisebox")
        log_files = list()
        for f in d.glob('wp*'):
            dt = datetime.datetime.strptime(f.stem.replace(
                'wp', ''), '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)
            log_files.append((f.name, dt, f.suffix.replace('.', '')))
        return log_files


class Logfile:

    def decode_head(self, i, buf):
        ENCODING = 'utf_8'
        header = dict()
        header['logfile_version'] = struct.unpack_from('<H', buf, i)[0]
        i += 2
        mac_bytes = struct.unpack_from('<BBBBBB', buf, i)
        header['mac'] = ':'.join([f'{x:02x}' for x in mac_bytes])
        i += 6
        header['interval'] = struct.unpack_from('<I', buf, i)[0]
        i += 4
        tz_len = struct.unpack_from('<B', buf, i)[0]
        i += 1
        header['timezone'] = buf[i:i+tz_len].decode(ENCODING)
        i += tz_len
        metadata_len = struct.unpack_from('<I', buf, i)[0]
        i += 4
        metadata = buf[i:i+metadata_len].decode(ENCODING)
        i += metadata_len
        header['metadata'] = metadata
        return i, header

    def decode_body(self, i, buf):
        entries = list()
        while i < len(buf):
            (a, b, c) = struct.unpack_from('<iHH', buf, i)
            st = datetime.datetime.fromtimestamp(a, tz=pytz.UTC)
            i += 8
            j = i + c
            rssis = []
            while i < j:
                (rssi, ) = struct.unpack_from('<b', buf, i)
                i += 1
                rssis.append(rssi)
            entries.append((st, b, c, rssis))
        return i, entries

    def GET(self, filename):
        f = Path("/home/pi/projects/wisebox-logfile-server/data/wisebox", filename)
        startdate = datetime.datetime.strptime(f.stem.replace(
            'wp', ''), '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)
        with f.open('rb') as bf:
            buf = bf.read()
        i = 0
        i, header = self.decode_head(i, buf)
        i, entries = self.decode_body(i, buf)
        return (
            startdate,
            f.suffix.replace('.', ''),
            entries,
            header,
            )

'''
2022-02-16 08:54:53+00:00 complete {'logfile_version': 1, 'mac': '00:11:3b:13:1a:9c', 'interval': 5, 'timezone': 'Europe/London', 'metadata': '{"filters.rssi.min": null}'}
(datetime.datetime(2022, 2, 16, 8, 49, 53, tzinfo=<UTC>), 2437, 8, [-73, -70, -69, -60, -76, -71, -46, -79])
(datetime.datetime(2022, 2, 16, 8, 54, 53, tzinfo=<UTC>), 2437, 17, [-71, -62, -71, -71, -70, -63, -61, -69, -66, -68, -62, -75, -73, -70, -71, -76, -76])
(datetime.datetime(2022, 2, 16, 8, 59, 53, tzinfo=<UTC>), 2437, 5, [-73, -67, -75, -77, -46])
(datetime.datetime(2022, 2, 16, 9, 4, 53, tzinfo=<UTC>), 2437, 11, [-75, -69, -68, -75, -78, -75, -73, -69, -73, -73, -69])
(datetime.datetime(2022, 2, 16, 9, 9, 53, tzinfo=<UTC>), 2437, 22, [-66, -67, -66, -77, -72, -66, -66, -63, -59, -76, -75, -72, -70, -70, -71, -72, -67, -74, -72, -63, -60, -46])
(datetime.datetime(2022, 2, 16, 9, 14, 53, tzinfo=<UTC>), 2437, 8, [-70, -67, -68, -75, -75, -70, -66, -73])
(datetime.datetime(2022, 2, 16, 9, 19, 53, tzinfo=<UTC>), 2437, 11, [-75, -71, -59, -66, -70, -66, -76, -75, -74, -45, -59])
(datetime.datetime(2022, 2, 16, 9, 24, 53, tzinfo=<UTC>), 2437, 13, [-71, -71, -73, -63, -49, -60, -74, -67, -76, -72, -72, -70, -71])
(datetime.datetime(2022, 2, 16, 9, 29, 53, tzinfo=<UTC>), 2437, 15, [-60, -63, -73, -75, -73, -76, -78, -66, -75, -63, -75, -74, -45, -74, -72])
(datetime.datetime(2022, 2, 16, 9, 34, 53, tzinfo=<UTC>), 2437, 23, [-59, -66, -63, -65, -74, -73, -77, -78, -68, -73, -65, -66, -71, -69, -66, -72, -71, -73, -74, -73, -77, -67, -75])
(datetime.datetime(2022, 2, 16, 9, 39, 53, tzinfo=<UTC>), 2437, 9, [-71, -73, -60, -65, -74, -63, -76, -78, -43])
(datetime.datetime(2022, 2, 16, 9, 44, 53, tzinfo=<UTC>), 2437, 14, [-79, -74, -79, -75, -74, -73, -67, -71, -74, -66, -62, -77, -71, -62])
'''


def main():
 
    config = read_config()
    client = influxdb_client.InfluxDBClient.from_config_file("/etc/wisebox/influx.ini")
    
    # only do this *once*
    [lat, lon] = config['wisebox_location'].split(',')
    config['s2_cell_id'] = s2cell.lat_lon_to_token(float(lat), float(lon))
    
    start_seconds = int(datetime.datetime.now().timestamp())

    index = Index()       
    log_files = index.GET()
    #print(log_files)
    for log_files[1] in (log_files):
         batch_and_send(log_files[1][0], client, config)
  
            
if __name__ == "__main__":
    main()
