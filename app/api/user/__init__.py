# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 12:25
@note:  ??
"""
from __future__ import unicode_literals

from flask import Blueprint

user = Blueprint('user', __name__, url_prefix='/api/user')
from auth import user_login
from info import capital, capital_log, set_info, get_info, redpacket_in_log, redpacket_out_log
