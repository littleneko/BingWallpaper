#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import requests
from requests import RequestException

from config import conf
from send_mail import mail

SERVER_CHAN_URI = "https://sc.ftqq.com/"


def notify(to: str, title: str, content: str) -> bool:
    if not mail(conf.my_mail, conf.my_mail, conf.my_pass, to, title, content):
        logging.error("[Notify] failed to send mail")
    try:
        r = requests.get(SERVER_CHAN_URI + conf.server_chan_sendkey + ".send", params={"text": title})
        if r.status_code != 200:
            logging.error("[Notify] failed to notify, status_code=%d, msg=%s" % (r.status_code, r.text))
    except RequestException as e:
        logging.error("[Notify] failed to notify", e)
    return True
