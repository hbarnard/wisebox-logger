#!/usr/bin/env python3.9

import ctypes
import io
import json
import os
import shlex
import signal
import struct
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, List, Union

import netifaces
import pytz
import requests
import tzlocal
from jsonargparse import ActionConfigFile, ArgumentParser
from scapy.all import sniff

DESCRIPTION = '802.11 probe request frame logger'
VERSION = '1.2.0'
API_VERSION = 1
LOGFILE_VERSION = 1


class Empty(object):
    def __getattr__(self, name):
        return lambda *args: None


class ExtArgumentParser(ArgumentParser):

    def check_config(
            self,
            cfg: Union[SimpleNamespace, dict],
            skip_none: bool = True,
            branch=None):
        import jsonargparse as ap
        cfg = ccfg = ap.deepcopy(cfg)
        if not isinstance(cfg, dict):
            cfg = ap.namespace_to_dict(cfg)
        if isinstance(branch, str):
            cfg = ap._flat_namespace_to_dict(
                ap._dict_to_flat_namespace({branch: cfg}))

        def get_key_value(dct, key):
            keys = key.split('.')
            for key in keys:
                dct = dct[key]
            return dct

        def check_required(cfg):
            for reqkey in self.required_args:
                try:
                    val = get_key_value(cfg, reqkey)
                    if val is None:
                        raise TypeError(f'Required key "{reqkey}" is None.')
                except:
                    raise TypeError(
                        f'Required key "{reqkey}" not included in config.')

        def check_values(cfg, base=None):
            subcommand = None
            for key, val in cfg.items():
                if key in ap.meta_keys:
                    continue
                kbase = key if base is None else base+'.'+key
                action = ap._find_action(self, kbase)
                if action is not None:
                    if val is None and skip_none:
                        continue
                    self._check_value_key(action, val, kbase, ccfg)
                    if (isinstance(action, ap.ActionSubCommands)
                            and kbase != action.dest):
                        if subcommand is not None:
                            raise KeyError(
                                f'Only values from a single sub-command '
                                f'are allowed ("{subcommand}", "{kbase}).')
                        subcommand = kbase
                elif isinstance(val, dict):
                    check_values(val, kbase)
                else:
                    pass

        try:
            check_required(cfg)
            check_values(cfg)
        except Exception as ex:
            self.error(f'Config checking failed :: {ex}')


class InactivityMonitor(threading.Thread):

    def __init__(self, config: object):
        super().__init__(daemon=True)
        self.condition = threading.Condition()
        self.config = config
        self.last_activity = datetime.now(tz=pytz.UTC)
        self.interval = timedelta(minutes=config.inactivity.interval)

    def _do_command(self):
        args = shlex.split(self.config.inactivity.action)
        subprocess.run(args)

    def run(self):
        while True:
            with self.condition:
                delta = datetime.now(tz=pytz.UTC) - self.last_activity
                if delta > self.interval:
                    self._do_command()
                self.condition.wait(60)

    def register_activity(self):
        self.last_activity = datetime.now(tz=pytz.UTC)


class Uploader(threading.Thread):

    def __init__(self, config: object):
        super().__init__(daemon=False)
        self.do_stop = False
        self.condition = threading.Condition()
        self.config = config

    def _do_upload(self) -> bool:
        success = True
        sep = '' if self.config.upload.url.endswith('/') else '/'
        url = f'{self.config.upload.url}{sep}api/v{API_VERSION}/upload'
        params = {'api_key': self.config.upload.api_key}
        headers = {'Content-Type': 'application/octet-stream'}
        log_dir = Path(self.config.log.dir)
        for f in log_dir.glob('wp*.complete'):
            try:
                r = requests.post(
                    url,
                    data=f.read_bytes(),
                    params=params,
                    headers=headers)
                if r.status_code != 200:
                    raise Exception()
                if self.config.upload.keep_logs:
                    f.rename(Path(f.parent, f'{f.stem}.uploaded'))
                else:
                    f.unlink()
            except:
                success = False
        return success

    def run(self):
        while not self.do_stop:
            with self.condition:
                if self._do_upload():
                    self.condition.wait()
                else:
                    self.condition.wait(
                        timeout=(self.config.upload.retry_interval * 60))

    def stop(self):
        with self.condition:
            self.do_stop = True
            self.condition.notify()

    def wakeup(self):
        with self.condition:
            self.condition.notify()


