#!/usr/bin/python3
# gui.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-26 15:11:25
# Code:
'''
图形界面
'''
from filepath import filePath as fp
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget


class IncomeReportGeneratorAPP(App):
    pass


class MainWidget(Widget):
    pass


class BoxLayoutExample(BoxLayout):
    pass


'''    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        b1 = Button(text='A')
        b2 = Button(text='B')
        b3 = Button(text='C')
        self.add_widget(b1)
        self.add_widget(b2)
        self.add_widget(b3)
'''


if __name__ == '__main__':
    IncomeReportGeneratorAPP().run()
