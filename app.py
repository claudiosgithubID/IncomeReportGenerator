#!/usr/bin/python3
# app.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-26 08:08:01
# Code:
'''
入口脚本
'''
import os
from context import vehiclesContext
from vehicles import Vehicles

excel_files_test = ['test_files/12月货车_测试.xlsx', 'test_files/12月客车_测试.xlsx']
excel_files = ['test_files/12月货车.xlsx', 'test_files/12月客车.xlsx']


def get_files():
    root = 'test_files/leshanbei_xls_fast'
    root = 'test_files/maoqiao01'
    list_of_files = []
    for root, dirs, files in os.walk(root):
        for f in files:
            list_of_files.append(os.path.join(root, f))
    return list_of_files


def main():
    print('读取数据和绘制图片时，内存占用较大，建议使用前关闭计算机上其他不必要的程序。')
    print('开始读取数据...')
    vehicles = Vehicles(get_files())
    print(f'共读取数据{vehicles.nrows_read}条，用时{vehicles.time_spent}秒')
    print(f'开始绘制图片，并生成Word文件...')
    outputfile = vehiclesContext(vehicles).rend()
    print(f'生成成功：{outputfile}')


if __name__ == '__main__':
    main()
