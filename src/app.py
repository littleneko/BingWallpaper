# !/usr/bin/python3
# -*- coding: utf8 -*-

import argparse
import logging
import os
import time

from log import init_logging
from bing import BingDownloader
from notify import Notification
from env import env_default


def get_args():
    parser = argparse.ArgumentParser(
        description='A tool to download bing daily wallpaper.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    group1 = parser.add_argument_group('General Options')
    group1.add_argument('--storage-dir', default='storage', action=env_default('BING_STORAGE_DIR'),
                        help='directory to store database file, env: BING_STORAGE_DIR')
    group1.add_argument('--download-dir', default="download", action=env_default('BING_DOWNLOAD_DIR'),
                        help='directory to store image file, env: BING_DOWNLOAD_DIR')
    group1.add_argument('--download-timeout', default=5000, type=int, action=env_default('BING_DOWNLOAD_TIMEOUT'),
                        help='download timeout ms, env: BING_DOWNLOAD_TIMEOUT')
    group1.add_argument('--filelog', action="store_true", help='write log to file, otherwise to stdout')
    group1.add_argument('--log-dir', default="log", action=env_default('BING_LOG_DIR'),
                        help='directory to store log file if filelog is true, env: BING_LOG_DIR')
    group1.add_argument('--scan-interval', default=0, type=int, action=env_default('BING_SCAN_INTERVAL'),
                        help='every scan-interval seconds to get bing wallpaper, 0 means run once, '
                             'env: BING_SCAN_INTERVAL')

    group2 = parser.add_argument_group('Notify Options')
    group2.add_argument('--notify-mail', action=env_default('BING_NOTIFY_MAIL'),
                        help='email to notify when success or failed download, env: BING_NOTIFY_MAIL')
    group2.add_argument('--my-notify-mail', action=env_default('BING_MY_NOTIFY_MAIL'),
                        help='email to send notify email, env: BING_MY_NOTIFY_MAIL')
    group2.add_argument('--my-notify-pass', action=env_default('BING_MY_NOTIFY_PASS'),
                        help='my-email password or token, env: BING_MY_NOTIFY_PASS')
    group2.add_argument('--my-notify-name', default='Robot', action=env_default('BING_MY_NOTIFY_NAME'),
                        help='user name to send notify email, env: BING_MY_NOTIFY_NAME')
    group2.add_argument('--server-chan-key', action=env_default('BING_SERVER_CHAN_KEY'),
                        help='server-chan token to notify, env: BING_SERVER_CHAN_KEY')

    args = parser.parse_args()
    return args


def run():
    args = get_args()

    init_logging(args.filelog, args.log_dir)

    notify = None
    if args.notify_mail:
        if not args.my_notify_mail or not args.my_notify_pass:
            logging.error("args error, must specify my_notify_mail and my_notify_pass if you specified notify_mail")
            return
        notify = Notification(my_mail=args.my_notify_mail, my_password=args.my_notify_pass, to_mail=args.notify_mail,
                              server_chan_key=args.server_chan_key)

    if not os.path.exists(args.storage_dir):
        os.makedirs(args.storage_dir)
    db_file = os.path.join(args.storage_dir, "bing.db")

    bing_downloader = BingDownloader(db_file, args.download_dir, notify=notify,
                                     download_timeout_ms=args.download_timeout)
    bing_downloader.init_db()
    while True:
        bing_downloader.download()
        if args.scan_interval <= 0:
            break
        logging.info("wait for next round after %d second", args.scan_interval)
        try:
            time.sleep(args.scan_interval)
        except InterruptedError:
            break


if __name__ == '__main__':
    run()
