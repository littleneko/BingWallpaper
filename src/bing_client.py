# !/usr/bin/python3
# -*- coding: utf8 -*-

import dataclasses
import time
import requests
import json
from enum import Enum, auto
from dataclasses import dataclass

from requests import RequestException
from requests.adapters import HTTPAdapter, Retry


class WallpaperQuality(Enum):
    FHD_1609 = auto()
    FHD_1610 = auto()
    QHD_1609 = auto()
    QHD_1610 = auto()
    UHD_1609 = auto()
    UHD_1610 = auto()


@dataclass
class BingWallpaperInfo:
    startdate: str
    fullstartdate: str
    enddate: str
    url: str
    copyright: str
    copyrightlink: str
    copyrightonly: str
    title: str
    caption: str
    desc: str
    date: str
    quiz: str
    hsh: str
    zone: str

    def asdict(self) -> dict:
        return dataclasses.asdict(self)

    @staticmethod
    def fromdict(src: dict, ignore_miss: bool = True):
        new_src = {}
        for field_name, field_type in BingWallpaperInfo.__annotations__.items():
            if field_name in src:
                data = src.get(field_name)
                if type(data) is not field_type:
                    raise Exception(
                        "field '{}' type not match, require: {}, actual: {}".format(field_name, field_type, type(data)))
                new_src[field_name] = data
            elif ignore_miss:
                new_src[field_name] = None
            else:
                raise Exception("missing field '{}'".format(field_name))
        wallpaper_info = BingWallpaperInfo(**new_src)
        return wallpaper_info

    def tojson(self) -> str:
        return json.dumps(self.asdict(), ensure_ascii=False)

    def digest_str(self) -> str:
        return "[date: {}, hsh: {}, title: {}, url: {}]".format(self.startdate, self.hsh, self.title, self.url)


class BingWallpaperClient(object):
    BING_BASE_URL = "https://www.bing.com"
    BING_ARCHIVE_RUL = BING_BASE_URL + "/HPImageArchive.aspx"

    WALLPAPER_WH = {
        WallpaperQuality.FHD_1609: [1920, 1080],
        WallpaperQuality.FHD_1610: [1920, 1200],
        WallpaperQuality.QHD_1609: [2560, 1440],
        WallpaperQuality.QHD_1610: [2560, 1600],
        WallpaperQuality.UHD_1609: [3840, 2160],
        WallpaperQuality.UHD_1610: [3840, 2400]
    }

    def __init__(self, timeout: int = 3000, max_retries: int = 3, backoff: int = 1000):
        """

        :param timeout: millisecond
        :param max_retries:
        :param backoff: millisecond
        """
        self._timeout = timeout / 1000
        self._max_retries = max_retries
        self._backoff = backoff / 1000

    def get_wallpaper_info(self,
                           quality: WallpaperQuality = WallpaperQuality.UHD_1609,
                           idx: int = 0,
                           num: int = 8,
                           en_search: bool = True,
                           **kwargs) -> list[BingWallpaperInfo]:
        """

        :param quality: wallpaper quality
        :param idx: the day from today
        :param num: number of images to get, max is 8
        :param en_search: search en bing
        :return:
        """

        # response json
        """
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
        params = {
            "format": "js",
            "idx": idx,
            "n": num,
            "nc": int(time.time() / 1000),
            "pid": "hp",
            "ensearch": 1 if en_search else 0,
            "quiz": 1,
            "og": 1,
            "uhd": 1,
            "uhdwidth": BingWallpaperClient.WALLPAPER_WH[quality][0],
            "uhdheight": BingWallpaperClient.WALLPAPER_WH[quality][1],
        }
        for k, v in kwargs:
            params[k] = v

        s = requests.Session()
        retries = Retry(total=self._max_retries, backoff_factor=self._backoff)
        s.mount('https://', HTTPAdapter(max_retries=retries))

        response = s.get(BingWallpaperClient.BING_ARCHIVE_RUL, params=params, timeout=self._timeout)
        if response.status_code != 200:
            raise RequestException('status code: {}'.format(response.status_code))

        data = response.json()
        wallpapers = []
        for img in data['images']:
            img['zone'] = 'EN' if en_search else 'CN'
            img['url'] = BingWallpaperClient.BING_BASE_URL + img['url']
            wallpapers.append(BingWallpaperInfo.fromdict(img))
        return wallpapers


if __name__ == '__main__':
    client = BingWallpaperClient()
    items = client.get_wallpaper_info()
    for item in items:
        print(item.tojson())
