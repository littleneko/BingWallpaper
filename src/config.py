#!/usr/bin/python3
# -*- coding: utf8 -*-

import configparser
import os.path


class Config(object):
    def __init__(self):
        self.database_dir = None
        self.download_dir = None
        self.file_log = False
        self.log_dir = None
        self.scan_interval_sec = 0

        self.notify_mail = None
        self.my_mail = None
        self.my_pass = None
        self.my_name = None
        self.server_chan_key = None

    def read_conf(self, config_file: str):
        cp = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(config_file)
        cp.read(config_file)
        self.database_dir = cp.get("base", "database_dir", fallback="database")
        self.download_dir = cp.get("base", "download_dir", fallback="bing")
        self.file_log = cp.getboolean("base", "file_log", fallback=False)
        self.log_dir = cp.get("base", "log_dir", fallback="log")
        self.scan_interval_sec = cp.getint("base", "scan_interval_sec", fallback=3600 * 6)
        self.notify_mail = cp.get("notify", "notify_mail")
        self.my_mail = cp.get("notify", "my_mail")
        self.my_pass = cp.get("notify", "my_pass")
        self.my_name = cp.get("notify", "my_name", fallback="Robot")
        self.server_chan_key = cp.get("notify", "server_chan_key")


def get_config(config_file: str) -> Config:
    conf = Config()
    conf.read_conf(config_file)
    return conf
