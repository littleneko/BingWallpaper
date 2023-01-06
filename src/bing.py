#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import os
import time
import json
import re
import sqlite3
import requests
from requests import Timeout, RequestException

from notify import Notification


class BingDownloader(object):
    ZONE_CN = "CN"
    ZONE_EN = "EN"

    BING_BASE_URL = "https://www.bing.com"
    BING_ARCHIVE_RUL = BING_BASE_URL + "/HPImageArchive.aspx"
    FILE_NAME_PATTERN = re.compile(r"^/th\?id=(.*)&rf=.*", re.I)

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

    def __init__(self,
                 sqlite_file: str = "bing.db",
                 download_dir: str = "bing",
                 max_retry: int = 3,
                 backoff_ms: int = 1000,
                 timeout_ms: int = 5000,
                 download_timeout_ms: int = 10000,
                 notify: Notification = None):
        self._sqlite_file = sqlite_file
        self._download_dir = download_dir
        self._max_retry = max_retry
        self._backoff_ms = backoff_ms
        self._timeout_ms = timeout_ms
        self._download_timeout_ms = download_timeout_ms
        self._notify = notify
        self._db_conn = sqlite3.connect(self._sqlite_file)

        file_paths = [os.path.join(self._download_dir, BingDownloader.ZONE_CN),
                      os.path.join(self._download_dir, BingDownloader.ZONE_EN)]
        for path in file_paths:
            if not os.path.exists(path):
                os.makedirs(path)

    def get_img_info(self, idx: int, num: int, en: int) -> dict:
        """

        :param idx:
        :param num: number of images to get, max is 8
        :param en: EN or ZH
        :return:
        {
            "images": [
                {
                    "startdate": "20200229",
                    "fullstartdate": "202002290800",
                    "enddate": "20200301",
                    "url": "/th?id=OHR.WallaceFF_EN-CN6550155171_UHD.jpg&rf=LaDigue_UHD.jpg&pid=hp&w=3840&h=2160&rs=1&c=4",
                    "urlbase": "/th?id=OHR.WallaceFF_EN-CN6550155171",
                    "copyright": "A Wallace's flying frog glides to the forest floor (© Stephen Dalton/Minden Pictures)",
                    "copyrightlink": "/search?q=wallace%27s+flying+frog&form=hpcapt&filters=HpDate%3a%2220200229_0800%22",
                    "title": "It's leap day!",
                    "caption": "It's leap day!",
                    "copyrightonly": "© Stephen Dalton/Minden Pictures",
                    "desc": "For leap day (the extra day added to February every four years), we're looking at a Wallace's flying frog. Also known as parachute frogs, these critters live in the tropical jungles of Malaysia and Borneo. They spend most of their time in trees, gliding down to the ground to mate and lay eggs. They 'fly' by leaping and using their webbed fingers and toes to glide as far as 50 feet.",
                    "date": "Feb 29, 2020",
                    "bsTitle": "It's leap day!",
                    "quiz": "/search?q=Bing+homepage+quiz&filters=WQOskey:%22HPQuiz_20200229_WallaceFF%22&FORM=HPQUIZ",
                    "wp": true,
                    "hsh": "f12d92fa7c1da6fa876d4e9fb67a5104",
                    "drk": 1,
                    "top": 1,
                    "bot": 1,
                    "hs": [],
                    "og": {
                        "img": "https://www.bing.com/th?id=OHR.WallaceFF_EN-CN6550155171_tmb.jpg",
                        "title": "It's leap day!",
                        "desc": "For leap day (the extra day added to February every four years), we're looking at a Wallace's flying frog. Also known as parachute frogs…",
                        "hash": "rIV/nHYEvgH2ITMK5WgAA99XRLLTyTHeGJiIMDKsyI0="
                    }
                }
            ],
            "tooltips": {
                "loading": "Loading...",
                "previous": "Previous image",
                "next": "Next image",
                "walle": "This image is not available to download as wallpaper.",
                "walls": "Download this image. Use of this image is restricted to wallpaper only."
            },
            "quiz": {
                "question": "Who first introduced the concept of a leap year?",
                "id": "HPQuiz_20200229_WallaceFF",
                "url": "/search?q=Bing+homepage+quiz&filters=WQOskey%3A%22HPQuiz_20200229_WallaceFF%22&FORM=HPQUIZ",
                "options": [
                    {
                        "text": "Julius Caesar",
                        "url": "/search?q=julius+caesar&filters=IsConversation%3A%22True%22+btrequestsource%3A%22homepage%22+WQOskey%3A%22HPQuiz_20200229_WallaceFF%22+WQId%3A%221%22+WQQI%3A%220%22+WQCI%3A%220%22+ShowTimesTaskPaneTrigger%3A%22false%22+WQSCORE%3A%221%22&FORM=HPQUIZ"
                    },
                    {
                        "text": "Lanny Poffo",
                        "url": "/search?q=julius+caesar&filters=IsConversation%3A%22True%22+btrequestsource%3A%22homepage%22+WQOskey%3A%22HPQuiz_20200229_WallaceFF%22+WQId%3A%221%22+WQQI%3A%220%22+WQCI%3A%221%22+ShowTimesTaskPaneTrigger%3A%22false%22+WQSCORE%3A%220%22&FORM=HPQUIZ"
                    },
                    {
                        "text": "Pope Gregory XIII",
                        "url": "/search?q=julius+caesar&filters=IsConversation%3A%22True%22+btrequestsource%3A%22homepage%22+WQOskey%3A%22HPQuiz_20200229_WallaceFF%22+WQId%3A%221%22+WQQI%3A%220%22+WQCI%3A%222%22+ShowTimesTaskPaneTrigger%3A%22false%22+WQSCORE%3A%220%22&FORM=HPQUIZ"
                    }
                ]
            }
        }
        """
        retry_times = self._max_retry
        while retry_times > 0:
            try:
                response = requests.get(BingDownloader.BING_ARCHIVE_RUL, params={
                    "format": "js",
                    "idx": idx,
                    "n": num,
                    "nc": int(time.time() / 1000),
                    "pid": "hp",
                    "ensearch": en,
                    "quiz": 1,
                    "og": 1,
                    "uhd": 1,
                    "uhdwidth": 3840,
                    "uhdheight": 2160
                }, timeout=self._timeout_ms / 1000)
                if response.status_code != 200:
                    logging.info("[BingDownloader] failed to get image, status code = %d", response.status_code)
                    retry_times -= 1
                else:
                    data = response.json()
                    return data
            except Timeout:
                retry_times -= 1
                logging.info("[BingDownloader] timeout to get image, retry = %d", retry_times)
            except RequestException as e:
                logging.error("[BingDownloader] failed to get image, error info", e)
                raise e
            time.sleep(self._backoff_ms / 1000)

    def img_exist(self, hsh: str) -> bool:
        cur = self._db_conn.cursor()
        res = cur.execute(BingDownloader.CHECK_HSH_SQL, (hsh,))
        rows = res.fetchall()
        return rows is not None and len(rows) > 0

    def save_img_info(self, img: dict):
        hsh = img['hsh']
        url = img['url']
        date = img['startdate']
        cur = self._db_conn.cursor()
        cur.execute(BingDownloader.INSERT_IMG_SQL,
                    (date, url, img['copyright'], hsh, BingDownloader.ZONE_CN, json.dumps(img, ensure_ascii=False)))
        self._db_conn.commit()
        logging.info("[BingDownloader] success save image info to db, date: %s, hash: %s, url: %s", date, hsh, url)

    def init_and_get_filename(self, zone: str, date: str, url: str) -> str | None:
        match = BingDownloader.FILE_NAME_PATTERN.match(url)
        if not match:
            return None
        file_name = date + '_' + match.group(1)
        month = date[:-2]
        file_dir = os.path.join(self._download_dir, zone, month)
        if not os.path.exists(file_dir):
            logging.info("[BingDownloader] create dir: %s", file_dir)
            os.mkdir(file_dir)
        file_path = os.path.join(file_dir, file_name)
        return file_path

    def download_one_img(self, zone: str, date: str, url: str) -> bool:
        filename = self.init_and_get_filename(zone, date, url)
        if filename is None:
            logging.error("[BingDownloader] can't get file name from url: %s", url)
            return False
        logging.info("[BingDownloader] file path: %s", filename)

        retry_times = self._max_retry
        while retry_times > 0:
            try:
                r = requests.get(BingDownloader.BING_BASE_URL + url, timeout=self._download_timeout_ms / 1000)
                if r.status_code != 200:
                    logging.error(
                        "[BingDownloader] failed to download, status_code: %d, resp: %s" % (r.status_code, r.text))
                    retry_times -= 1
                with open(filename, "w+b") as code:
                    code.write(r.content)
                return True
            except RequestException as e:
                logging.error("[BingDownloader] failed to download", e)
                retry_times -= 1
            except Exception as e:
                logging.error("[BingDownloader] failed to download", e)
                retry_times -= 1
            time.sleep(self._backoff_ms / 1000)

    def download(self):
        img_info = self.get_img_info(0, 8, 0)
        images = img_info['images']
        for img in images:
            hsh = img['hsh']
            url = img['url']
            date = img['startdate']

            if self.img_exist(hsh):
                logging.info("[BingDownloader] image exist: date=%s, hsh=%s, url=%s", date, hsh, url)
                continue

            logging.info("[BingDownloader] success get img, date: %s, hsh: %s, url: %s", date, hsh, url)
            if not self.download_one_img(BingDownloader.ZONE_CN, date, url):
                logging.error("[BingDownloader] failed to download '%s'", img)
                if self._notify: self._notify.notify("Bing Wallpaper Download ERROR", img)
                continue
            self.save_img_info(img)
            if self._notify: self._notify.notify("Bing Wallpaper Download SUCCESS", json.dumps(img, ensure_ascii=False))

    def init_db(self):
        conn = sqlite3.connect(self._sqlite_file)
        cur = conn.cursor()
        cur.execute(BingDownloader.CREATE_TABLE_SQL)
        conn.close()

    def clean_db(self):
        if not os.path.exists(self._sqlite_file):
            return
        conn = sqlite3.connect(self._sqlite_file)
        cur = conn.cursor()
        cur.execute(BingDownloader.CLEAN_DB_SQL)
        conn.close()
