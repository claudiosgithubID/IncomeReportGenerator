#!/usr/bin/python3
# context.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-26 07:13:21
# Code:
'''
利用docxtpl渲染Word所需context
'''
import docx
import jinja2
from docxtpl import DocxTemplate, InlineImage
from filepath import filePath as fp

# 注册jinja2函数


def to_ch(int_):
    "将循环编号转换为汉字"
    ch = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    return ch[int_]


def to_letter(int_):
    '将循环编号转换为字母'
    letters = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    return letters[int_]


def to_circle(int_):
    circles = '⓪ ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩'.split()
    return circles[int_]


jinja_env = jinja2.Environment()
# jinja_env.trim_blocks = True
# jinja_env.lstrip_blocks = True
jinja_env.filters['to_ch'] = to_ch
# jinja_env.filters['to_letter'] = to_letter
# jinja_env.filters['to_circle'] = to_circle


class vehiclesContext:
    '''
    通过Vehicles对象，渲染Word模板
    '''

    def __init__(self, vehicles, template='template.docx'):
        self.vehicles = vehicles
        self.tpl = DocxTemplate(fp(template).as_template_file)
        self.context = {}
        self._title_and_overview()
        self._all_modes()
        self._cars_and_trcucks()
        self._in_vs_out()
        self._primary_out()
        self._primary_stations_3cats()
        self._primary_modes_details()
        self._topmost_plates()
        self._topmost_plates_of_primary_modes()
        self._no_source_fee()

    def _setk(self, key_value_dict):
        '''更新self.context中的数据
        '''
        for key in key_value_dict:
            self.context[key] = key_value_dict[key]

    def _remove_empty_lines(self, filename):
        '''
        docxtpl渲染结果暂时不知道怎样删除多余的空白行
        用python-docx集中全部删除
        '''
        def delete_paragraph(paragraph):
            p = paragraph._element
            p.getparent().remove(p)
            paragraph._p = paragraph._element = None

        document = docx.Document(filename)  # 打开
        for paragraph in document.paragraphs:
            if len(paragraph.text) == 0:
                if 'graphicData' not in paragraph._p.xml:  # 判断是否为单行图片
                    delete_paragraph(paragraph)
        document.save(filename)  # 关闭

    def rend(self):
        station = self.context['station']
        month_gap = self.context['month_gap']
        report_file = fp(
            f'{month_gap}{station}通行费收入分析.docx').as_report_file
        self.tpl.render(self.context, jinja_env)
        self.tpl.save(report_file)
        self._remove_empty_lines(report_file)
        return report_file

    def _register_fig(self, fig_path):
        return InlineImage(self.tpl, fig_path)

    def _title_and_overview(self):
        '标题和概述'
        self._setk({
            'month_gap': self.vehicles.month_gap,
            'station': self.vehicles.station,
            'total_fee': self.vehicles.total_fee,
            'daily_fee': self.vehicles.daily_fee
        })

    def _all_modes(self):
        '所有车型比较'
        fee_of_all_modes = self.vehicles.fee_of_all_modes
        fig_path = fee_of_all_modes['fig_path']
        fee_of_all_modes['fig'] = self._register_fig(fig_path)
        self._setk({'fee_of_all_modes': fee_of_all_modes
                    })

    def _cars_and_trcucks(self):
        '客车和货车各车型比较'
        fee_of_cars_and_trucks = self.vehicles.fee_of_cars_and_trucks
        for record in fee_of_cars_and_trucks:
            fig_path = record['fig_path']
            record['fig'] = self._register_fig(fig_path)
        self._setk({'fee_of_cars_and_trucks': fee_of_cars_and_trucks})

    def _in_vs_out(self):
        '所有车型省内省外比较'
        in_vs_out = self.vehicles.fee_of_in_vs_out_province_all_modes

        in_vs_out['fig'] = self._register_fig(in_vs_out['fig_path'])
        self._setk({'count_of_all_provinces': self.vehicles.count_of_all_provinces,
                    'in_vs_out': in_vs_out
                    })

    def _primary_out(self):
        '只要外省省份'
        primary_out = self.vehicles.fee_of_primary_out_provinces_all_modes
        primary_out['fig'] = self._register_fig(primary_out['fig_path'])
        self._setk({'primary_out': primary_out})

    def _primary_stations_3cats(self):
        primary_stations_3cats = self.vehicles.fee_of_primary_stations_3cats_of_all_modes
        for cat in primary_stations_3cats:
            total_count = cat['total_count']
            location = cat['cat']
            if location == '省内':
                count_of_stations_in = total_count
            if location == '省外':
                count_of_stations_out = total_count
            if location == '全国':
                count_of_all_stations = total_count

            fig_path = cat['fig_path']
            cat['fig'] = self._register_fig(fig_path)

        self._setk({'primary_stations_3cats': primary_stations_3cats})

    def _primary_modes_details(self):
        details = self.vehicles.fee_of_primary_modes_details
        for d in details:
            in_vs_out = d['in_vs_out']
            in_vs_out['fig'] = self._register_fig(in_vs_out['fig_path'])
            primary_out = d['primary_out']
            primary_out['fig'] = self._register_fig(primary_out['fig_path'])
            primary_stations_3cats = d['primary_stations_3cats']
            for cat in primary_stations_3cats:
                total_count = cat['total_count']
                location = cat['cat']
                if location == '省内':
                    count_of_stations_in = total_count
                if location == '省外':
                    count_of_stations_out = total_count
                if location == '全国':
                    count_of_all_stations = total_count

                fig_path = cat['fig_path']
                cat['fig'] = self._register_fig(fig_path)

        self._setk({'primary_mode_threhold': self.vehicles.primary_mode_threhold,
                    'primary_modes': self.vehicles.primary_modes,
                    'primary_modes_details': details})

    def _topmost_plates_of_primary_modes(self):
        mode_details = self.vehicles.fee_of_topmost_plates_of_primary_modes
        for m in mode_details:
            m['fig'] = self._register_fig(m['fig_path'])
        self._setk({'topmost_plates_of_primary_modes': mode_details,
                    'topmost_plates_count': self.vehicles.topmost_plates_count
                    })

    def _topmost_plates(self):
        topmost_plates = self.vehicles.fee_of_topmost_plates
        fig_path = topmost_plates['fig_path']
        topmost_plates['fig'] = self._register_fig(fig_path)
        self._setk({'topmost_plates': topmost_plates,
                    'topmost_plates_count': self.vehicles.topmost_plates_count
                    })

    def _no_source_fee(self):
        self._setk({'no_source_fee': self.vehicles.no_source_fee})


if __name__ == '__main__':
    for i in range(11):
        print(to_ch(i))
