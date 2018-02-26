#!/usr/bin/python
# coding=utf-8
"""
@version: 2017/7/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: formatter.py
@time: 15:20
@note:  ??
"""
from __future__ import unicode_literals

import re
import bson
import json
import base64
import hashlib
import datetime
from mongoengine import QuerySet

from config import config

logger = config.logger


def encryptPwd(rawPwd):
    """
    密码加密闭包
    :param rawPwd: 
    :return: 
    """

    def md5Encrypt(raw, salt):
        m = hashlib.md5()
        m.update(raw)
        m.update(raw)
        m.update(salt)
        return m.hexdigest()

    return md5Encrypt(rawPwd, config.pwdSalt)


# 响应格式
handlers = {
    datetime.datetime: lambda o: str(o),
    bson.ObjectId: lambda o: str(o),
    QuerySet: lambda o: list(o)
}


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        handler = handlers.get(type(o), json.JSONEncoder.default)
        return handler(o)


def decode_base64_file(b64string):
    imgType, others = b64string.split(';', 1)
    m = re.match('data:(?P<type>\w+)/(?P<ext>\w+)', imgType)
    dt = m.group('type')
    if dt.lower() != 'image':
        logger.error('Not Support Type:' + dt)
        return None, None
    ext = m.group('ext')
    encoding, data = others.split(',', 1)
    if encoding.lower() != 'base64':
        logger.error('Not Support Encoding:' + encoding)
        return None, None
    return base64.b64decode(data), ext


def time2str(dt):
    if not isinstance(dt, datetime.datetime):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def str2objectid(str):
    if isinstance(str, bson.ObjectId):
        return str
    else:
        try:
            return bson.ObjectId(str)
        except:
            return
