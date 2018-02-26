# coding=utf-8
"""
@version: 2017/12/25 025
@author: Suen
@contact: sunzh95@hotmail.com
@file: testapi
@time: 18:49
@note:  ??
"""
from __future__ import unicode_literals

from config import config

logger = config.logger
from app.api.test import test
from flask_ext.response import json_resp


@test.route('/')
def hello_world():
    logger.info('hello world')
    j = json_resp.success(message='hello world')
    return j
