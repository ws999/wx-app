# coding=utf-8
"""
@version: 2018/1/16 016
@author: Suen
@contact: sunzh95@hotmail.com
@file: interface
@time: 10:58
@note:  ??
"""
import random


class CreatePacketList(object):
    def _init_packet_random(self, total_value, number, max_value=None, min_value=None):
        """
        随机红包分配，传入max_value,min_value为不完全随机分配，否则为完全随机分配
        :param total_value: 随机分配的总金额
        :param number: 随机分配部分的总红包数
        :param max_value: 单个红包金额上限
        :param min_value: 单个红包金额下限
        :return: 
        """
        packet_list = []
        normal_list = self.normalvariate_list(total_value, number, max_value, min_value)
        s = sum(normal_list)
        for i in xrange(number):
            if i == number - 1:
                value = total_value - sum(packet_list)
            else:
                value = int(round(total_value * normal_list[i] / s))
            packet_list.append(value)
        return packet_list

    def normalvariate_list(self, total_value, number, max_value=None, min_value=None):
        """
        正态分布计算函数
        :param total_value: 
        :param number: 
        :param max_value: 
        :param min_value: 
        :return: 
        """
        normal_list = []
        max_ratio = 1.0 * number * max_value / total_value if max_value else 3.0
        min_ratio = 1.5 * number * min_value / total_value if min_value else 0
        for i in xrange(number):
            while True:
                normal_value = random.normalvariate(1, 0.5)
                if (normal_value > min_ratio) & (normal_value < max_ratio):
                    normal_list.append(normal_value)
                    break
        return normal_list

    def result(self, total_value, number, random_min=1):
        """
        外部调用
        :param total_value:总金额 
        :param number: 总数量
        :param kwargs: 分配规则
        :return: 红包列表
        """
        if random_min * number > total_value:
            return False, '单个红包金额必须大于%0.2f' % (random_min / 100.0)
        packet_list_random = self._init_packet_random(
            total_value, number, min_value=random_min)
        packet_list = packet_list_random[:]
        random.shuffle(packet_list)  # 打乱红包列表

        return True, packet_list


redpacketobj = CreatePacketList()

if __name__ == '__main__':
    print redpacketobj.result(1002, 100, 10)
