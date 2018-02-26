#!/usr/bin/python
# coding=utf-8
"""
@version: 2017/7/20 020
@author: Suen
@contact: sunzh95@hotmail.com
@file: model
@time: 12:15
@note:  默认mongodb主键为_id，适配user表中_id字段等
"""
from __future__ import unicode_literals

from flask_login import UserMixin
from flask_mongoengine import MongoEngine, BaseQuerySet,Document


class ExtUserMixin(UserMixin):
    def get_open_id(self):
        try:
            return str(self.open_id)
        except AttributeError:
            raise NotImplementedError('No `open_id` attribute')

    def get_id(self):
        try:
            return str(self._id)
        except AttributeError:
            raise NotImplementedError('No `_id` attribute - override `get_id`')


class ExtDocument(Document):
    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}

    @classmethod
    def find_page(cls, page=1, per_page=6, order_by='', **kwargs):
        if not order_by:
            order_by = '_id'
        if not kwargs:
            kwargs = {}
        assert isinstance(kwargs, dict)
        skip = per_page * (page - 1)
        limit = per_page
        result = cls.objects.filter(**kwargs).skip(skip).limit(limit).order_by(order_by)
        count = cls.objects.filter(**kwargs).count()
        total = count / per_page + (1 if count % per_page else 0)
        page = page if 0 < page < total + 1 else 1
        return result, page, total, count


class ExtMongoEngine(MongoEngine):
    def __init__(self, app=None, config=None, Document=None):
        super(ExtMongoEngine, self).__init__(app=app, config=config)
        if Document:
            self.Document = Document
