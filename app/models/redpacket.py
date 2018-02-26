# coding=utf-8
"""
@version: 2018/1/15 015
@author: Suen
@contact: sunzh95@hotmail.com
@file: redpacket
@time: 16:45
@note:  ??
"""
from __future__ import unicode_literals

import collections
import datetime

import bson

from app import db
from interface import redpacketobj
from services.formatter import str2objectid


class RedPacket(db.Document):
    _id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    amount = db.IntField()
    count = db.IntField()
    left_count = db.IntField()
    title = db.StringField(max_length=64)
    level = db.IntField()
    poster = db.StringField(max_length=256)

    create_time = db.DateTimeField()
    expire_time = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'redpacket',
        'id_field': '_id',
    }

    @property
    def could_collect(self):
        flag = False
        if self.left_count and self.expire_time > datetime.datetime.now():
            flag = True
        return flag

    @classmethod
    def get_packet(cls, redpacket_id):
        redpacket_id = str2objectid(redpacket_id)
        packet = cls.objects.filter(_id=redpacket_id, expire_time__gte=datetime.datetime.now()).first()
        return packet

    @classmethod
    def get_packet_all(cls, redpacket_id):
        redpacket_id = str2objectid(redpacket_id)
        packet = cls.objects.filter(_id=redpacket_id).first()
        if not packet:
            return
        return packet

    @classmethod
    def has_collect(cls, redpacket_id, open_id=None):
        redpacket_id = str2objectid(redpacket_id)
        rpl = RedPacketLog.objects.filter(redpacket_id=redpacket_id, open_id=open_id,
                                          status=RedPacketLog.STATUS_DONE).first() if open_id else None
        has_collect, value = (True, rpl.value) if rpl else (False, 0)
        return has_collect, value / 100.0

    @classmethod
    def create_redpacket(cls, open_id, amount, number, title, level, posterurl, _id=None):
        flag, result = redpacketobj.result(amount, number, 1)
        if not flag:
            return result
        now = datetime.datetime.now()
        if not _id: _id = bson.ObjectId()
        redpacket = cls(_id=_id, open_id=open_id, amount=amount, count=number, left_count=number, title=title,
                        level=level, create_time=now, expire_time=now + datetime.timedelta(days=7), poster=posterurl)
        redpacketlog = []
        for value in result:
            redpacketlog.append(RedPacketLog(redpacket_id=_id, value=value, status=0, last_modify=now))
        rpl = RedPacketLog.objects.insert(redpacketlog)
        rp = cls.objects.insert(redpacket) if rpl else None
        return _id if rp else None

    @classmethod
    def collect_redpacket(cls, redpacket_id, open_id):
        redpacket_id=str2objectid(redpacket_id)
        rp = cls.objects.filter(_id=redpacket_id, left_count__gte=1).update_one(inc__left_count=-1)
        if not rp:
            return False,
        filters = dict(redpacket_id=redpacket_id, status=RedPacketLog.STATUS_UN, open_id__exists=False)
        rpl = RedPacketLog.objects.filter(**filters).first()
        if not rpl:
            return False,
        modify = {'status': RedPacketLog.STATUS_DONE, 'open_id': open_id, 'last_modify': datetime.datetime.now()}
        result = rpl.modify(query=filters, **modify)
        if not result:
            return False,
        return rpl.value, rpl.pk

    def collect_report(self, open_id, status, rp_log_id=None):
        data = dict(redpacket_id=self.pk, status=status, open_id=open_id, create_time=datetime.datetime.now())
        if status == RedPacketCollectLog.STATUS_SUCCESS and rp_log_id:
            data.update({'rp_log_id': str(rp_log_id)})
            rpcl = RedPacketCollectLog(**data)
        elif status == RedPacketCollectLog.STATUS_FAIL:
            rpcl = RedPacketCollectLog(**data)
        else:
            return False
        RedPacketCollectLog.objects.insert(rpcl)
        return RedPacketCollectLog.objects.filter(redpacket_id=self.pk, open_id=open_id).count()


class RedPacketLog(db.Document):
    STATUS_UN = 0
    STATUS_DONE = 1
    OPTIONS_STATUS = collections.OrderedDict([
        (STATUS_UN, '未领取'),
        (STATUS_DONE, '已领取')
    ])

    _id = db.ObjectIdField()
    redpacket_id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    value = db.IntField()
    status = db.IntField(choices=OPTIONS_STATUS.iteritems(), default=0)

    last_modify = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'redpacket_log',
        'id_field': '_id',
    }


class RedPacketCollectLog(db.Document):
    STATUS_SUCCESS = 0
    STATUS_FAIL = 1
    OPTIONS_STATUS = collections.OrderedDict([
        (STATUS_SUCCESS, '成功'),
        (STATUS_FAIL, '失败')
    ])
    _id = db.ObjectIdField()
    redpacket_id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    rp_log_id = db.StringField(max_length=64, default='')
    status = db.IntField(choices=OPTIONS_STATUS.iteritems())

    create_time = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'rp_collect_log',
        'id_field': '_id',
    }
