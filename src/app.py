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
        description='A tool to download bing daily wallpaper.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    gen_group = parser.add_argument_group('General Options')
    gen_group.add_argument('--server-mode', action='store_true',
                           help='run as server and scan new wallpaper cyclically, otherwise only run once')
    gen_group.add_argument('--scan-interval', default=3600, type=int, action=env_default('BING_SCAN_INTERVAL'),
                           help='seconds to check new wallpaper if run in server mode, env: BING_SCAN_INTERVAL')

    gen_group.add_argument('--log-type', default='stdout', choices=['stdout', 'file'],
                           action=env_default('BING_LOG_TYPE'),
                           help='write log to file or stdout, env: BING_LOG_TYPE')
    gen_group.add_argument('--log-path', default="log", action=env_default('BING_LOG_PATH'),
                           help='location for log file if filelog is true, env: BING_LOG_PATH')
    gen_group.add_argument('--log-level', default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                           action=env_default('BING_LOG_LEVEL'),
                           help='location for log file if filelog is true, env: BING_LOG_LEVEL')
    gen_group.add_argument('--storage-type', default='SQLITE', choices=list(StorageType),
                           type=StorageType, action=env_default('BING_STORAGE_TYPE'),
                           help='how to store wall paper info and check wallpaper exist, NONE for no check, '
                                'env: BING_STORAGE_TYPE')
    gen_group.add_argument('--storage-path', default='storage', action=env_default('BING_STORAGE_PATH'),
                           help='location for sqlite database files, env: BING_STORAGE_PATH')
    gen_group.add_argument('--download-path', default="download", action=env_default('BING_DOWNLOAD_PATH'),
                           help='location for downloaded image files, env: BING_DOWNLOAD_PATH')
    gen_group.add_argument('--download-timeout', default=5000, type=int, action=env_default('BING_DOWNLOAD_TIMEOUT'),
                           help='download timeout millisecond, env: BING_DOWNLOAD_TIMEOUT')
    gen_group.add_argument('--retries', default=3, type=int, action=env_default('BING_RETRIES'),
                           help='times to retry when failed to download, env: BING_RETRIES')

    bing_group = parser.add_argument_group('Bing Options')
    bing_group.add_argument('--zone', default='CN', choices=['CN', 'EN'], action=env_default('BING_ZONE'),
                            help='where to download wallpaper, env: BING_ZONE')
    bing_group.add_argument('--count', default=8, type=int, choices=range(1, 9), action=env_default('BING_COUNT'),
                            help='how many wallpaper to download, env: BING_COUNT')

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

    init_logging(args.log_type, args.log_path, args.log_level)

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

    en_search = False if args.zone == 'CN' else True
    bing_downloader = BingWallpaperDownloader(en_search=en_search,
                                              download_cnt=args.count,
                                              download_path=args.download_path,
                                              max_retries=args.retries,
                                              download_timeout_ms=args.download_timeout,
                                              notify=notify,
                                              wallpaper_mgr=wallpaper_mgr)

    while True:
        bing_downloader.download()
        if not args.server_mode: break
        logging.info("wait for next round after %d second", args.scan_interval)
        try:
            time.sleep(args.scan_interval)
        except InterruptedError:
            break


if __name__ == '__main__':
    run()
