# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: config.py
@time: 11:31
@note:  ??
"""
from __future__ import unicode_literals
import os

import datetime
import redis

basedir = os.path.abspath(os.path.dirname(__file__))

from pymongo import MongoClient
import logging


class Config(object):
    DEBUG = True
    # logging setting

    logger = logging.getLogger('debug')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(levelname)s - %(asctime)s - Process:%(process)d - thread:%(thread)d - %(filename)s - line:%(lineno)d - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    JSONIFY_MIMETYPE = 'application/json'

    SECRET_KEY = '5c61a9b3-00c2-4398-8b71-f2132cfafdcf'
    pwdSalt = "dsfjlflsjglsj;lgj7987891313is62m"
    smsApiKey = '4a4831aa5eea902e4cb34eea301320fe'

    MAIN_SITE = 'https://wx_app.cn/wx-app'
    GLOBAL_URL_PREFIX = '/wx-app'
    DEFAULT_USER_HEAD = 'https://wx_app.cn/static/image/df_head.jpg'

    CHARGE_RATE = 102

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True

    MONGODB_SETTINGS = [
        {'alias': 'default', 'db': 'wxapp', 'host': 'mongodb://192.168.1.2/wxapp', 'connect': False},
    ]
    MONGODB_CLIENT_DEFAULT = MongoClient(MONGODB_SETTINGS[0]['host'], connect=False)

    DB_DEFAULT = MONGODB_CLIENT_DEFAULT.get_database('wxapp')
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_NAME = 'wxappsid'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    SESSION_KEY_PREFIX = ''
    SESSION_COOKIE_PATH = '/'
    SESSION_REDIS = redis.Redis(host='192.168.1.2', port=6379, db=2)

    # redis cache
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 7200
    CACHE_REDIS_HOST = '192.168.1.2'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 2
    CACHE_KEY_PREFIX = 'wxapp_'

    WX_APPID = ''
    WX_MCHID = ''
    WX_APPSECRET = ''
    WX_APPAPIKEY = ''

    server_static_file = 'static'


class TestConfig(Config):
    DEBUG = False

    MONGODB_SETTINGS = [
        {'alias': 'default', 'db': 'wxapp', 'host': 'mongodb://127.0.0.1/wxapp', 'connect': False},
    ]
    MONGODB_CLIENT_DEFAULT = MongoClient(MONGODB_SETTINGS[0]['host'], connect=False)

    DB_DEFAULT = MONGODB_CLIENT_DEFAULT.get_database('wxapp')
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_NAME = 'wxappsid'
    SESSION_COOKIE_PATH = '/'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port=6379, db=0)

    # redis cache
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 7200
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 2

    WX_APPID = ''
    WX_MCHID = ''
    WX_APPSECRET = ''
    WX_APPAPIKEY = ''


from local_config import ProConfig

configDict = {
    'dev': DevConfig,  # 开发环境
    'test': TestConfig,  # 测试环境
    'pro': ProConfig,  # 生产环境
}

# TODO 需配置local_config并设置WXAPP_CONFIG
config = configDict[os.getenv('WXAPP_CONFIG') or 'dev']
