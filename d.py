#!/usr/bin/python3
# d.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-21 23:33:57
# Code:
'''
利用decimal模块计算panda的series对象
'''
from decimal import ROUND_HALF_UP, Decimal
from functools import reduce


class D:
    '''
    decimal模块计算费用
对pandas的Series进行操作
'''

    def __init__(self, series):
        '''
        series:pandas的Series对象,内部数据为字符串
        '''
        self.series = series

    @classmethod
    def is_mumber(cls, x):
        '是否为int或float类型'
        return isinstance(x, (int, float))

    @classmethod
    def is_digit_str(cls, string):
        '是否为int或float类型的字符串'
        return string.replace('.', '1', 1).isdigit()

    @classmethod
    def to_decimal(cls, x):
        '转换为Decimal对象，仅支持float或int,或float,int字符串'
        if isinstance(x, Decimal):
            return x
        elif cls.is_mumber(x):
            return Decimal(str(x))
        elif cls.is_digit_str(x):
            return Decimal(x)
        else:
            return x

    @classmethod
    def divide(cls, up, below):
        'decimal除法,返回Decimal对象'
        return cls.to_decimal(up) / cls.to_decimal(below)

    @classmethod
    def scale(cls, x, times=10000):
        '将x缩小times倍，返回Decimal对象'
        return cls.to_decimal(x)/Decimal(str(times))

    @classmethod
    def round(cls, x, ndigits=2):
        '将x保留ndigit位小数，返回decimal对象'
        ndigits_str = '0.'
        if ndigits <= 0:
            ndigits_str = '0'
        else:
            for i in range(ndigits):
                ndigits_str += '0'
        return cls.to_decimal(x).quantize(
            Decimal(ndigits_str),
            rounding=ROUND_HALF_UP)

    @classmethod
    def minus(cls, head, tail):
        '利用decimal:head - tail返回Decimal对象'
        return cls.to_decimal(head) - cls.to_decimal(tail)

    def _sum(self):
        '''
        对pandas的series进行累加
        '''
        return reduce(lambda x, y: x+self.to_decimal(y), self.series, Decimal('0'))

    def sum(self, scale=False, rounding=False):
        '''求Series对象的总和，支持缩放和默认保留两位小数
        '''
        dresult = self._sum()
        if scale:
            dresult = self.scale(dresult)
        if rounding:
            dresult = self.round(dresult)
        return float(dresult)

    def per(self, total, rounding=True):
        '''根据总量total，计算Series总和的占比
        默认放大100倍，保留两位小数
        '''
        amount = self._sum()
        dresult = self.divide(amount, total)
        dresult = self.scale(dresult, 0.01)
        if rounding:
            dresult = self.round(dresult)
        return float(dresult)


if __name__ == '__main__':
    print(D.divide(1, 3))
