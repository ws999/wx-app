# coding=utf-8
"""
@version: 2018/1/25 025
@author: Suen
@contact: sunzh95@hotmail.com
@file: wxappqr
@time: 13:59
@note:  ??
"""

from __future__ import unicode_literals

import json
import requests
from app import cache
from io import BytesIO
from PIL import Image

from config import config

logger = config.logger


class TokenError(KeyError):
    pass


class WXQR(object):
    def __init__(self, appid, secret):
        self.GET_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
            appid, secret)
        self.WXAPPQR_BASE_URL = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=%s'

    @property
    def token(self):
        token = cache.get('wx_token')

        if token:
            logger.info('wx token: %s' % token)
            return token
        try:
            resp = requests.get(self.GET_TOKEN_URL)
            content = json.loads(resp.content)
            token = content.get('access_token', '')
            expires = content.get('expires_in', '')
            assert token and expires
        except:
            logger.error('get wx_token error')
            raise TokenError
        logger.info('wx token: %s' % token)
        cache.set('wx_token', token, timeout=expires)
        return token

    def get_wx_qr(self, url, redpacket_id):
        post_url = self.WXAPPQR_BASE_URL % self.token
        params = {'scene': 'id=%s' % redpacket_id, 'page': url, 'width': 350, 'auto_color': True}
        logger.info('page:%s' % url)
        try:
            resp = requests.post(url=post_url, data=json.dumps(params), timeout=3,
                                 headers={'Content-type': 'image/jpeg'})
            logger.info('wx_qr resp content: %s' % resp.content)
            img = BytesIO(resp.content)
            Image.open(img)
        except Exception as e:
            logger.error('get wx_qr error:%s' % e)
            return
        logger.info('get wx_qr success')
        return img


if __name__ == '__main__':
    wxqr = WXQR(config.WX_APPID, config.WX_APPSECRET)
    wxqr.get_wx_qr('index')
