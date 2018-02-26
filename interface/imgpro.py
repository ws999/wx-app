# coding=utf-8
"""
@version: 2018/1/23 023
@author: Suen
@contact: sunzh95@hotmail.com
@file: imgpro
@time: 15:10
@note:  ??
"""

from __future__ import unicode_literals
import os
import math
import StringIO
import uuid
from io import BytesIO

import requests
from PIL import Image
from config import config


def make_background(img, background):
    """Only Support RGB mode"""
    x, y = img.size
    for xx in range(x):
        for yy in range(y):
            color = img.getpixel((xx, yy))
            if color == (255, 255, 255):
                img.putpixel((xx, yy), background.getpixel((xx, yy)))
    return img


def add_border(img, color, px, circular, background):
    def in_circle(xx, yy):
        for x0, y0 in points:
            dis = math.sqrt((xx - x0) ** 2 + (yy - y0) ** 2)
            if dis <= circular and dis >= circular - px:
                return True
        return False

    def in_cornor(xx, yy):
        for x0, y0 in points:
            dis = math.sqrt((xx - x0) ** 2 + (yy - y0) ** 2)
            if dis < circular:
                return False
        return True

    x, y = (200, 200)
    newimg = Image.new('RGB', (x, y), 0)
    img = img.resize((x - 2 * px, y - 2 * px))
    newimg.paste(img, (px, px))
    p1 = circular, circular
    p2 = x - circular, circular
    p3 = circular, y - circular
    p4 = x - circular, y - circular
    points = [p1, p2, p3, p4]
    for xx in range(x):
        for yy in range(y):
            if (xx > circular and xx < x - circular) and (yy > circular and yy < y - circular):
                continue
            elif in_circle(xx, yy) and ((xx < circular and (yy < circular or yy > y - circular)) or (
                            xx > x - circular and (yy < circular or yy > y - circular))):
                newimg.putpixel((xx, yy), color)
            elif (xx <= px or xx >= x - px) and (yy >= circular and yy <= y - circular):
                newimg.putpixel((xx, yy), color)
            elif (yy <= px or yy >= y - px) and (xx >= circular and xx <= x - circular):
                newimg.putpixel((xx, yy), color)
            elif in_cornor(xx, yy) and (xx < circular or xx > x - circular) and (yy < circular or yy > y - circular):
                newimg.putpixel((xx, yy), background.getpixel((xx, yy)))
    return newimg


def make_qr(img, outter, inner, background, bar_qr):
    def in_bar_area(dis):
        if dis >= inner / 2 and dis <= outter / 2:
            return True
        return False

    def out_area(dis):
        if dis > outter / 2:
            return True
        return False

    x, y = 350, 350
    px = (outter - inner) / 2
    img = img.resize((x - px * 2, y - px * 2))
    newimg = Image.new('RGB', (x, y), (255, 255, 255))
    newimg.paste(img, (px, px))
    for xx in range(x):
        for yy in range(y):
            dis = math.sqrt((xx - x / 2) ** 2 + (yy - y / 2) ** 2)
            if in_bar_area(dis):
                newimg.putpixel((xx, yy), bar_qr)
            elif out_area(dis):
                newimg.putpixel((xx, yy), background.getpixel((xx, yy)))
    return newimg


def fill_circle_qr(img_qr):
    qrxxyy = (365, 617, 715, 967)
    redpacket_path = os.path.join('.', 'static', 'server', 'redpacket')

    background_path = os.path.join(redpacket_path, 'background.jpg')
    img_background = Image.open(background_path)
    img_background = img_background.convert('RGB')

    img_qr = Image.open(img_qr)
    img_qr = img_qr.convert('RGB')
    qr_background = img_background.crop(qrxxyy)
    img_qr = make_qr(img_qr, 350, 310, qr_background, (233, 205, 158))
    return img_qr


def blend_img(img_qr, head_path=None):
    fingerxxyy = (450, 1042, 630, 1222)
    headxxyy = (440, 218, 640, 418)
    qrxxyy = (365, 617, 715, 967)
    redpacket_path = os.path.join('.', 'static', 'server', 'redpacket')

    background_path = os.path.join(redpacket_path, 'background.jpg')
    img_background = Image.open(background_path)
    img_background = img_background.convert('RGB')
    finger_background = img_background.crop(fingerxxyy)

    finger_path = os.path.join(redpacket_path, 'finger.png')
    img_finger = Image.open(finger_path)
    img_finger = img_finger.convert('RGB')
    img_finger = make_background(img_finger, finger_background)

    if head_path:
        try:
            img_head = BytesIO(requests.get(head_path).content)
            img_head = Image.open(img_head)
        except:
            img_head = Image.open(config.DEFAULT_USER_HEAD)
    else:
        img_head = Image.open(config.DEFAULT_USER_HEAD)
    img_head = img_head.convert('RGB')
    head_background = img_background.crop(headxxyy)
    img_head = add_border(img_head, (231, 63, 92), 8, 16, head_background)

    img_qr = Image.open(img_qr)
    img_qr = img_qr.convert('RGB')
    qr_background = img_background.crop(qrxxyy)
    img_qr = make_qr(img_qr, 350, 310, qr_background, (233, 205, 158))

    newimg = Image.new("RGB", (1080, 1350), (255, 255, 255))
    newimg.paste(img_background)
    newimg.paste(img_finger, fingerxxyy[:2])
    newimg.paste(img_head, headxxyy[:2])
    newimg.paste(img_qr, qrxxyy[0:2])

    return newimg, img_qr


def save_img_to_disk(img, dirname, ext='png', filename=''):
    if not filename:
        filename = uuid.uuid4().get_hex()
    if not '.' in filename:
        fullname = filename + '.' + ext
    else:
        fullname = filename
    fullpath = os.path.join('.', config.server_static_file, dirname, fullname)
    img.save(fullpath)
    return fullname


def img2stringio(img):
    cimg = StringIO.StringIO()
    img.save(cimg, 'png')
    cimg.seek(0)
    return cimg


def get_disk_img(filepath):
    fullpath = os.path.join('.', config.server_static_file, filepath)
    img = Image.open(fullpath)
    return img
