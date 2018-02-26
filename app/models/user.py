# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: user
@time: 11:42
@note:  ??
"""
from __future__ import unicode_literals

import collections
import datetime

import bson

from app import db
from config import config
from services import formatter

logger = config.logger

from app.models import Capital
from flask_ext import ExtUserMixin
from interface.model_operator import UserOperator


class User(db.Document, ExtUserMixin):
    OPTIONS_GENDER = collections.OrderedDict([
        ('UNKNOWN', '未设置'),
        ('MAN', '男'),
        ('WOMAN', '女'),
    ])
    _id = db.ObjectIdField()
    open_id = db.StringField(max_length=64)
    union_id = db.StringField(max_length=64)
    nickname = db.StringField(max_length=64)

    avatar = db.StringField(max_length=256)
    gender = db.StringField(max_length=16, choices=OPTIONS_GENDER.iteritems(), default='UNKNOWN')  # 性别

    province = db.StringField(max_length=64)
    city = db.StringField(max_length=64)
    intro = db.StringField()

    is_active = db.BooleanField()

    create_time = db.DateTimeField()

    meta = {
        'db_alias': 'default',
        'collection': 'user',
        'id_field': '_id',
    }

    @classmethod
    def create_user(cls, open_id, union_id):
        u = cls.objects.filter(open_id=open_id, union_id=union_id).first()
        if u: return -2
        user = cls(open_id=open_id, union_id=union_id, is_active=True,
                   create_time=datetime.datetime.now())
        r = cls.objects.insert(user)
        if r: return r
        logger.error(msg='insert user err:%s_%s' % (open_id, union_id))

    @property
    def info(self):
        data = self._data
        return data

    @property
    def capital(self):
        capital = Capital.objects.filter(open_id=self.open_id).first()
        return 0 if not capital else capital.value

    def get_operator(self):
        return UserOperator(self, self.__class__)


# from app import lm
#
#
# @lm.user_loader
# def load_user(user_id):
#     print user_id
#     try:
#         return User.objects.get(_id=user_id)
#     except:
#         return None


from app import cache
from app import lm


# 从请求参数中获取Token, 如果不存在, 必须返回None
@lm.request_loader
def load_user_from_request(request):
    token = request.args.get('token', '')
    value = cache.get(token)
    if not isinstance(value, dict):
        return None
    if not value.get('open_id', ''):
        return None
    open_id = value.get('open_id')
    try:
        user = User.objects.filter(open_id=open_id).first()
        if user:
            cache.set(token, value, timeout=config.PERMANENT_SESSION_LIFETIME)
            return user
    except:
        return None
