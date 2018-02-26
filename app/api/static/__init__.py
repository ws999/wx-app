# coding=utf-8
"""
@version: 2018/1/23 023
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 10:17
@note:  ??
"""
from flask import Blueprint

staticapi = Blueprint('staticapi', __name__, url_prefix='')
from .wxqrimg import create, blend, uploadimg
from .filequery import get_text, get_img
