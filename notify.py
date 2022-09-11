#!/usr/bin/python3
# -*- coding: utf8 -*-

import requests
from requests import RequestException

from log import logger
from config import *
from send_mail import mail

SERVER_CHAN_URI = "https://sc.ftqq.com/"


def notify(to: str, title: str, content: str) -> bool:
    if not mail(MY_MAIL, MY_NAME, MY_PASS, to, title, content):
        logger.error("[Notify] failed to send mail")
    try:
        r = requests.get(SERVER_CHAN_URI + SERVER_CHAN_SENDKEY + ".send", params={"text": title})
        if r.status_code != 200:
            logger.error("[Notify] failed to notify, status_code=%d, msg=%s" % (r.status_code, r.text))
    except RequestException as e:
        logger.error("[Notify] failed to notify", e)
    return True