class Header():

    def __init__(self, mac: str, config: object, timezone: str):
        ENCODING = 'utf_8'
        buf = io.BytesIO()
        buf.write(struct.pack('<H', LOGFILE_VERSION))
        for x in mac.split(':'):
            buf.write(struct.pack('<B', int(x, base=16)))
        buf.write(struct.pack('<I', config.bucket.interval))
        tz = timezone.encode(ENCODING)
        buf.write(struct.pack('<B', len(tz)))
        buf.write(tz)
        metadata = json.dumps({
            'filters.rssi.min': config.filters.rssi.min
        }).encode(ENCODING)
        buf.write(struct.pack('<I', len(metadata)))
        buf.write(metadata)
        self.__bytes = buf.getvalue()

    def get_bytes(self):
        return self.__bytes


class Bucket():

    def __init__(self, starttime: datetime, interval: timedelta):
        self.__starttime = starttime
        self.__interval = interval
        self.__endtime = starttime + interval
        self.__elements = dict()
        self.__frequency = 0

    def add(self, mac: str, rssi: int, frequency: int):
        if mac not in self.__elements or rssi > self.__elements[mac]:
            self.__elements[mac] = rssi
            self.__frequency = frequency

    def size(self):
        return len(self.__elements)

    def should_close(self, timestamp: datetime):
        return timestamp >= self.__endtime

    def find_bucket_for(self, timestamp: datetime):
        if timestamp < self.__endtime:
            raise Exception('timestamp must be after this bucket\'s end time')
        start = self.__starttime
        while True:
            start += self.__interval
            if (start + self.__interval) > timestamp:
                return Bucket(start, self.__interval)

    def __str__(self):
        return f'{self.__starttime}<{self.__interval}>: {len(self.__elements)}'

    def get_bytes(self):
        count = len(self.__elements)
        buf = bytearray(8 + count)
        struct.pack_into(
            '<iHH',
            buf,
            0,
            int(self.__starttime.timestamp()),
            self.__frequency,
            count)
        i = 8
        for rssi in self.__elements.values():
            struct.pack_into('<b', buf, i, rssi)
            i += 1
        return bytes(buf)


class FileWriter():

    def __init__(
            self,
            log_dir: str,
            starttime: datetime,
            interval: timedelta,
            header: Header):
        self.__log_dir = log_dir
        self.__starttime = starttime
        self.__interval = interval
        self.__header = header
        self.__endtime = starttime + interval
        os.makedirs(log_dir, exist_ok=True)
        start = starttime.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S')
        self.__path = Path(log_dir, f'wp{start}.part')
        self.__file = self.__path.open(mode='wb', buffering=0)
        self.__file.write(header.get_bytes())

    def should_rollover(self, timestamp: datetime):
        return timestamp >= self.__endtime

    def close(self):
        if not self.__file.closed:
            self.__file.close()
        self.__path.rename(self.__path.with_suffix('.complete'))

    def write(self, bucket: Bucket):
        if self.__file.closed:
            self.__file = self.__path.open(mode='wb', buffering=0)
        self.__file.write(bucket.get_bytes())

    def find_writer_for(self, timestamp: datetime):
        if timestamp < self.__endtime:
            raise Exception(
                'timestamp must be after this file writer\'s end time')
        start = self.__starttime
        while True:
            start += self.__interval
            if (start + self.__interval) > timestamp:
                return FileWriter(
                    self.__log_dir, start, self.__interval, self.__header)


class WISEBoxLogger():

    def __init__(
            self,
            config,
            starttime: datetime,
            mac: str,
            timezone: datetime.tzinfo,
            rollover_actions: List[Callable[[], None]] = [],
            log_actions: List[Callable[[], None]] = []):
        self.__config = config
        self.__bucket = Bucket(starttime, timedelta(
            minutes=config.bucket.interval))
        header = Header(mac, config, str(timezone))
        self.__filewriter = FileWriter(
            config.log.dir,
            starttime,
            timedelta(minutes=config.log.rollover.time),
            header)
        self.rollover_actions = rollover_actions
        self.log_actions = log_actions

    def write(self, timestamp: datetime):
        if self.__filewriter.should_rollover(timestamp):
            self.__filewriter.close()
            self.__filewriter = self.__filewriter.find_writer_for(timestamp)
            for action in self.rollover_actions:
                action()
        self.__filewriter.write(self.__bucket)

    def log(self, timestamp: datetime, mac: str, rssi: int, frequency: int):
        if self.__bucket.should_close(timestamp):
            self.write(timestamp)
            self.__bucket = self.__bucket.find_bucket_for(timestamp)
        if (self.__config.filters.rssi.min is None or
                rssi >= self.__config.filters.rssi.min):
            self.__bucket.add(mac, rssi, frequency)
        for action in self.log_actions:
            action()

    def close(self):
        self.__filewriter.close()


