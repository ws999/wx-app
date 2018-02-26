# coding=utf-8
"""
@version: 2018/1/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: wxauth
@time: 10:43
@note:  ??
"""

from __future__ import unicode_literals

import json
import requests
from config import config

logger = config.logger
base_url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'


def code2session(code):
    url = base_url.format(appid=config.WX_APPID, secret=config.WX_APPSECRET, code=code)
    print url
    try:
        resp = requests.post(url=url, timeout=3)
        logger.info('code2session:%s' % resp.content)
        content = json.loads(resp.content)
        assert content.get('openid')
    except ValueError:
        logger.error('failed: json loads code2session response error')
    except AssertionError:
        logger.error('failed: weixin code2session params error')
    except:
        logger.error('failed: weixin code2session remote error')
    else:
        logger.info('success: code2session')
        return content


if __name__ == '__main__':
    code2session('12345')
