#!/usr/bin/python3
# paint.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-07 00:27:24
# Code:
'''
画图代码
'''
import matplotlib as mpl
import matplotlib.pyplot as plt
import render_get as get

# 设置显示中文
# 中文显示
mpl.font_manager.fontManager.addfont('resources/SimHei.ttf')
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

FW = 8  # full width 缩写 全屏宽度


mpl.style.use('ggplot')
mpl.rcParams['savefig.dpi'] = 1000  # 测试用100,实际使用时用1000

nn


def bar_for_full_width(rows, image_path, title,
                       ylabel='通行费（万元）',
                       figsize=(FW, 3.0)):
    '''
    根据Row对象链表画柱函数，返回image_path,方便docxtpl注册图片
所有柱状图的共同特点：
1.横跨整行
不同点：
1.y_label。除主要车辆为元外，都为万元。通过y_label参数控制
2.bar_label：是否添加。函数内控制，当数据条数大于12时，不添加。
3.x_ticks:是否旋转。函数内控制，当数据条数大于12时，旋转
旋转程度由数据条数控制。

'''
    def get_max_len_of_cats(cats):
        '获取字符串链表中最长字符串的长度'
        max_len = 0
        for c in cats:
            len_c = len(c)
            if len_c > max_len:
                max_len = len_c
        return max_len

    cats, amounts, pers = get_data_from_rows(rows)
    too_many = False              # 数据条数是否过多，据此改变图像。
    data_len = len(cats)
    if data_len >= 15:
        too_many = True
    fig, ax = plt.subplots(figsize=figsize)
    b = ax.bar(cats, amounts)
    ax.set(title=title, ylabel=ylabel)
    # 如果柱子不多，在上面加上数量说明
    if not too_many:
        ax.bar_label(b, map(lambda a: f'{a:.2f}', amounts))

    # 如果字符串过长，倾斜显示，方便观看
    if get_max_len_of_cats(cats) > 2:
        angle = data_len * 2    # 待调试
        angle = 80
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=angle,
                 horizontalalignment='center',
                 fontsize='smaller')

    fig.subplots_adjust(bottom=0.4)  # 使其有更多空间显示下面的文字
    fig.savefig(image_path)
    return image_path


def barh_for_cars_and_trucks(rows, image_path, title):
    '''
    为各车型比较定制的简化_bar版本
'''
    cats, amounts, pers = get_data_from_rows(rows)
    fig, ax = plt.subplots(figsize=(FW/2, 2.6))
    cats.reverse()
    amounts.reverse()
    b = ax.barh(cats, amounts)
    ax.xaxis.tick_top()
    ax.bar_label(b, map(lambda a: f'{a:.2f}', amounts))
    fig.savefig(image_path)
    return image_path


def pie_for_in_vs_out_province(rows, image_path, title):
    '对Row对象链表画饼图'
    cats, amounts, pers = get_data_from_rows(rows)
    total_pers = get.reduce_rows_per(rows)
    fig, ax = plt.subplots(figsize=(FW/2, 1.8))
    wedget, texts, autotexts = ax.pie(pers, autopct='%1.2f%%')
    ax.legend(wedget, cats,  loc=(1.04, 0))
    fig.savefig(image_path)
    return image_path


def for_primary(rows, image_path, title, ylabel='通行费（万元）'):
    '''当获取主要占比的数据时，会出现数据过少的情况。
若数据量<=5:绘制饼图，否则绘制柱状图
'''
    row_count = len(rows)
    if row_count <= 5:
        return pie_for_primary(rows, image_path, title)
    return bar_for_primary(rows, image_path, title, ylabel=ylabel)


def pie_for_primary(rows, image_path, title):
    '横跨横个文档的饼图'
    cats, amounts, pers = get_data_from_rows(rows)
    total_pers = get.reduce_rows_per(rows)
    diff = 100 - total_pers
    if diff > 0:
        cats.append('其它')
        pers.append(diff)
    fig, ax = plt.subplots(figsize=(FW, 3))
    # ax.set_title(title, loc='left', pad=-1)
    wedget, texts, autotexts = ax.pie(pers, autopct='%1.2f%%')
    ax.legend(wedget, cats,  loc=(1.04, 0))
    fig.savefig(image_path)
    return image_path


def bar_for_primary(rows, image_path, title, ylabel='通行费（万元）'):
    return bar_for_full_width(rows, image_path, title, ylabel=ylabel)


def get_data_from_rows(rows):
    '通过Row对象的链表获取plot需要的数据，'
    result = {'cats': [], 'amounts': [], 'pers': []}
    for row in rows:
        result['cats'].append(row.cat)
        result['amounts'].append(row.amount)
        result['pers'].append(row.per)
    return result['cats'], result['amounts'], result['pers']


if __name__ == '__main__':
    import db_helper
    import render_get as get
    import sqlite3 as sql
    con = sql.connect('test.db')
    cur = con.cursor()
    con.create_aggregate('mysqlsum', 1, db_helper.MySQLSum)
    con.create_function('mysqldivide', 2, db_helper.mysqldivide)
    # topmost = get.topmost_plates(cur)[0]
    # print(get_max_len_of_cats(['1', '1234', '12']))
