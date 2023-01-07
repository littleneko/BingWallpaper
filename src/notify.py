#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import requests
from requests import RequestException

from send_mail import send_mail


class Notification(object):
    SERVER_CHAN_URI = "https://sc.ftqq.com/"

    def __init__(self,
                 my_mail: str = None,
                 my_password: str = None,
                 my_name: str = 'Robot',
                 to_mail: str = None,
                 server_chan_key: str = None):
        self._my_mail = my_mail
        self._my_pass = my_password
        self._my_name = my_name
        self._to_mail = to_mail
        self._server_chan_key = server_chan_key

    def notify(self, title: str, content: str):
        if self._to_mail:
            try:
                send_mail(self._my_mail, self._my_name, self._my_pass, self._to_mail, title, content)
            except Exception as e:
                logging.error("[Notify] failed to send mail, %s", e)

        if self._server_chan_key:
            try:
                r = requests.get(Notification.SERVER_CHAN_URI + self._server_chan_key + ".send", params={"text": title},
                                 timeout=5)
                if r.status_code != 200:
                    logging.error("[Notify] failed to notify server chan, status_code=%d, msg=%s", r.status_code,
                                  r.text)
            except RequestException as e:
                logging.error("[Notify] failed to notify server-chan, %s", e)
