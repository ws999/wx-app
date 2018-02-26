# coding=utf-8
"""
@version: 2018/1/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 16:26
@note:  ??
"""
from __future__ import unicode_literals
from flask import Blueprint

order = Blueprint('order', __name__, url_prefix='/api/order')
from wxorder import order_create, order_notify, pay_status
from transfer import transfer_wx
