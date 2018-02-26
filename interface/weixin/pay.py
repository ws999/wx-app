# coding=utf-8
"""
@version: 2017/3/27
@author: Suen
@contact: sunzh95@hotmail.com
@file: pay
@time: 14:40
@note:
"""
from __future__ import unicode_literals
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import time
import uuid
import hashlib
from xml.etree import cElementTree as etree

import requests


class WXPay(object):
    UORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    REFUND_URL = "https://api.mch.weixin.qq.com/secapi/pay/refund"
    QUERY_URL = "https://api.mch.weixin.qq.com/pay/orderquery"

    def __init__(self, appid, mch_id, api_key, notify_url, ssl_cert="", ssl_key=""):
        self._appid = appid
        self._mch_id = mch_id
        self._api_key = api_key
        self._notify_url = notify_url
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key

    def to_xml(self, raw):
        s = ""
        for k, v in raw.items():
            s += "<{0}>{1}</{0}>".format(k, v)
        s = "<xml>{0}</xml>".format(s)
        return s.encode("utf-8")

    def to_dict(self, content):
        raw = {}
        root = etree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        return raw

    def create_unifiedorder(self, body, out_trade_no, total_fee, openid, spbill_create_ip,
                            trade_type='JSAPI', notify_url=''):
        data = {
            "appid": self._appid,
            "mch_id": self._mch_id,
            "nonce_str": uuid.uuid4().hex,
            "body": body,
            "out_trade_no": out_trade_no,
            "total_fee": total_fee,
            "trade_type": trade_type,
            "spbill_create_ip": spbill_create_ip,
            "notify_url": notify_url or self._notify_url,
            "openid": openid
        }
        data['sign'] = self.sign(data)
        request_body = self.to_xml(data)
        resp = requests.post(self.UORDER_URL, data=request_body)
        return self.to_dict(resp.content)

    def get_jsapi_request_args(self, prepay_id):
        data = {
            "appId": self._appid,  # 公众号名称，由商户传入
            "timeStamp": str(int(time.time())),  # 时间戳，自1970年以来的秒数
            "nonceStr": uuid.uuid4().hex,  # 随机串
            "package": "prepay_id=%s" % prepay_id,
            "signType": "MD5"  # 微信签名方式：
        }
        data["paySign"] = self.sign(data)  # 微信签名
        return data

    def sign(self, data):
        string = '&'.join(
            ['%s=%s' % (key, v) for key, v in sorted(data.iteritems(), key=lambda x: x[0]) if v])
        string = string + "&key=" + self._api_key
        return hashlib.md5(string).hexdigest().upper()

    def refund(self, **kwargs):
        data = {
            "appid": self._appid,
            "mch_id": self._mch_id,
            "nonce_str": uuid.uuid4().hex,
            "op_user_id": self._mch_id,
            "out_refund_no": "_refund_%s" % kwargs.get('out_trade_no')
        }
        data.update(kwargs)
        data['sign'] = self.sign(data)
        request_body = self.to_xml(data)
        resp = requests.post(
            self.REFUND_URL, data=request_body, cert=(self._ssl_cert, self._ssl_key)
        )
        result = self.to_dict(resp.content)
        if not result.get('result_code') == 'SUCCESS':
            raise Exception(result.get('return_msg', ''))
        return result

    def query_order(self, out_trade_no):
        data = {
            'appid': self._appid,
            'mch_id': self._mch_id,
            'out_trade_no': out_trade_no,
            'nonce_str': uuid.uuid4().hex,
        }
        data['sign'] = self.sign(data)
        request_body = self.to_xml(data)
        resp = requests.post(self.QUERY_URL, data=request_body)
        return self.to_dict(resp.content)


if __name__ == '__main__':
    from config import config

    wxpay = WXPay(
        'wx30f7c0f445593b28', '1396312502',
        'abcdefghijklmnopqrstuvwxyz123456', config.MAIN_SITE)
    print wxpay.create_unifiedorder(
        'ssdfsass', uuid.uuid4().hex, '100', 'ok6q7wRxqXAj2fkr20ivfZA6GVQA', '127.0.0.1'
    )
    print wxpay.query_order("wx15088126979883420")
