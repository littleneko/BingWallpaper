# !/usr/bin/python3
# -*- coding: utf8 -*-

import argparse
import logging
import os
import time

from log import init_logging
from config import get_config
from bing import BingDownloader
from notify import Notification

parser = argparse.ArgumentParser(description='bing-dl')
parser.add_argument('--config', '-c', default="config/bing.ini", help='config file name')
parser.add_argument('--clean-db', action='store_true', help='clean the bing wallpaper database')


def run():
    args = parser.parse_args()

    conf = get_config(args.config)
    init_logging(conf.file_log, conf.log_dir)

    notify = None
    if conf.notify_mail is not None:
        notify = Notification(conf.my_mail, conf.my_pass, conf.notify_mail, conf.server_chan_key)

    if not os.path.exists(conf.database_dir):
        os.makedirs(conf.database_dir)
    db_file = os.path.join(conf.database_dir, "bing.db")

    bing_downloader = BingDownloader(db_file, conf.download_dir, notify=notify)
    if args.clean_db:
        bing_downloader.clean_db()

    bing_downloader.init_db()
    while True:
        bing_downloader.download()
        if conf.scan_interval_sec <= 0:
            break
        logging.info("wait for next round after %d second", conf.scan_interval_sec)
        try:
            time.sleep(conf.scan_interval_sec)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    run()
