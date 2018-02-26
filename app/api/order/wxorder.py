# coding=utf-8
"""
@version: 2018/1/18 018
@author: Suen
@contact: sunzh95@hotmail.com
@file: pay
@time: 16:26
@note:  ??
"""
from __future__ import unicode_literals

import datetime
from flask import request
from flask_login import current_user, login_required
from app.models import UserOrder, CapitalLog, User
from interface import wxpay
from interface.order import order_interface
from flask_ext import json_resp
from config import config

logger = config.logger
from app.api.order import order


@login_required
@order.route('/pay/create', methods=['POST'])
def order_create():
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    open_id = current_user.open_id
    args = request.form.to_dict()
    logger.info('[create_order] %s' % (args))
    product_type = args.pop('product_type', '')
    pay_type = args.pop('pay_type', '')
    amount = args.pop('amount', '')
    try:
        product_type = int(product_type)
        pay_type = int(pay_type)
    except:
        return json_resp.failedByParameter('product_type and pay_type should be int')
    try:
        amount = int(float(amount) * 100)
    except:
        return json_resp.failedByParameter('amount should be float')

    # 1.产品订单接口类
    order_iface = order_interface.get_order_iface(product_type)
    if not order_iface:
        return json_resp.failed(message='unknown product_type')
    # 2.生成订单号
    order_no = order_iface.general_order_no(pay_type)
    if not order_no:
        return json_resp.failed(message='unknown pay_type')
    # 3.创建订单
    try:
        data = order_iface.create(open_id, product_type, order_no, pay_type, amount=amount)
    except Exception as e:
        return json_resp.failed(message=str(e))

    result_data = {'order_no': order_no}
    if pay_type == UserOrder.PAY_TYPE_WX:  # 微信
        wxpay_order = wxpay.create_unifiedorder(
            data['title'], order_no, int(data['price_pay']), open_id,
            spbill_create_ip=request.environ.get('REMOTE_ADDR')
        )
        logger.info('wxpay_order:%s' % wxpay_order)
        wxpay_jsapi_args = wxpay.get_jsapi_request_args(wxpay_order['prepay_id'])
        result_data['wxpay_jsapi_args'] = wxpay_jsapi_args

    return json_resp.success(data=result_data)


@order.route('/pay/notify', methods=['POST'])
def order_notify():
    args = wxpay.to_dict(request.get_data())
    logger.info('[wxpay-notify]' + str(args))
    try:
        assert args.get('return_code', '') == 'SUCCESS'
        logger.info('return code: success')
        order_iface = order_interface.get_order_iface(order_no=args.get('out_trade_no', ''))
        if order_iface:
            logger.info('out_trade_no: %s' % args.get('out_trade_no', ''))
        pay_time = datetime.datetime.strptime(args.get('time_end', ''), '%Y%m%d%H%M%S')
        result = order_iface.set_success(args.get('out_trade_no', ''), pay_time, args)
        if not result:
            logger.error('set_success error')
        number, order_id, open_id = result
        user = User.objects.filter(open_id=open_id).first()
        assert user
    except Exception as e:
        logger.error('wxpay-notify failed: %s\n%s' % (args, e))
    else:
        user.change_capital(CapitalLog.REASON_CHARGE, number, order_id)
    return wxpay.to_xml({'return_code': 'SUCCESS', 'return_msg': 'OK'})


@login_required
@order.route('/<order_no>/status', methods=['GET'])
def pay_status(order_no):
    if not current_user.is_authenticated:
        return json_resp.failedByUnauthenticated()
    flag, result = order_interface.status(order_no, current_user.open_id)
    if not flag:
        return json_resp.failed(message=result)
    return json_resp.success(data={'status': result})
