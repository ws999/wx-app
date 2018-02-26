# coding=utf-8
"""
@version: 2018/1/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: order
@time: 14:58
@note:  ??
"""
from __future__ import unicode_literals

import collections
from app import db


class UserOrder(db.Document):
    PAY_TYPE_WX = 0
    PAY_TYPE_REDPACKET = 1
    OPTIONS_PAY_TYPE = collections.OrderedDict([
        (PAY_TYPE_WX, '微信账户'),
        (PAY_TYPE_REDPACKET, '红包账户'),
    ])

    PRODUCT_TYPE_WX = 0
    PRODUCT_TYPE_REDPACKET = 1
    OPTIONS_PRODUCT_TYPE = collections.OrderedDict([
        (PRODUCT_TYPE_WX, '微信账户'),
        (PRODUCT_TYPE_REDPACKET, '红包账户'),
    ])

    STATUS_UNPAY = 0
    STATUS_PAID = 1
    OPTIONS_STATUS = collections.OrderedDict([
        (STATUS_UNPAY, '未支付'),
        (STATUS_PAID, '已支付'),
    ])

    _id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)

    order_no = db.StringField(max_length=64)
    pay_type = db.IntField(choices=OPTIONS_PAY_TYPE.iteritems(), default=PAY_TYPE_WX)

    product_type = db.IntField(choices=OPTIONS_PRODUCT_TYPE.iteritems(), default=PRODUCT_TYPE_REDPACKET)
    product_id = db.StringField(max_length=64)
    product_value = db.IntField()
    status = db.IntField(choices=OPTIONS_STATUS.iteritems(), default=STATUS_UNPAY)

    price_origin = db.IntField()
    price_pay = db.IntField()
    product_num = db.IntField()

    order_msg = db.DictField()

    create_time = db.DateTimeField()
    pay_time = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'userorder',
        'id_field': '_id',
    }
