# coding=utf-8
"""
@version: 2018/2/5 005
@author: Suen
@contact: sunzh95@hotmail.com
@file: user
@time: 16:25
@note:  ??
"""
import datetime

from app.models.capital import CapitalLog, Capital
from app.models.redpacket import RedPacket, RedPacketLog
from services import formatter
from config import config

logger = config.logger


class UserOperator(object):
    def __init__(self, user_ins=None, user_cls=None):
        self.proto_ins = user_ins
        self.proto_cls = user_cls

    def set_info(self, user_id, nickname=None, avatar=None, gender=None, province=None, city=None, intro=None):
        user_id = formatter.str2objectid(user_id)
        info = dict(nickname=nickname, avatar=avatar, gender=gender, province=province, city=city, intro=intro)
        user = self.proto_cls.objects.filter(_id=user_id).first()
        if not user:
            logger.error(msg='set user info err:%s' % (user_id))
            return False
        r = user.modify({}, **info)
        return 1 if r else False

    def get_info(self, open_id):
        user = self.proto_cls.objects.filter(open_id=open_id).first()
        if not user:
            return {}
        data = user.info
        info = dict(nickname=data.pop('nickname'), avatar=data.pop('avatar'), gender=data.pop('gender'))
        return info

    def capital_log(self, page, per_page):
        capital_log, page, total, count = CapitalLog.find_page(
            open_id=self.proto_ins.open_id,
            page=page, per_page=per_page,
            order_by='-create_time')

        result = []
        for cl in capital_log:
            data = cl._data
            data.pop('_id')
            data.pop('open_id')
            data.pop('remark')
            data['create_time'] = formatter.time2str(data['create_time'])
            result.append(data)
        return result, count, total

    def redpacket_in_log(self, page, per_page):
        redpacket_log, page, total, count = RedPacketLog.find_page(
            open_id=self.proto_ins.open_id,
            page=page, per_page=per_page,
            order_by='-last_modify')
        result = []
        for rpl in redpacket_log:
            data = rpl._data
            data['value'] = data['value'] / 100.0
            data.pop('open_id')
            data.pop('status')

            rp_id = data.pop('redpacket_id')
            rp = RedPacket.objects.filter(_id=rp_id).first()
            rp_info = dict(
                redpacket_id=str(rp_id),
                title=rp.title,
                amount=rp.amount / 100.0,
                count=rp.count,
                create=formatter.time2str(rp.create_time))
            data.update(rp_info)

            result.append(data)
        return result, count, total

    def redpacket_out_log(self, page, per_page):
        redpacket, page, total, count = RedPacket.find_page(
            open_id=self.proto_ins.open_id, page=page,
            per_page=per_page, order_by='-create_time')
        result = []
        for rp in redpacket:
            data = rp._data
            data.pop('open_id')
            data['amount'] = data['amount'] / 100.0
            data['create_time'] = formatter.time2str(data['create_time'])
            data['expire_time'] = formatter.time2str(data['expire_time'])
            result.append(data)
        return result, count, total

    def change_capital(self, reason, value, remark=''):
        open_id = self.proto_ins.open_id
        if reason in (CapitalLog.REASON_CHARGE, CapitalLog.REASON_COLLECT):
            flag, result = Capital.add_capital(open_id, value)
            sign = 1
        elif reason in (CapitalLog.REASON_DELIVER, CapitalLog.REASON_TOCASH):
            flag, result = Capital.reduce_capital(open_id, value)
            sign = 0
        else:
            return False,
        if not flag:
            logger.error('change_capital_err:%s_%s' % (open_id, value))
            return False, result
        after_value = result.get('value')
        data = CapitalLog(
            open_id=open_id,
            reason=reason,
            sign=sign,
            value=abs(value),  # 这里只存正值,正负号存在sign
            after_value=after_value,
            remark=remark,
            create_time=datetime.datetime.now()
        )
        result = CapitalLog.objects.insert(data)
        logger.info('change_capital_success:%s_%s' % (open_id, value))
        return True, result.pk
