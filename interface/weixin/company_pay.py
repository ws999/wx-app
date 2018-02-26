# coding=utf-8
"""
@version: 2018/1/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: company_pay
@time: 14:35
@note:  ??
"""
from __future__ import unicode_literals

import os
import uuid
import requests
import hashlib
from xml.etree import cElementTree as etree
from config import config

logger = config.logger


class CompanyPay(object):
    TRANSFER_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'

    def __init__(self, appid, mch_id, api_key, ssl_cert="", ssl_key=""):
        self._appid = appid
        self._mch_id = mch_id
        self._api_key = api_key
        self._ssl_cert = ssl_cert
        self._ssl_key = ssl_key
        self.api_client_cert_path = os.path.join('.', 'cert', 'apiclient_cert.pem')
        self.api_client_key_path = os.path.join('.', 'cert', 'apiclient_key.pem')

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

    def get_transfer_args(self, out_trade_no, total_fee, openid, desc, spbill_create_ip):
        data = {
            "mch_appid": self._appid,
            "mchid": self._mch_id,
            "nonce_str": uuid.uuid4().hex,
            "partner_trade_no": out_trade_no,
            "openid": openid,
            "check_name": 'NO_CHECK',
            "amount": total_fee,
            "desc": desc,
            "spbill_create_ip": spbill_create_ip,
        }
        data['sign'] = self.sign(data)
        return self.to_xml(data)

    def request_transfer(self, request_body):
        resp = requests.post(self.TRANSFER_URL, data=request_body,
                             cert=(self.api_client_cert_path, self.api_client_key_path))
        content = self.to_dict(resp.content)
        logger.info('[wxtransfer] %s' % content)
        try:
            if content.get('return_code') == 'SUCCESS' and content.get('return_msg', {}).get(
                    'err_code') == 'SYSTEMERROR':
                resp = requests.post(self.TRANSFER_URL, data=request_body)  # 返回系统错误应重试
                content = self.to_dict(resp.content)
                logger.info('[syserr-wxtransfer retry] %s' % content)
            if content.get('return_code') == 'SUCCESS' and content.get('return_msg', {}).get(
                    'result_code') == 'SUCCESS':
                return True, content.get('return_msg', {})
        except:
            return False, None
        return False, None

    def sign(self, data):
        string = '&'.join(
            ['%s=%s' % (key, v) for key, v in sorted(data.iteritems(), key=lambda x: x[0]) if v])
        string = string + "&key=" + self._api_key
        return hashlib.md5(string).hexdigest().upper()
