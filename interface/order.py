# coding=utf-8
"""
@version: 2017/3/28
@author: Suen
@contact: sunzh95@hotmail.com
@file: order
@time: 14:11
@note:  ??
"""
import time
import datetime
import random
from pip.utils import cached_property
from app.models import UserOrder, User
from config import config

logger = config.logger


class OrderInterface(object):
    SUPPORT_PAY_WAY = []

    @cached_property
    def iface_charge(self):
        return RedpacketOrderInterface()

    @cached_property
    def iface_transfer(self):
        return TransferOrderInterface()

    def get_order_iface(self, product_type='', order_no=''):
        """
        获取订单操作类
        :param product_type:参照UserOrder.PRODUCT_TYPE_*
        :return:
        """
        if order_no:
            order = UserOrder.objects.filter(order_no=order_no).first()
            if not order: return
            product_type = order.product_type

        if product_type in (UserOrder.PRODUCT_TYPE_REDPACKET,):
            return self.iface_charge
        elif product_type == UserOrder.PRODUCT_TYPE_WX:
            return self.iface_transfer
        return

    def general_order_no(self, pay_type):
        """
        生成订单号
        :param pay_way:支付方式
        :return: str
        """
        if pay_type not in self.SUPPORT_PAY_WAY:
            return ''
        if pay_type == UserOrder.PAY_TYPE_WX:
            return 'wx%s%s' % (str(int(time.time() * 1000)), str(random.randint(1000, 9999)))
        elif pay_type == UserOrder.PAY_TYPE_REDPACKET:
            return 'rptransfer%s%s' % (str(int(time.time() * 1000)), str(random.randint(1000, 9999)))
        return ''

    def create(self, user_mobile, product_type, order_no, pay_way, **kwargs):
        raise Exception('need override')

    def set_success(self, order_no, pay_time, third_msg=None):
        raise Exception('need override')

    def status(self, order_no, open_id):
        order = UserOrder.objects.filter(open_id=open_id, order_no=order_no).first()
        if not order:
            return False, 'order not found'
        status = order.status
        return True, status


class RedpacketOrderInterface(OrderInterface):
    SUPPORT_PAY_WAY = [UserOrder.PAY_TYPE_WX]
    LIMIT_INFO = ""

    def get_product_dict(self, amount):
        data = dict(charge_value=amount, price_pay=int(amount * config.CHARGE_RATE / 100.0), price_origin=amount)
        return data

    def create(self, open_id, product_type, order_no, pay_type, **kwargs):
        amount = kwargs.get('amount')
        if not amount:
            logger.error('charge value error')
            raise Exception('charge value error')
        product = self.get_product_dict(amount)
        ol = UserOrder(
            open_id=open_id,
            order_no=order_no,
            status=UserOrder.STATUS_UNPAY,
            create_time=datetime.datetime.now(),
            pay_time=None,
            pay_type=pay_type,
            product_type=product_type,
            product_value=product['charge_value'],
            product_num=1,
            price_origin=product['price_origin'],  # 应付产品价格, 分
            price_pay=product['price_pay']  # 实际支付, 分
        )
        UserOrder.objects.insert(ol)
        return dict(order_no=order_no, title="充值%0.2f" % (product['charge_value'] / 100.0),
                    price_pay=product['price_pay'])

    def set_success(self, order_no, pay_time, third_msg=None):
        """
        :param order_no:订单编号
        :param third_msg: 第三方报文
        """
        order = UserOrder.objects.filter(order_no=order_no).first()
        if not order:
            logger.error('[order not found]' + order_no)
            raise Exception('[order not found]' + order_no)
        user = User.objects.filter(open_id=order.open_id).first()
        if not user:
            logger.error('[user not found]' + order_no)
            raise Exception('[user not found]' + order_no)

        if order.status == UserOrder.STATUS_PAID:
            logger.info('[order_no:%s] already notify' % order_no)
            return
        logger.info('start to modify')
        modify = dict(set__status=UserOrder.STATUS_PAID, set__pay_time=pay_time, set__order_msg=third_msg)
        order.modify({}, **modify)
        logger.info('wxpay-notify success: %s' % order_no)
        number = order.product_value

        return number, order.pk, order.open_id


class TransferOrderInterface(OrderInterface):
    SUPPORT_PAY_WAY = [UserOrder.PAY_TYPE_REDPACKET]
    LIMIT_INFO = ""

    def create(self, open_id, product_type, order_no, pay_type, **kwargs):
        amount = kwargs.get('amount', '')
        ol = UserOrder(
            open_id=open_id,
            order_no=order_no,
            status=UserOrder.STATUS_UNPAY,
            create_time=datetime.datetime.now(),
            pay_time=None,
            pay_type=pay_type,
            product_type=product_type,
            product_value=amount,
            product_num=1,
            price_origin=amount,  # 应付产品价格,分
            price_pay=amount,  # 实际支付,分
        )
        UserOrder.objects.insert(ol)
        return dict(order_no=order_no, desc="红包余额%.2f提取到微信钱包" % (amount / 100.0),
                    price=amount)

    def set_success(self, order_no, pay_time, third_msg=None):
        """
        :param order_no:订单编号
        :param third_msg: 第三方报文
        """
        order = UserOrder.objects.filter(order_no=order_no).first()
        if not order:
            logger.error('[order not found]' + order_no)
            return False, '[order not found]' + order_no
        user = User.objects.filter(open_id=order.open_id).first()
        if not user:
            logger.error('[user not found]' + order_no)
            return False, '[user not found]' + order_no

        if order.status == UserOrder.STATUS_PAID:
            logger.info('[order_no:%s] already notify' % order_no)
            return False, '[order_no:%s] already notify' % order_no
        modify = dict(set__status=UserOrder.STATUS_PAID, set__pay_time=pay_time, set__order_msg=third_msg)
        order.modify({}, **modify)

        return True, order.pk


order_interface = OrderInterface()
