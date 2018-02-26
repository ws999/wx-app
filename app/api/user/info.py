# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: info
@time: 14:07
@note:  ??
"""
from __future__ import unicode_literals

from flask import request
from flask_login import current_user, login_required

from app.models import User, RedPacketLog, RedPacket
from config import config
from flask_ext import json_resp

logger = config.logger

from app.api.user import user


@login_required
@user.route('/info_set', methods=['POST', 'GET'])
def set_info():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    args = request.form
    nickname = args.get('nickname', '')
    avatar = args.get('avatar', '')
    gender = args.get('gender', 'UNKNOW')
    province = args.get('province', '')
    city = args.get('city', '')
    intro = args.get('intro', '')
    if not gender in User.OPTIONS_GENDER.keys():
        return json_resp.failedByParameter('gender')

    user_id = current_user._id
    userop = current_user.get_operator()
    r = userop.set_info(user_id, nickname, avatar, gender, province, city, intro)
    if r:
        return json_resp.success()
    elif r == -1:
        return json_resp.failed(message='用户不存在')
    else:
        return json_resp.failed()


@login_required
@user.route('/info', methods=['GET'])
def get_info():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    data = current_user.info
    data.update({'capital': current_user.capital / 100.0})
    data.pop('_id', '')
    data.pop('open_id', '')
    data.pop('union_id', '')
    return json_resp.success(data=data)


@login_required
@user.route('/capital', methods=['GET'])
def capital():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    value = 0 if not current_user else current_user.capital
    logger.info('get_capital:%s_%s' % (current_user.open_id, value))
    return json_resp.success(data={'capital': value / 100.0})


@login_required
@user.route('/capital_log', methods=['GET'])
def capital_log():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    per_page = request.args.get('per_page', 6)
    page = request.args.get('page', 1)
    per_page = int(per_page) if isinstance(per_page, int) or per_page.isdigit() else 6
    page = int(page) if isinstance(page, int) or page.isdigit() else 1

    userop = current_user.get_operator()
    result, count, total = userop.capital_log(page, per_page)
    logger.info('capital_log:%s-page%s/%s_per%s' % (current_user.open_id, page, total, per_page))
    return json_resp.success(data={'total': total, 'result': result, 'page': page})


@login_required
@user.route('/rp_in_log', methods=['GET'])
def redpacket_in_log():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    per_page = request.args.get('per_page', 6)
    page = request.args.get('page', 1)
    per_page = int(per_page) if isinstance(per_page, int) or per_page.isdigit() else 6
    page = int(page) if isinstance(page, int) or page.isdigit() else 1

    userop = current_user.get_operator()
    rp_in_log, count, total = userop.redpacket_in_log(page, per_page)
    value = sum(RedPacketLog.objects.filter(open_id=current_user.open_id).values_list('value')) / 100.0

    logger.info('redpacket_in_log:%s-page%s/%s_per%s' % (current_user.open_id, page, total, per_page))
    data = {'total': total, 'rp_in_log': rp_in_log, 'page': page, 'count': count, 'amount_total': value}
    return json_resp.success(data=data)


@login_required
@user.route('/rp_out_log', methods=['GET'])
def redpacket_out_log():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    open_id = current_user.open_id
    per_page = request.args.get('per_page', 6)
    page = request.args.get('page', 1)
    per_page = int(per_page) if isinstance(per_page, int) or per_page.isdigit() else 6
    page = int(page) if isinstance(page, int) or page.isdigit() else 1

    userop = current_user.get_operator()
    rp_out_log, count, total = userop.redpacket_out_log(page, per_page)
    value = sum(RedPacket.objects.filter(open_id=open_id).values_list('amount')) / 100.0

    logger.info('redpacket_out_log:%s-page%s/%s_per%s' % (open_id, page, total, per_page))
    data = {'total': total, 'rp_out_log': rp_out_log, 'page': page, 'count': count, 'amount_total': value}
    return json_resp.success(data=data)
