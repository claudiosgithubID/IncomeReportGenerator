#!/usr/bin/python3
# draw.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-24 22:31:21
# Code:
'''
绘制图片
'''
import matplotlib as mpl
import seaborn as sns

mpl.font_manager.fontManager.addfont('resources/SimHei.ttf')
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


class Draw:
    def __init__(self, df):
        '''
        df:pandas的dataFrame对象
        '''
        self.df = df

    def for_all_modes(self):
        pass

    def for_cars_and_trucks(self):
        pass

    def for_in_vs_out(self):
        pass

    def for_primary(self):
        pass

    def _bar_for_primary(self):
        pass

    def _pie_for_primaty(self):
        pass
