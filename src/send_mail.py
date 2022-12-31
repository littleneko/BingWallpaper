#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# GNU All-Permissive License
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

import argparse
import logging
import re
import sys
import smtplib

from enum import Enum
from email.mime.text import MIMEText
from email.utils import formataddr


class SmtpType(Enum):
    N163 = 1
    N126 = 2
    QQ = 5
    Google = 10


class SmtpInfo:
    def __init__(self, server, port, ssl):
        self.server = server
        self.port = port
        self.ssl = ssl


SMTP_RE = [
    (re.compile(r".*@163.com$"), SmtpType.N163),
    (re.compile(r".*@126.com$"), SmtpType.N126),
    (re.compile(r".*@qq.com$"), SmtpType.QQ),
    (re.compile(r".*@gmail.com$"), SmtpType.Google)
]

SMTP_INFO = {
    SmtpType.N163: SmtpInfo("smtp.163.com", 465, True),
    SmtpType.N126: SmtpInfo("smtp.126.com", 465, True),
    SmtpType.QQ: SmtpInfo("smtp.qq.com", 465, True),
    SmtpType.Google: SmtpInfo("smtp.gmail.com", 465, True),
}


def get_smtp_info(mail_address: str) -> SmtpInfo:
    smtp_type = SmtpType.N163
    for item in SMTP_RE:
        if item[0].match(mail_address):
            smtp_type = item[1]
            break
    return SMTP_INFO[smtp_type]


def mail(from_address: str, from_name: str, pwd: str, to_address: str, title: str, content: str) -> bool:
    success = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr((from_name, from_address))
        msg['To'] = formataddr(("", to_address))
        msg['Subject'] = title

        smtp_info = get_smtp_info(from_address)
        if smtp_info.ssl:
            server = smtplib.SMTP_SSL(smtp_info.server, smtp_info.port)
        else:
            server = smtplib.SMTP(smtp_info.server, smtp_info.port)

        server.login(from_address, pwd)
        server.sendmail(from_address, [to_address, ], msg.as_string())
        server.quit()
    except Exception as e:
        logging.error("failed to send mail, %s", e)
        success = False
    return success


def get_options(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("--from-addr", default="example@163.com", help="Your email send from.")
    parser.add_argument("--from-name", default="Robot", help="Your name.")
    parser.add_argument("--to-addr", default="example@163.com", help="Your email send to.")
    parser.add_argument("-p", "--password", help="Your sent email password.")
    parser.add_argument("-t", "--title", help="Your email title.")
    parser.add_argument("-c", "--content", help="Your email content, only support text.")
    opts = parser.parse_args(args)
    return opts


if __name__ == '__main__':
    options = get_options(sys.argv[1:])
    ret = mail(options.from_addr, options.from_name, options.password, options.to_addr, options.title, options.content)
    if ret:
        print("success")
    else:
        print("fail")
