# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: urls
@time: 11:37
@note:  ??
"""
from __future__ import unicode_literals

from app.api.test import test
from app.api.user import user
from app.api.redpacket import packet
from app.api.order import order
from app.api.static import staticapi

register_module = [test, user, packet, order, staticapi]

from config import config


def url_register(app, register_module=register_module):
    for mod in register_module:
        mod.url_prefix = config.GLOBAL_URL_PREFIX + mod.url_prefix
        app.register_blueprint(mod)
