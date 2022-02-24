#!/usr/bin/python3
# file_util.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-24 22:01:14
# Code:
'''
文件夹，文件路径工具
'''
import os


class filePath:
    '''
    文件，文件夹路径工具
功能：
1.
    '''

    def __init__(self, fname):
        '''fname:文件名
        '''
        self.fname = fname

        self.resources_folder = self.make_dir('resources')
        self.images_folder = self.make_dir('images')
        self.templates_folder = self.make_dir('templates')
        self.reports_folder = self.make_dir('reports')

    @classmethod
    def make_dir(cls, dirname):
        '''在当前文件夹内新建文件夹，如果存在忽略
        '''
        cwd = os.getcwd()
        folder = os.path.join(cwd, dirname)
        os.makedirs(folder, exist_ok=True)
        return folder

    # 用lisp的Macro是否就可以不重复定义下面模式相同的函数
    @property
    def as_image_file(self):
        return os.path.join(self.images_folder, self.fname)

    @property
    def as_resource_file(self):
        return os.path.join(self.resources_folder, self.fname)

    @property
    def as_template_file(self):
        return os.path.join(self.templates_folder, self.fname)

    @property
    def as_report_file(self):
        return os.path.join(self.reports_folder, self.fname)


if __name__ == '__main__':
    fname = 'xxxx'
    print(filePath(fname).as_resource_file)
    print(filePath(fname).as_image_file)
    print(filePath(fname).as_template_file)
    print(filePath(fname).as_report_file)
