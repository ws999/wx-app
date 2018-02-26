# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: auth
@time: 12:25
@note:  ??
"""
from __future__ import unicode_literals

import uuid

from flask import request, session
from flask_login import login_user, current_user

from app.api.user import user
from app.models import User
from config import config
from interface.weixin import wxauth
from flask_ext import json_resp

logger = config.logger
from app import cache


@user.route('/login', methods=['POST'])
def user_login():
    token = request.args.get('token', '')
    code = request.form.get('code', '')
    if not code:
        return json_resp.failedByParameter('code')
    logger.info('login user code: %s' % code)
    if current_user.is_authenticated:
        cache.set(token, cache.get(token), timeout=config.PERMANENT_SESSION_LIFETIME)
        data = current_user.info
        data.pop('open_id')
        data.pop('union_id')
        data.pop('_id')
        return json_resp.success(message='用户已登录', data={'user': data, 'token': token})

    content = wxauth.code2session(code)
    if not content:
        return json_resp.failed('微信登录服务异常')
    open_id = content.get('openid', '')
    union_id = content.get('union_id', '')
    session_key = content.get('session_key', '')

    user = User.objects.filter(open_id=open_id).first()
    if not user:
        logger.info('create user openid: %s' % open_id)
        user = User.create_user(open_id, union_id)

    login_user(user)
    session['open_id'] = open_id
    session['wx_session_key'] = session_key
    session.pop('user_id')
    token = uuid.uuid4().hex if not token else token
    cache.set(token, dict(session), timeout=config.PERMANENT_SESSION_LIFETIME)
    return json_resp.success(message='登陆成功', data={'user': user.info, 'token': token})
