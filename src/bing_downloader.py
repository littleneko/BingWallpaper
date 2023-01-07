#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import os
import re
import sqlite3
from abc import ABCMeta, abstractmethod
from enum import Enum, auto

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from bing_client import BingWallpaperInfo, BingWallpaperClient
from notify import Notification


class StorageType(Enum):
    NONE = 'NONE'
    SQLITE = 'SQLITE'

    def __str__(self):
        return self.value


class BingWallpaperManager(metaclass=ABCMeta):
    @abstractmethod
    def init_db(self):
        pass

    @abstractmethod
    def clean_db(self):
        pass

    @abstractmethod
    def wallpaper_exist(self, hsh: str) -> bool:
        pass

    @abstractmethod
    def save_wallpaper_info(self, wallpaper_info: BingWallpaperInfo):
        pass


class NoBingWallpaperManager(BingWallpaperManager):
    def init_db(self):
        pass

    def clean_db(self):
        pass

    def wallpaper_exist(self, hsh: str) -> bool:
        return False

    def save_wallpaper_info(self, wallpaper_info: BingWallpaperInfo):
        pass


class SqliteBingWallpaperManager(BingWallpaperManager):
    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS `bing.bing` (
            `id` INTEGER PRIMARY KEY,
            `date` varchar(16) NOT NULL DEFAULT '',
            `url` varchar(255) NOT NULL DEFAULT '',
            `copyright` text NOT NULL DEFAULT '',
            `hsh` varchar(64) NOT NULL DEFAULT '' UNIQUE,
            `zone` varchar(8) NOT NULL DEFAULT 'cn',
            `detail` text DEFAULT '',
            `_create_time` datetime DEFAULT CURRENT_TIMESTAMP,
            `_update_time` datetime DEFAULT CURRENT_TIMESTAMP
        )"""

    CHECK_HSH_SQL = "SELECT `hsh`, `url` from `bing.bing` WHERE `hsh` = ? LIMIT 1"
    INSERT_IMG_SQL = "REPLACE INTO `bing.bing` VALUES(NULL, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
    CLEAN_DB_SQL = "DELETE FROM `bing.bing`"

    def __init__(self, sqlite_file: str):
        self._sqlite_file = sqlite_file
        self._db_conn = sqlite3.connect(self._sqlite_file)

    def init_db(self):
        conn = sqlite3.connect(self._sqlite_file)
        cur = conn.cursor()
        cur.execute(SqliteBingWallpaperManager.CREATE_TABLE_SQL)
        conn.close()

    def clean_db(self):
        if not os.path.exists(self._sqlite_file):
            return
        conn = sqlite3.connect(self._sqlite_file)
        cur = conn.cursor()
        cur.execute(SqliteBingWallpaperManager.CLEAN_DB_SQL)
        conn.close()

    def wallpaper_exist(self, hsh: str) -> bool:
        cur = self._db_conn.cursor()
        res = cur.execute(SqliteBingWallpaperManager.CHECK_HSH_SQL, (hsh,))
        rows = res.fetchall()
        return rows is not None and len(rows) > 0

    def save_wallpaper_info(self, wallpaper_info: BingWallpaperInfo):
        cur = self._db_conn.cursor()
        cur.execute(SqliteBingWallpaperManager.INSERT_IMG_SQL,
                    (wallpaper_info.startdate, wallpaper_info.url, wallpaper_info.copyright, wallpaper_info.hsh,
                     wallpaper_info.zone, wallpaper_info.tojson()))
        self._db_conn.commit()


def write_file(file_name: str, data: bytes):
    file_dir = os.path.dirname(file_name)
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
        logging.info("[BingDownloader] create new dir: %s", file_dir)

    with open(file_name, "w+b") as file:
        file.write(data)


class BingWallpaperDownloader(object):
    FILE_NAME_PATTERN = re.compile(r"^https://www.bing.com/th\?id=(.*)&rf=.*", re.I)

    def __init__(self,
                 en_search: bool = True,
                 download_offset: int = 0,
                 download_cnt: int = 8,
                 download_path: str = "bing",
                 max_retries: int = 3,
                 backoff_ms: int = 1000,
                 timeout_ms: int = 5000,
                 download_timeout_ms: int = 10000,
                 wallpaper_mgr: BingWallpaperManager = None,
                 notify: Notification = None):
        self._en_search = en_search
        self._download_offset = download_offset
        self._download_cnt = download_cnt
        self._download_path = download_path
        self._max_retries = max_retries
        self._backoff = backoff_ms / 1000
        self._timeout = timeout_ms / 1000
        self._download_timeout = download_timeout_ms / 1000
        self._wallpaper_mgr = wallpaper_mgr
        self._notify = notify
        self._wallpaper_client = BingWallpaperClient(timeout_ms, max_retries, backoff_ms)

        if not os.path.exists(self._download_path):
            os.makedirs(self._download_path)

    def get_filename(self, date: str, url: str) -> str:
        match = BingWallpaperDownloader.FILE_NAME_PATTERN.match(url)
        if not match:
            raise Exception('not found filename from url')

        file_name = date + '_' + match.group(1)
        month = date[:-2]
        file_dir = os.path.join(self._download_path, month)
        file_path = os.path.join(file_dir, file_name)
        return file_path

    def download_one_img(self, wallpaper: BingWallpaperInfo):
        filename = self.get_filename(wallpaper.startdate, wallpaper.url)
        s = requests.Session()
        retries = Retry(total=self._max_retries, backoff_factor=self._backoff)
        s.mount('https://', HTTPAdapter(max_retries=retries))
        r = s.get(wallpaper.url, timeout=self._download_timeout)
        if r.status_code != 200:
            raise Exception("status_code: %d, resp: %s".format(r.status_code, r.text))

        write_file(file_name=filename, data=r.content)
        logging.info("[BingDownloader] success download wallpaper, %s, filename: %s", wallpaper.digest_str(), filename)

    def download(self):
        try:
            wallpapers = self._wallpaper_client.get_wallpaper_info(idx=self._download_offset,
                                                                   num=self._download_cnt,
                                                                   en_search=self._en_search)
            for w in wallpapers:
                if self._wallpaper_mgr.wallpaper_exist(w.hsh):
                    logging.info("[BingDownloader] wallpaper exist: %s", w.digest_str())
                    continue

                try:
                    self.download_one_img(w)
                    self._wallpaper_mgr.save_wallpaper_info(w)
                    logging.info("[BingDownloader] success save wallpaper info to database, %s", w.digest_str())
                    if self._notify:
                        self._notify.notify("Bing Wallpaper Download SUCCESS", w.tojson())
                except Exception as e:
                    logging.error("[BingDownloader] failed to download wallpaper, %s, msg: %s", w.digest_str(), e)
                    if self._notify:
                        self._notify.notify("Bing Wallpaper Download ERROR", "msg: {}\ninfo: {}".format(e, w.tojson()))
        except Exception as e:
            logging.error("[BingDownloader] failed to download, msg: %s", e)
