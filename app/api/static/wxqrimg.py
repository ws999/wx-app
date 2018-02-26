# coding=utf-8
"""
@version: 2018/1/23 023
@author: Suen
@contact: sunzh95@hotmail.com
@file: imgapi
@time: 10:17
@note:  ??
"""
import os

from PIL import Image

from app.models import RedPacket, User
from interface import imgpro, wxqr
from app.api.static import staticapi
from flask import request
from flask_ext import json_resp, ImgResponse
from config import config

logger = config.logger


@staticapi.route('/api/img/wxqr/create', methods=['GET'])
def create():
    args = request.args.to_dict()
    redpacket_id = args.get('redpacket_id', '')
    shape = args.get('shape', '')
    logger.info('blend img redpacket_id:%s shape:%s' % (redpacket_id, shape))

    if not shape in ['circle']:
        return json_resp.failedByParameter('shape')
    redpacket = RedPacket.get_packet(redpacket_id)
    if not redpacket:
        return json_resp.failed(message='红包不存在或已过期')
    user = User.objects.filter(open_id=redpacket.open_id).first()
    if not user:
        return json_resp.failed(message='未找到红包来源')
    rp_url = 'pages/detail/detail'
    img_qr = wxqr.get_wx_qr(rp_url, redpacket_id)  # 获取圆形二维码
    if not img_qr:
        logger.error('微信二维码服务异常')
        img_qr = os.path.join('.', config.server_static_file, 'wx_qr', 'default_qr.png')

    try:  # 保存至本地
        img_qr = imgpro.fill_circle_qr(img_qr)
        filename = imgpro.save_img_to_disk(img_qr, 'wx_qr', filename=str(redpacket_id))
        logger.info('save img to localdisk success: %s' % filename)
    except:
        logger.error('save img to localdisk failed: %s' % redpacket_id)

    cimg = imgpro.img2stringio(img_qr)
    return ImgResponse(cimg)


@staticapi.route('/api/img/wxqr/blend', methods=['GET'])
def blend():
    redpacket_id = request.args.get('redpackey_id', '')
    redpacket = RedPacket.get_packet(redpacket_id)
    if not redpacket:
        return json_resp.failed(message='红包不存在或已过期')
    user = User.objects.filter(open_id=redpacket.open_id).first()
    if not user:
        return json_resp.failed(message='未找到红包来源')

    qr_name = redpacket_id + '.png'
    qrpath = os.path.join(config.server_static_file, 'wx_qr', qr_name)
    if not os.path.exists(qrpath):
        return json_resp.failed(message='验证码不存在')
    newimg, _ = imgpro.blend_img(qrpath, user.avatar)  # 合并图片

    try:
        filename = imgpro.save_img_to_disk(newimg, 'wx_qr', filename=str(redpacket_id) + '_pic')
        logger.info('save img to localdisk success: %s' % filename)
    except Exception as e:
        logger.error('save img to localdisk failed: %s_pic\n%s' % (redpacket_id, e))

    cimg = imgpro.img2stringio(newimg)
    return ImgResponse(cimg)


@staticapi.route('/api/img/upload', methods=['POST'])
def uploadimg():
    file = request.files.get('file')
    dirname = request.form.get('type', 'redpacket')
    try:
        img = Image.open(file)
        alpha = min(img.size) / 100.0
        img = img.resize([int(s / alpha) for s in img.size])
        img = img.crop((0, 0, 100, 100))
        imgname = imgpro.save_img_to_disk(img, dirname)
    except Exception as e:
        logger.error('parse picture failed: %s' % e)
        return json_resp.failed(message='图片解析失败')
    filepath = os.path.join(config.MAIN_SITE, config.server_static_file, dirname, imgname)
    logger.info('save file: %s' % filepath)
    return json_resp.success(data={'imgurl': filepath})
