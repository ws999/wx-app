# coding=utf-8
"""
@version: 2018/1/15 015
@author: Suen
@contact: sunzh95@hotmail.com
@file: capital
@time: 11:48
@note:  ??
"""
import collections

import datetime
from app import db
from config import config

logger = config.logger


class Capital(db.Document):
    _id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    value = db.IntField()

    last_modify = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'capital',
        'id_field': '_id',
    }

    @classmethod
    def reduce_capital(cls, open_id, value):
        if value > 0:
            return False, 'value must less than 0'
        filters = dict(open_id=open_id, value__gte=abs(value))
        capital = cls.objects.filter(**filters).first()
        if not capital:
            return False, '余额不足, 请前往充值'
        r = capital.modify(query=filters, inc__value=value, set__last_modify=datetime.datetime.now())
        if not r:
            return False, '扣除余额失败'
        return True, capital._data

    @classmethod
    def add_capital(cls, open_id, value):
        if value < 0:
            return False, 'value must greater than 0'

        capital = cls.objects.filter(open_id=open_id).first()
        if not capital:
            capital = cls.objects.insert(cls(open_id=open_id, value=0, last_modify=datetime.datetime.now()))
        r = capital.modify({}, inc__value=value, set__last_modify=datetime.datetime.now())
        if not r:
            return False, '操作失败'
        return True, capital._data


class CapitalLog(db.Document):
    REASON_CHARGE = 'CHARGE'
    REASON_TOCASH = 'TOCASH'
    REASON_COLLECT = 'COLLECT'
    REASON_DELIVER = 'DELIVER'
    OPTIONS_REASON = collections.OrderedDict([
        ('CHARGE', '充值'),
        ('TOCASH', '提现'),
        ('COLLECT', '领取'),
        ('DELIVER', '发出')
    ])
    _id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    sign = db.BooleanField()
    value = db.IntField()
    after_value = db.IntField()
    reason = db.StringField(max_length=16, choices=OPTIONS_REASON.iteritems(), default='OTHER')
    remark = db.StringField(max_length=64)

    create_time = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'capital_log',
        'id_field': '_id',
    }
