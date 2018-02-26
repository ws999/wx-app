# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 15:48
@note:  ??
"""
from __future__ import unicode_literals

from flask import Blueprint

packet = Blueprint('redpacket', __name__, url_prefix='/api/redpacket')
from redpacket import red_packet_detail, red_packet_create, red_packet_collect
