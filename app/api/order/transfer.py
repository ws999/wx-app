# coding=utf-8
"""
@version: 2018/1/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: wxtransfer
@time: 15:06
@note:  ??
"""

from __future__ import unicode_literals

import datetime
from flask_login import current_user, login_required
from flask import request

from app.models import CapitalLog
from interface import wxtransfer
from interface.order import order_interface
from app.api.order import order
from flask_ext import json_resp
from config import config

logger = config.logger


@login_required
@order.route('/transfer/request', methods=['POST'])
def transfer_wx():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    open_id = current_user.open_id
    args = request.form.to_dict()
    if not args: args = request.args.to_dict()
    pay_type = args.pop('pay_type', '')
    product_type = args.pop('product_type', '')
    amount = args.pop('amount', '')
    try:
        pay_type = int(pay_type)
        product_type = int(product_type)
        amount = int(float(amount) * 100)
    except:
        return json_resp.failedByParameter('amount, pay_type and product_type should be int')

    # 1.产品订单接口类
    order_iface = order_interface.get_order_iface(product_type)
    if not order_iface:
        return json_resp.failed(message='unknown product_type')

    # 2.生成订单号
    order_no = order_iface.general_order_no(pay_type)
    if not order_no:
        return json_resp.failed(message='unknown pay_type')
    try:  # 创建订单
        data = order_iface.create(open_id, product_type, order_no, pay_type, amount=amount)
        # 生成请求参数
        request_body = wxtransfer.get_transfer_args(
            order_no, amount, open_id, data.get('desc', '红包余额提取到微信'),
            spbill_create_ip=request.environ.get('REMOTE_ADDR'))
    except Exception as e:
        return json_resp.failed(message=str(e))
    # 扣除红包账户余额
    logger.info('扣除 %s 账户余额 %s' % (open_id, amount))
    userop = current_user.get_operator()
    flag, cl_id = userop.change_capital(CapitalLog.REASON_TOCASH, -amount)
    if not flag:
        logger.error('扣除失败 %s 账户余额失败 %s' % (open_id, amount))
        return json_resp.failed(message='账户余额不足')
    # 请求wx remote
    flag, msg = wxtransfer.request_transfer(request_body)
    if not flag:
        logger.error('提现失败(%s,%s)' % (open_id, amount))
        return json_resp.failed(message='提现失败,如余额已扣除请联系客服')
    # 更新关联信息
    flag, order_id = order_iface.set_success(order_no, datetime.datetime.now(), msg)
    if not flag:
        logger.error('关联信息更新失败(%s,%s,%s)' % (order_no, datetime.datetime.now(), msg))
        return json_resp.success(data={'amount': amount / 100.0, 'status': 'SUCCESS'})
    CapitalLog.objects.filter(_id=cl_id).update_one(set__remark=str(order_id))
    return json_resp.success(data={'amount': amount / 100.0, 'status': 'SUCCESS'})
