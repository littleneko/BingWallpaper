#!/usr/bin/python3
# -*- coding: utf8 -*-

import os.path
from configparser import ConfigParser


class Config(object):
    def __init__(self):
        self.database_dir = "database"
        self.download_dir = "bing"
        self.file_log = False
        self.log_dir = "log"
        self.scan_sec = 3600 * 6

        self.notify_mail = "example@163.com"
        self.my_mail = "example@qq.com"
        self.my_pass = "password"
        self.my_name = "Roboot"
        self.server_chan_sendkey = ""

    def read_conf(self, config_file: str):
        cp = ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(config_file)
        cp.read(config_file)
        self.database_dir = cp.get("base", "database_dir")
        self.download_dir = cp.get("base", "download_dir")
        self.file_log = cp.getboolean("base", "file_log")
        self.log_dir = cp.get("base", "log_dir")
        self.scan_sec = cp.getint("base", "scan_sec")
        self.notify_mail = cp.get("notify", "notify_mail")
        self.my_mail = cp.get("notify", "my_mail")
        self.my_pass = cp.get("notify", "my_pass")
        self.my_name = cp.get("notify", "my_name")
        self.server_chan_sendkey = cp.get("notify", "server_chan_sendkey")


conf = Config()
