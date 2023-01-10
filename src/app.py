# !/usr/bin/python3
# -*- coding: utf8 -*-

import argparse
import logging
import os
import time

from log import init_logging
from bing_downloader import BingWallpaperDownloader, SqliteBingWallpaperManager, NoBingWallpaperManager, StorageType
from notify import Notification
from env import env_default


def get_args():
    parser = argparse.ArgumentParser(
        prog='bing-dl',
        description='A tool to download bing daily wallpaper.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    gen_group = parser.add_argument_group('General Options')
    gen_group.add_argument('--service-mode', action='store_true',
                           help='Run as service and periodically scan new wallpaper, otherwise only run once')
    gen_group.add_argument('--scan-interval', default=3600, type=int, action=env_default('BING_SCAN_INTERVAL'),
                           help='Check new wallpaper every scan-interval millisecond if run in server mode, '
                                'env: BING_SCAN_INTERVAL')
    gen_group.add_argument('--log-path', action=env_default('BING_LOG_PATH'),
                           help='Location for log file, default is stdout, env: BING_LOG_PATH')
    gen_group.add_argument('--log-level', default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                           action=env_default('BING_LOG_LEVEL'), help='Log level, env: BING_LOG_LEVEL')
    gen_group.add_argument('--storage-type', default='SQLITE', choices=list(StorageType),
                           type=StorageType, action=env_default('BING_STORAGE_TYPE'),
                           help='The way to store wallpaper info and check exist, NONE means not store and not check, '
                                'env: BING_STORAGE_TYPE')
    gen_group.add_argument('--storage-path', default='storage', action=env_default('BING_STORAGE_PATH'),
                           help='Location for database files if storage-type is not NONE, env: BING_STORAGE_PATH')
    gen_group.add_argument('--download-path', default="download", action=env_default('BING_DOWNLOAD_PATH'),
                           help='Location for downloaded wallpaper files, env: BING_DOWNLOAD_PATH')
    gen_group.add_argument('--download-timeout', default=5000, type=int, action=env_default('BING_DOWNLOAD_TIMEOUT'),
                           help='Download timeout millisecond, env: BING_DOWNLOAD_TIMEOUT')
    gen_group.add_argument('--max-retries', default=3, type=int, action=env_default('BING_MAX_RETRIES'),
                           help='Times to retry when failed to download, env: BING_MAX_RETRIES')
    gen_group.add_argument('--retry-backoff', default=1000, type=int, action=env_default('BING_RETRY_BACKOFF'),
                           help='Backoff time millisecond to retry if failed, env: BING_RETRY_BACKOFF')

    bing_group = parser.add_argument_group('Bing Options')
    bing_group.add_argument('--search-zone', default='CN', choices=['CN', 'EN'], action=env_default('BING_SEARCH_ZONE'),
                            help='Search in bing china or international web site, env: BING_SEARCH_ZONE')
    bing_group.add_argument('--day-offset', default=0, type=int, choices=range(0, 8),
                            action=env_default('BING_DAY_OFFSET'),
                            help='The num days before today start to get, env: BING_DAY_OFFSET')
    bing_group.add_argument('--day-count', default=8, type=int, choices=range(1, 9),
                            action=env_default('BING_DAY_COUNT'),
                            help='The bing API can get up to 8 days of wallpaper before today, env: BING_DAY_COUNT')

    notify_group = parser.add_argument_group('Notify Options')
    notify_group.add_argument('--notify-mail', action=env_default('BING_NOTIFY_MAIL'),
                              help='send email to this address after download, env: BING_NOTIFY_MAIL')
    notify_group.add_argument('--notify-user-mail', action=env_default('BING_NOTIFY_USER_MAIL'),
                              help='email to send notify email, env: BING_NOTIFY_USER_MAIL')
    notify_group.add_argument('--notify-user-pass', action=env_default('BING_NOTIFY_USER_PASS'),
                              help='notify user email password or token, env: BING_NOTIFY_USER_PASS')
    notify_group.add_argument('--notify-user-name', default='Robot', action=env_default('BING_NOTIFY_USER_NAME'),
                              help='notify user name to send email, env: BING_NOTIFY_USER_NAME')
    notify_group.add_argument('--server-chan-key', action=env_default('BING_SERVER_CHAN_KEY'),
                              help='server-chan token to notify, env: BING_SERVER_CHAN_KEY')

    args = parser.parse_args()
    return args


def run():
    args = get_args()

    init_logging(args.log_path, args.log_level)

    notify = None
    if args.notify_mail:
        if not args.notify_user_mail or not args.notify_user_pass:
            logging.error("args error, must specify notify_user_mail and notify_user_pass if you specified notify_mail")
            return
        notify = Notification(my_mail=args.notify_user_mail, my_password=args.notify_user_pass,
                              my_name=args.notify_user_name, to_mail=args.notify_mail,
                              server_chan_key=args.server_chan_key)

    if args.storage_type == StorageType.SQLITE:
        if not os.path.exists(args.storage_path):
            os.makedirs(args.storage_path)
        db_file = os.path.join(args.storage_path, "bing.db")
        wallpaper_mgr = SqliteBingWallpaperManager(db_file)
        wallpaper_mgr.init_db()
    else:
        wallpaper_mgr = NoBingWallpaperManager()

    en_search = False if args.search_zone == 'CN' else True
    bing_downloader = BingWallpaperDownloader(en_search=en_search,
                                              download_offset=args.day_offset,
                                              download_cnt=args.day_count,
                                              download_path=args.download_path,
                                              max_retries=args.max_retries,
                                              retry_backoff_ms=args.retry_backoff,
                                              download_timeout_ms=args.download_timeout,
                                              notify=notify,
                                              wallpaper_mgr=wallpaper_mgr)

    while True:
        bing_downloader.download()
        if not args.service_mode: break

        logging.info("wait for next round after %d second", args.scan_interval)
        try:
            time.sleep(args.scan_interval)
        except InterruptedError:
            break


if __name__ == '__main__':
    run()