def build_packet_callback(logger: WISEBoxLogger):
    def packet_callback(packet):
        try:
            freq = packet.ChannelFrequency
        except:
            freq = None
        if not freq or freq < 0:
            freq = 0
        logger.log(
            datetime.fromtimestamp(packet.time, tz=pytz.UTC),
            packet.addr2,
            packet.dBm_AntSignal,
            freq)
    return packet_callback


def find_incomplete_logs(config):
    d = Path(config.log.dir)
    if d.exists() and d.is_dir():
        for f in d.glob('*.part'):
            f.rename(f.with_suffix('.complete'))


def main():
    app = Path(sys.argv[0]).stem

    parser = ExtArgumentParser(
        prog=app,
        default_config_files=[],
        description=DESCRIPTION,
        error_handler='usage_and_exit_error_handler')

    parser.add_argument(
        'interface',
        type=str,
        help='capture interface, e.g. wlan0')
    parser.add_argument(
        'channel',
        type=int,
        help='channel number to listen on')
    parser.add_argument(
        'log.dir',
        type=str,
        help='directory to write logs to')
    parser.add_argument(
        '--bucket.interval',
        type=int,
        default=5,
        help='bucket interval time in minutes')
    parser.add_argument(
        '--log.rollover.time',
        type=int,
        default=60,
        help='time, in minutes, between log file rollover')
    parser.add_argument(
        '--filters.rssi.min',
        type=int,
        help='RSSI minimum filter level')
    parser.add_argument(
        '--upload.enabled',
        type=bool,
        default=False,
        help='enable upload of logs')
    parser.add_argument(
        '--upload.url',
        type=str,
        help='server url to upload logs to')
    parser.add_argument(
        '--upload.api_key',
        type=str,
        help='api key to use to authenticate with server')
    parser.add_argument(
        '--upload.retry_interval',
        type=int,
        default=10,
        help='time, in minutes, to retry failed uploads')
    parser.add_argument(
        '--upload.keep_logs',
        type=bool,
        default=True,
        help='whether to keep uploaded logs or to delete after upload')
    parser.add_argument(
        '--inactivity.enabled',
        type=bool,
        default=False,
        help='whether to monitor for inactivity and take an action')
    parser.add_argument(
        '--inactivity.interval',
        type=int,
        default=60,
        help='inactivity time interval in minutes, after which action is taken')
    parser.add_argument(
        '--inactivity.action',
        type=str,
        default='/bin/true',
        help='action (command) to be taken after inactivity interval elapsed')
    parser.add_argument('--config', action=ActionConfigFile)
    parser.add_argument(
        '--version',
        action='version',
        version=f'{app} version {VERSION}')

    cfg = parser.parse_args()

    startup_tasks = [find_incomplete_logs]
    for task in startup_tasks:
        task(cfg)

    try:
        iface = netifaces.ifaddresses(cfg.interface)
        mac = iface[netifaces.AF_LINK][0]['addr']
    except KeyError:
        mac = '00:00:00:00:00:00'

    if cfg.upload.enabled:
        uploader = Uploader(cfg)
        uploader.start()
        rollover_actions = [uploader.wakeup]
    else:
        uploader = Empty()
        rollover_actions = []

    if cfg.inactivity.enabled:
        inactivity_monitor = InactivityMonitor(cfg)
        inactivity_monitor.start()
        log_actions = [inactivity_monitor.register_activity]
    else:
        log_actions = []

    logger = WISEBoxLogger(
        cfg, datetime.now(
            tz=pytz.UTC),
            mac,
            tzlocal.get_localzone(),
            rollover_actions=rollover_actions,
            log_actions=log_actions)

    def handler(signum, frame):
        uploader.stop()
        logger.close()
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, handler)
    packet_cb = build_packet_callback(logger)
    sniff(
        iface=cfg.interface,
        prn=packet_cb,
        store=0,
        filter='type mgt subtype probe-req')
    uploader.stop()
    logger.close()


if __name__ == '__main__':
    main()
