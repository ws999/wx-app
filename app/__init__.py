# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 11:16
@note:  ??
"""
from __future__ import unicode_literals

from flask import Flask
from flask_ext import ExtMongoEngine, ExtDocument
from services import formatter

db = ExtMongoEngine(Document=ExtDocument)

from flask_session import Session
from flask_login import LoginManager
from flask_cache import Cache

session = Session()
lm = LoginManager()
lm.session_protection = 'strong'
lm.login_view = '/wx-app/page/login'
cache = Cache()
from config import config
from app.urls import url_register


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)
    db.init_app(app)
    session.init_app(app)
    lm.init_app(app)
    cache.init_app(app)
    url_register(app)
    app.json_encoder = formatter.JSONEncoder

    return app
