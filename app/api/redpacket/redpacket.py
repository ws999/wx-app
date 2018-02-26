# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: legendmall
@time: 15:49
@note:  ??
"""
from __future__ import unicode_literals

import json
import os

import bson
import requests
from flask import request, url_for
from flask_login import login_required, current_user

from app.models import RedPacket, CapitalLog, User, RedPacketLog, RedPacketCollectLog
from config import config
from services import formatter
from flask_ext import json_resp

logger = config.logger

from app.api.redpacket import packet


@packet.route('/<redpacket_id>/detail', methods=['GET'])
def red_packet_detail(redpacket_id):
    _id = bson.ObjectId(redpacket_id)
    redpacket = RedPacket.get_packet_all(_id)
    if not redpacket:
        return json_resp.failed(message='红包不存在')
    user = User.objects.filter(open_id=redpacket.open_id).first()
    redpacket_data = redpacket._data
    redpacket_data.update({'user_nickname': user.nickname, 'user_avatar': user.avatar})
    redpacket_data['amount'] = redpacket_data['amount'] / 100.0
    if current_user.is_authenticated:
        has_collect, value = RedPacket.has_collect(_id, current_user.open_id)
        challenge = RedPacketCollectLog.objects.filter(
            redpacket_id=bson.ObjectId(redpacket_id),
            open_id=current_user.open_id).count()
    else:
        has_collect, value = False, 0
        challenge = 0
    redpacket_data.update({'has_collect': has_collect, 'challenge': challenge,
                           'could_collect': redpacket.could_collect, 'value': value})

    logger.info('redpacket_data:%s' % (redpacket_id))

    redpacketlog = RedPacketLog.objects.filter(
        redpacket_id=bson.ObjectId(redpacket_id),
        status=RedPacketLog.STATUS_DONE
    ).order_by('-last_modify')
    userop = current_user.get_operator()
    redpacketlog_data = []
    for rpl in redpacketlog:
        data = rpl._data
        data.pop('_id')
        data.pop('redpacket_id')
        data.pop('status')
        data['value'] = data['value'] / 100.0
        challenge = RedPacketCollectLog.objects.filter(
            redpacket_id=bson.ObjectId(redpacket_id),
            open_id=data['open_id']).count()
        data.update({'rp_user': userop.get_info(data['open_id']), 'challenge': challenge})
        redpacketlog_data.append(data)
    logger.info('redpacket_log:%s' % (redpacket_id))

    rp_faillog = RedPacketCollectLog.objects.filter(redpacket_id=bson.ObjectId(redpacket_id))
    redpacketlogfail_data = []
    fail_openids = set()
    for rpfl in rp_faillog:
        fail_openids.add(rpfl.open_id)
    for open_id in fail_openids:
        if rp_faillog.filter(open_id=open_id, status=RedPacketCollectLog.STATUS_SUCCESS):
            continue
        failsobj = rp_faillog.filter(open_id=open_id).order_by('-last_modify')
        challenge = failsobj.count()
        create_time = formatter.time2str(failsobj.first().create_time)
        data = {'rp_user': userop.get_info(open_id), 'challenge': challenge, 'last_fail_time': create_time}
        redpacketlogfail_data.append(data)

    logger.info('redpacket_fail_log:%s' % (redpacket_id))

    return json_resp.success(
        data={'redpacket': redpacket_data, 'redpacketlog': redpacketlog_data,
              'redpacketlog_fail': redpacketlogfail_data})


@login_required
@packet.route('/create', methods=['POST', 'GET'])
def red_packet_create():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    token = request.args.get('token', '')
    args = request.form
    _id = bson.ObjectId()
    total_value = args.get('amount')
    number = args.get('number')
    title = args.get('title')
    level = args.get('level')
    poster = args.get('poster')
    try:
        postername = os.path.split(poster)[-1]
        posterurl = os.path.join(config.server_static_file, 'redpacket', postername)
        assert os.path.exists(posterurl)
    except AssertionError:
        # TODO 无图片则选择默认图片
        logger.error('can\'t find img: %s' % poster)
        return json_resp.failed(message='红包图片不存在')
    except:
        logger.error('invalid img path: %s' % poster)
        return json_resp.failed(message='图片地址不合法')

    try:
        amount = int(float(total_value) * 100)
        number = int(number)
        level = int(float(level))
    except:
        return json_resp.failed(message='invalid amount or number')
    if amount > current_user.capital:
        charge = amount - current_user.capital
        logger.info('%s余额不足, 需充值%s' % (current_user.open_id, charge))
        host = request.host_url.replace('http://', 'https://')
        url = host + url_for('order.order_create').strip('/') + '?token=%s' % token
        params = {'product_type': 1, 'pay_type': 0, 'amount': '%.2f' % (charge / 100.0)}
        logger.info('local request (%s,%s)' % (url, params))
        try:
            resp = requests.post(
                url=url, data=params, timeout=3,
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )
            logger.info('local request create order:%s' % resp.content)
            data = json.loads(resp.content).get('data')
        except Exception as e:
            logger.error('local request create order err: %s' % e)
            return json_resp.failed('创建订单失败')
        return json_resp.failed(data=data, code=-5)
    userop = current_user.get_operator()
    flag, msg = userop.change_capital(reason=CapitalLog.REASON_DELIVER, value=-amount)
    if not flag:
        return json_resp.failed(message=msg)

    rp_id = RedPacket.create_redpacket(current_user.open_id, amount, number, title, level, posterurl, _id)
    if not rp_id: return json_resp.failed(message=rp_id)
    CapitalLog.objects.filter(_id=msg).update_one(set__remark=str(rp_id))
    red_packet = RedPacket.get_packet(rp_id)
    data = red_packet._data
    data['amount'] = data['amount'] / 100.0
    return json_resp.success(data=data)


@login_required
@packet.route('/<redpacket_id>/collect', methods=['POST'])
def red_packet_collect(redpacket_id):
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    redpacket = RedPacket.get_packet(redpacket_id)
    userop = current_user.get_operator()
    if not redpacket:
        return json_resp.failed(message='红包不存在或已过期')
    open_id = current_user.open_id

    if not redpacket.could_collect:
        return json_resp.failed(message='红包已经被领光啦~')

    has_collect, value = RedPacket.has_collect(redpacket_id, open_id)
    if has_collect:
        return json_resp.failed(message='您已经领取过啦~', data={'value', value / 100.0})
    logger.info('collect redpcaket: %s_%s' % (open_id, redpacket_id))
    value, rpl_id = RedPacket.collect_redpacket(redpacket_id, open_id)
    if not value:
        return json_resp.failed('领取失败~')
    userop.change_capital(CapitalLog.REASON_COLLECT, value, str(rpl_id))
    try:
        redpacket.collect_report(open_id, RedPacketCollectLog.STATUS_SUCCESS, rpl_id)
    except:
        logger.error('collect success report faild(%s,%s)' % (open_id, rpl_id))

    redpacket = RedPacket.get_packet_all(redpacket_id)
    redpacket_data = redpacket._data
    redpacket_data.update({'user_nickname': current_user.nickname, 'user_avatar': current_user.avatar})
    redpacket_data['amount'] = redpacket_data['amount'] / 100.0
    has_collect = RedPacket.has_collect(redpacket_id, current_user.open_id) if current_user.is_authenticated else False
    redpacket_data.update({'has_collect': has_collect, 'could_collect': redpacket.could_collect})

    return json_resp.success(data={'value': value / 100.0, 'redpacket': redpacket_data})


@login_required
@packet.route('/<redpacket_id>/fail_report', methods=['POST'])
def red_packet_collect_report(redpacket_id):
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    redpacket = RedPacket.get_packet_all(redpacket_id)
    if not redpacket:
        return json_resp.failed(message='红包不存在')
    try:
        challenge = redpacket.collect_report(current_user.open_id, RedPacketCollectLog.STATUS_FAIL)
    except:
        challenge = 0
        logger.error('collect failed report faild(%s)' % (current_user.open_id))
    return json_resp.success(data={'challenge': challenge})
