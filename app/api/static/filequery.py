# coding=utf-8
"""
@version: 2018/2/5 005
@author: Suen
@contact: sunzh95@hotmail.com
@file: textfile
@time: 15:02
@note:  ??
"""
import os
import codecs
from PIL import Image
from interface import imgpro
from config import config

logger = config.logger
from flask_ext import TextResponse, ImgResponse, json_resp
from app.api.static import staticapi


@staticapi.route('/<filename>')
def get_text(filename):
    file_path = os.path.join('.', config.server_static_file, filename)
    if not os.path.exists(file_path):
        logger.error('文件不存在:%s' % file_path)
        return json_resp.failed(message='文件不存在')
    with codecs.open(file_path) as f:
        txt = f.readline()
    return TextResponse(txt)


@staticapi.route(r'/static/<type>/<name>')
def get_img(type, name):
    path = os.path.join('.', config.server_static_file, type, name)
    if not os.path.exists(path):
        logger.error('can\'t find file: %s' % path)
        return json_resp.failed(message='文件不存在')
    img = Image.open(path)
    cimg = imgpro.img2stringio(img)
    return ImgResponse(cimg)
