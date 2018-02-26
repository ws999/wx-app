# coding=utf-8
"""
@version: 2017/12/25 025
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 18:48
@note:  ??
"""
from __future__ import unicode_literals

from flask import Blueprint
test = Blueprint('test', __name__, url_prefix='')
from testapi import hello_world