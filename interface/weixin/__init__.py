# coding=utf-8
"""
@version: 2018/1/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: __init__.py
@time: 11:07
@note:  ??
"""
from __future__ import unicode_literals
from config import config
from pay import WXPay
from company_pay import CompanyPay

wxpay = WXPay(config.WX_APPID, config.WX_MCHID, config.WX_APPAPIKEY, config.MAIN_SITE + '/api/order/pay/notify')
wxtransfer = CompanyPay(config.WX_APPID, config.WX_MCHID, config.WX_APPAPIKEY, )

from wxappqr import WXQR

wxqr = WXQR(config.WX_APPID, config.WX_APPSECRET)
