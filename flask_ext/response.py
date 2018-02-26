#!/usr/bin/python
# coding=utf-8
"""
@version: 2017/7/21 021
@author: Suen
@contact: sunzh95@hotmail.com
@file: response
@time: 11:35
@note:  'application/json'
"""
from __future__ import unicode_literals

from flask import jsonify, Response
from werkzeug.utils import cached_property

from config import config


class JsonResponse(object):
    """
    >0 : successed, 0 means general, if specail, make the code > 0
    <0 : failed, -1 means general, if specail, make the code < -1
    """
    CODE_DEFAULT = CODE_SUCCESS = 0
    CODE_FAIL = -1
    CODE_FAIL_BY_PARAMS = -2
    CODE_FAIL_UNAUTHENTICATED = -3
    CODE_FAIL_LOGIN = -4

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def _result(self, code=None, message=None, data=None, **kwargs):
        if not code: code = self.CODE_DEFAULT
        if not message: message = ':)'
        if not data: data = {}

        try:
            obj = dict(code=code, msg=message, data=data)
            response = jsonify(obj)
            return response
        except Exception as e:
            config.logger.error(e, exc_info=True)
            return jsonify(kwargs)

    def success(self, code=0, message=':)', data=None, **kwargs):
        return self._result(code, message, data, **kwargs)

    def failed(self, code=-1, message=':(', data=None, **kwargs):
        return self._result(code, message, data, **kwargs)

    def failedByParameter(self, errorParameter, data=None, **kwargs):
        msg = 'error parameter:{}'.format(errorParameter, **kwargs)
        return self.failed(-2, msg, data)

    def failedByUnauthenticated(self):
        return self.failed(-3, 'Unauthenticated')

    def failedByLogin(self):
        return self.failed(-4, 'login error')

    @cached_property
    def code_func_map(self):
        return {
            self.CODE_SUCCESS: self.success,
            self.CODE_FAIL: self.failed,
            self.CODE_FAIL_BY_PARAMS: self.failedByParameter,
            self.CODE_FAIL_UNAUTHENTICATED: self.failedByUnauthenticated,
            self.CODE_FAIL_LOGIN: self.failedByLogin
        }

    def make_response(self, **kwargs):
        code = kwargs.pop('code', self.CODE_DEFAULT)
        return self.code_func_map.get(code)(**kwargs)


json_resp = JsonResponse()


class ImgResponse(Response):
    default_mimetype = 'image/gif'


class TextResponse(Response):
    default_mimetype = 'text/plain'
