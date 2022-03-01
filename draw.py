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
from d import D
from decimal import Decimal
from filepath import filePath as fp
from matplotlib import pyplot as plt

mpl.font_manager.fontManager.addfont(fp('SimHei.ttf').as_resource_file)
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.transparent'] = True

mpl.rcParams['savefig.dpi'] = 1000
# mpl.rcParams['savefig.pad_inches'] = 0.01
sns.set(font='SimHei', style='white', context='paper')

mpl.rcParams['figure.max_open_warning'] = False


class Draw:
    FW = 10                     # Word横向放置适合很跨整个页面的宽度

    def __init__(self, df, fig_path):
        '''
        df:pandas的dataFrame对象
        '''
        self.df = df
        self.fig_path = fig_path

    def for_all_modes(self):
        df = self.df.sort_values(by='fee', ascending=False)
        fig, ax = plt.subplots(figsize=(self.FW, 1.7))
        sns.barplot(ax=ax, data=df, x='mode', y='fee')
        sns.despine()
        ax.set(xlabel='', ylabel='通行费（万元）')
        ax.bar_label(ax.containers[0], df['fee'].map(
            lambda f: f'{f:.2f}').to_list())
        fig.savefig(self.fig_path)

    def for_cars_and_trucks(self):
        df = self.df.sort_values(by='fee', ascending=False)
        nrows = df.shape[0]
        fig, ax = plt.subplots(figsize=(self.FW/2, (nrows+1)*0.46))
        sns.barplot(ax=ax, data=df, x='fee', y='mode', orient='h')
        sns.despine(right=True, bottom=True)
        ax.xaxis.set_label_position('top')
        ax.set(ylabel='', xlabel='通行费（万元）')
        ax.xaxis.tick_top()
        ax.bar_label(ax.containers[0], df['fee'].map(
            lambda f: f'{f:.2f}').to_list())
        fig.savefig(self.fig_path)

    def for_in_vs_out(self):
        cats, pers = [], []
        for record in self.df.to_dict('records'):
            cats.append(record['province'])
            pers.append(record['per'])
        colors = sns.color_palette(n_colors=2)

        fig, ax = plt.subplots(figsize=(self.FW/2, 1.8))
        wedget, texts, autotexts = ax.pie(
            pers, autopct='%1.2f%%', colors=colors)
        ax.legend(wedget, cats, loc=(1.04, 0))
        fig.savefig(self.fig_path)

    def for_primary(self):
        nrows = self.df.shape[0]
        if nrows >= 6:
            self._bar_for_primary()
        else:
            self._pie_for_primary()

    def _bar_for_primary(self):
        '''
        主要外省省份，和主要入口收费站
        '''
        df = self.df.sort_values(by='fee', ascending=False)
        nrows = df.shape[0]
        if 'province' in df.columns:
            x = 'province'
        else:
            x = 'station'
        fig, ax = plt.subplots(figsize=(self.FW, 3))
        sns.barplot(ax=ax, data=df, x=x,  y='fee')
        sns.despine()
        ax.set(xlabel='', ylabel='通行费（万元）')
        # 根据数据条数决定是否在bar上添加数值
        if nrows <= 15:
            ax.bar_label(ax.containers[0], df['fee'].map(
                lambda f: f'{f:.2f}').to_list())
        # 根据xticksi字符串是否过长，设置倾斜
        if df[x].str.len().max() >= 4:
            labels = ax.get_xticklabels()
            plt.setp(labels, rotation=80,
                     horizontalalignment='center',
                     fontsize='smaller')

        fig.savefig(self.fig_path)

    def _pie_for_primary(self):
        df = self.df.sort_values(by='fee', ascending=False)
        nrows = df.shape[0]
        colors = sns.color_palette(n_colors=nrows)

        if 'province' in df.columns:
            cat = 'province'
        else:
            cat = 'station'
        cats, pers = [], []
        for record in df.to_dict('records'):
            cats.append(record[cat])
            pers.append(record['per'])
        total_per = D(df['per']).sum()
        diff = D.minus(100, total_per)
        if diff > Decimal('0'):
            pers.append(float(diff))
            cats.append('其他')
            colors = sns.color_palette(n_colors=nrows+1)

        fig, ax = plt.subplots(figsize=(self.FW, 3))
        wedget, text, autotexts = ax.pie(pers, autopct='%1.2f%%')
        ax.legend(wedget, cats, loc=(1.04, 0))
        fig.savefig(self.fig_path)

    def for_topmost_plates(self):
        df = self.df.sort_values(by='fee', ascending=False)
        nrows = df.shape[0]
        fig, ax = plt.subplots(figsize=(self.FW, 3))
        sns.barplot(ax=ax, data=df, x='plate',  y='fee')
        sns.despine()
        ax.set(xlabel='', ylabel='通行费（元）')
        # 根据数据条数决定是否在bar上添加数值
        ax.bar_label(ax.containers[0],
                     df['count'].to_list(),
                     label_type='edge')

        # 设置倾斜
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=80,
                 horizontalalignment='center',
                 fontsize='smaller')

        fig.savefig(self.fig_path)
