#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import requests
from requests import RequestException

from send_mail import mail


class Notification(object):
    SERVER_CHAN_URI = "https://sc.ftqq.com/"

    def __init__(self,
                 my_mail: str,
                 my_password: str,
                 server_chan_key: str,
                 to_mail: str):
        self._my_mail = my_mail
        self._my_pass = my_password
        self._server_chan_key = server_chan_key
        self._to_mail = to_mail

    def notify(self, title: str, content: str) -> bool:
        if not mail(self._my_mail, self._my_mail, self._my_pass, self._to_mail, title, content):
            logging.error("[Notify] failed to send mail")
        try:
            r = requests.get(Notification.SERVER_CHAN_URI + self._server_chan_key + ".send", params={"text": title})
            if r.status_code != 200:
                logging.error("[Notify] failed to notify, status_code=%d, msg=%s" % (r.status_code, r.text))
        except RequestException as e:
            logging.error("[Notify] failed to notify", e)
        return True
