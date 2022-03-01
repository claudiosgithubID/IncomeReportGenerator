#!/usr/bin/python3
# vehicles.py
# Author: Claudio <3261958605@qq.com>
# Created: 2022-02-17 09:07:02
# Code:
'''
车辆信息处理
'''


import numpy as np
import pandas as pd
from d import D
from datetime import datetime
from decimal import Decimal
from draw import Draw
from filepath import filePath as fp
from timeit import default_timer as timer


class Vehicles:
    '''车辆信息关系表，从Excel文件中获取渲染Word所需数据。

输入数据：一个或多个Excel文件。
输出数据：
一，单值：
1.total_fee:通行费总额，单位万元，保留2位小数
2.daily_fee:日均通行费，单位万元，保留2位小数
3.month_gap:XXXX年XX月，说明Excel文件中数据所在日期的文字
4.station:：当前收费站名称。
5.no_source_fee:无入口信息的通行费，单位元，保留2位小数
二，复合数据
1.fee_of_all_modes：所有车型通行费，及总占比
    数据结构dict{'rows':rows, fig_path:图片路径},按车型排序
    rows为list，单个元素为dict：{'mode':'一客', 'fee':通行费，万元, 'per':通行费总占比}
    按车型由小到大排序。
2.fee_of_cars_and_trucks：客车和货车通行费比较
    数据结构list[{'mode':'客车', 'fig_path':, 'rows':}
    rows为list，单个元素为dict：{'mode':'一客', 'fee':, 'per'}
3.provinces_count:（所有，或主要车型车型）省份个数
4.fee_of_province_in_vs_out：省内/省外通行费对比
    数据结构dict{'rows':,'fig_path':}
    单个row为dict{'province':'省内', 'fee':,'per':}
5.fee_of_primary_out_provinces：主要外省省份通行费数据
    数据结构dict{'count':省份个数,'fee':, 'per':,'fig_path':, 'rows':}
    rows：按通行费排序
    单个row为dict{'province':'云南', 'fee':, 'per'}
6.fee_of_primary_stations_3cats:全国，省内，省外主要入口收费站数据，返回list
    如_get_fee_of_primary_stations(mode=(1,16, province='all'))：全国主要入口收费站数据
    按通行费排序
    数据类型为dict{'cat':'全国', 'total_count':：全国收费站数量,
                 'count':主要收费站数量, 'fee':, 'per':, 'fig_path',
                  'rows':}
    rows为list，单个数据为{'station':,'fee':,'per':}
7.fee_of_primary_mode_details:主要车型进一步分析，包含上面所有的入口站省份和入口站的所有数据。
    返回list，按车型通行费多少排序，单个元素为dict：
    {
    'mode':'一客',
    'provinces_count':,
    'in_vs_out':,
    'primary_out':,
    'primary_stations_3cats'
    从key值可推测出对应的上面函数数据，及数据结构
    }
8.fee_of_topmost_plates_of_primary_modes:所有车型主要车牌的数据
    返回list，单个元素为dict：{'mode':'一客’, fig_path:,'fee':, 'per':当前车型中通行费的占比,rows:}
    rows按通行费排序
    单个row为dict{'plate':, 'fee':, 'per':在当前车型中的占比}

9.fee_of_topmost_plates:所有车辆中，通行费排序最前的车牌。当无主要车型时使用
    返回：dict{'fee':, 'per':'rows':}
    rows同上，只是占比为所有通行费中的占比

代码结构：
1._get_fee_by_group(self, frame, by)
    按不同分组by，获取frame中fee列的总和，及在frame中所有fee总和的占比
    由此衍生出：
    _get_fee_by_mode->_fee_of_trucks, _fee_of_cars->fee_of_cars_vs_trucks
    fee_of_primary_out_provinces
    fee_of_primary_stations_3cats
    fee_of_stations
    fee_of_topmost_plates
2.normalize_per(cls, per_col)
    对per_col整列和为100的值进行调整，使四舍五入后的累加值为100
3.get_primary_rows(cls, frame, key='per', pct=80, max_len=30)
    所有获取主要部分数据的函数都调用此类方法

命名约定：
1.百分比：per, pct
2.通行费: fee
3.cat/cats: 类别
4.以上所有返回复合数据的方法名前都无get,只有私有方法用_get_...
5.最先声明__init__函数，其次类变量和类方法

创建模块：
1.d.py 对所有结果数值计算使用Python内置decimal模块，避免溢出
2.file_util:自动创建文件夹，以及实现代码中只出现文件名，自动生成绝对路径。

图片：
处理数据时生成图片。目的，尝试将dataframe对象传递给seaborn做图
'''

    def __init__(self, excel_files):
        begin = timer()
        self.frame = self._read(excel_files)
        end = timer()
        self.nrows_read = self.frame.shape[0]
        self.time_spent = round(end-begin, 2)

        self.station = 'XXX收费站'       # 出口站名
        self.no_source_fee = 0.0  # 不明来源地的通行费
        self.primary_mode_threhold = 25  # 主要车型通行费占比判别值
        self.topmost_plates_count = 30   # 靠前车牌数量
        # 数据清理
        self.frame.drop_duplicates(inplace=True, ignore_index=True)
        self._get_station(excel_files[0])
        self._normalize_mode()
        self._sum_no_source_fee()
        self._add_province()
        self._fillna_plate()
        self._normalize_datetime()
        self._reduce_memory_use()
        # 最后获取精确总通行费，方便以后计算
        # 需在数据清理完成后获取：多次调用的数值
        self._total_fee = self._get_total_fee()
        self._primary_modes = self._get_primary_modes()

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    PROVINCES = ['四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙古',
                 '广西', '西藏', '宁夏', '新疆', '北京', '天津', '上海', '重庆',
                 '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽',
                 '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '海南',
                 '香港', '澳门']
    MODES = {1: "一类客车", 2: "二类客车", 3: "三类客车", 4: "四类客车",
             11: "一类货车", 12: "二类货车", 13: "三类货车", 14: "四类货车",
             15: "五类货车", 16: "六类货车"}

    @classmethod
    def decode_province(cls, province_code):
        '将省份代码变换为名称'
        try:
            return cls.PROVINCES[province_code]
        except IndexError:
            return '其他'

    @classmethod
    def encode_province(cls, province_str):
        '将省份名字转换为数值'
        return cls.PROVINCES.index(province_str)

    @classmethod
    def decode_mode(cls, code, simplified=True):
        '将车型代码变换为名称'
        decoded = cls.MODES[code]
        if simplified:
            return decoded[0:1]+decoded[-2:-1]
        return decoded

    @classmethod
    def normalize_per(cls, per_col):
        '''
        将Series对象per_col中的数（百分比）正常化：
        即所有值相加等于100,若不等于100,用最大值减去差值
        先将per_col数据类型转换为np.str_方便使用D.sum()
        返回时再转换为np.float32类型
        为使用Series.idmax方法，需提前获取最大值索引和数值
        '''
        # 获取最大百分比位置，和数值
        idx_max = per_col.argmax()
        value_max = per_col[idx_max]

        per_col = per_col.copy().astype(np.str_)
        total = D(per_col).sum()
        diff = D.minus(total, 100)
        # print(f'total={total}, diff={diff}, max={value_max}')
        if diff == Decimal('0'):
            return per_col.map(lambda p: float(Decimal(p)))
        # 用最大百分比减去差值
        per_col[idx_max] = str(D.minus(value_max, diff))
        return per_col.map(float)

    @classmethod
    def get_primary_rows(cls, frame, key='per', pct=60, max_len=30):
        '''
        frame:DataFrame对象，无需按key值从大到小排序，此函数排序
        key:frame中需操作的列名，数值为百分比，如89, 20, 22.4
        pct:需获共取占多少比值的行。<100，否则调用此函数无意义
        max_len:如果到达max_len行还没有pct百分比，则返回前max_len行数据

        返回数据类型：{data: 截取后的frame, fee:截取后的总通行费，per:截取后的总占比}

        1.如果frame的行数<=max_len,直接返回
        2.获取对frame按key进行降序排列，key列逐行累加
        3.获取第一个>=pct值行的位置
        如果行数<=max_len，则成功获取并返回
        如果>max_len, 则返回max_len行数据


        假设排序后的索引为0,1,...20，索引7对应累加值=71.23,索引8对于累加值=82.34
        pct=80，则bigger_idx(刚好>=pct的行索引值)=8
        1.由于pct<100，则bigger_idx<=20，截取[:bigger_idx+1]合理
        2.若选取[:bigger_idx+1]相当于选取了9行所以当bigger_idx+1>max_len时，
        应该返回[:max_len]行的数据，
        由于代码一开始及就判断若max_len>=nrows，就返回，因此后续中max_len<nrows，
        所以街区[:max_len]合理

        pandas.Series.iloc:截取时超出边界也不报错。！！白思考了。
        '''
        # 降序排序
        sorted_df = frame.sort_values(
            by=key, ascending=False, ignore_index=True)

        nrows = frame.shape[0]
        # print(f'数据长度={nrows}')
        if nrows <= max_len:
            return sorted_df

        per_col = sorted_df[key]
        # print(f'累加前：\n{per_col}')
        # 获取表示百分比的列,并累加
        cumsum_col = per_col.cumsum()
        # print(f'累加后：\n{cumsum_col}')
        # 定位满足大于百分比pct的行位置
        bigger_idx = cumsum_col.loc[cumsum_col >= pct].index[0]

        if bigger_idx + 1 > max_len:
            return sorted_df.iloc[:max_len]
        return sorted_df.iloc[:bigger_idx+1]

    @classmethod
    def get_tuple_or_single_param(cls, param):
        '''param = (x, y),或x
        获取函数参数，如果param为元组直接返回(x, y)
        如果为单值返回(x, x)
        '''
        if isinstance(param, tuple):
            return param
        return (param, param)

    def _read(self, excel_files):
        '''从多个excel文件中读取数据
操作顺序:
1.从多个excel文件中读取数据
2.从新读取第一个excel文件的第一行，获取当前收费站
3.通过axis和mode两列合理化mode，删除axis列
4.去除fee为空和fee为0的行
5.获取station为空的行，统计这些行的所有通行费
6.通过station获取入口站省份
7.将车牌栏为空的填写为WPKXXXX
8.将出口时间转换为pandas的datetime对象
9.转换数据类型，降低内存消耗
'''
        header = 3
        col_rename = {'出口车牌号': 'plate',
                      '出口时间': 'datetime',
                      '入口站名': 'station',
                      '出口车型': 'mode',
                      '通行费金额': 'fee',
                      '车辆总轴数': 'axis',
                      }

        usecols = col_rename.keys()
        engine = 'openpyxl'
        frames = []
        for excel_file in excel_files:
            print(excel_file)
            frame = pd.read_excel(excel_file,
                                  names=None,  # 读取所有sheets
                                  header=header,
                                  usecols=usecols,
                                  dtype={'通行费金额': np.str_}  # 方便使用decimal
                                  # engine=engine
                                  )

            frames.append(frame)

        frame = pd.concat(frames, ignore_index=True)
        frame.rename(columns=col_rename, inplace=True)
        return frame

    def _get_station(self, excel_file):
        '获取所在收费站'
        usecols = ['出口高速', '出口站名']
        nrows = 1
        header = 3
        frame = pd.read_excel(excel_file,
                              header=header,
                              usecols=usecols,
                              nrows=nrows
                              )
        read = frame.to_dict('records')[0]
        the_way, station = read[usecols[0]], read[usecols[1]]
        prefix = the_way[:-2]
        self.station = station.removeprefix(prefix) + '收费站'

    def _normalize_mode(self):
        '''
        1.六轴货车三类按六类计算
        2。专项作业车按同轴型货车计算
        '''
        frame = self.frame
        frame['mode'] = frame['mode'].apply(
            lambda m: m-10 if m >= 21 else m)
        frame['mode'] = frame[['axis', 'mode']].apply(
            lambda x: 16 if x['axis'] == 6 else x['mode'], axis='columns')
        frame.drop('axis', axis='columns', inplace=True)

    def _sum_no_source_fee(self):
        '''统计没有入口站信息的费用
        并删除该行
        依赖于先取出fee值非法的行，所以不单独定义函数
        '''
        def is_digit(fee_series):
            return fee_series.str.replace('.', '1', 1, regex=False).str.isdigit()

        # 去除fee为空和fee为0的行或不为数字的非法行
        frame = self.frame
        fee = frame['fee']
        i = frame[(fee.isna()) | ~(is_digit(fee)) | (fee <= '0.0')].index
        frame.drop(i, axis='index', inplace=True)

        # 获取station为空行的通行费总和
        rows = frame.loc[frame['station'].isna()]
        self.no_source_fee = D(rows['fee']).sum()
        frame.drop(rows.index, axis='index', inplace=True)

    def _add_province(self):
        '''添加入口站省份
        '''
        def slice_province(s):
            '截取入口收费站省份'
            special_provinces = ['黑龙', '内蒙']
            province = s[:2]
            if province in special_provinces:
                province = s[:3]
            return self.encode_province(province)

        self.frame['province'] = self.frame['station'].apply(
            slice_province)

    def _fillna_plate(self):
        '将车牌栏为空的填写为WPKXXXX'
        self.frame['plate'].fillna(value='WPKXXXX', inplace=True)

    def _normalize_datetime(self):
        '将单元格中提取时间字符串合法化,是否有必要？'
        def normalize(d_str):
            datetime_format = self.DATETIME_FORMAT
            dtime = datetime.strptime(d_str, datetime_format)
            return datetime.strftime(dtime, datetime_format)
        destination_datetime = self.frame['datetime']
        self.frame['datetime'] = destination_datetime.apply(
            normalize)

    def _reduce_memory_use(self):
        '''整理数据类型，减小内存使用
        '''
        # print(self.frame.info())
        # print('=================')
        self.frame = self.frame.astype({
            'plate': str,
            'datetime': np.datetime64,
            'station': str,
            'province': np.uint8,
            # 'fee': np.str_,
            'mode': np.uint8
        })
        # print(self.frame.info())
    # 获取数据

    def _get_total_fee(self):
        '获取精确的总通行费'
        return D(self.frame['fee']).sum()

    @ property
    def total_fee(self):
        '''获取总通行费
        返回值为最终文本需要:fee/10000 保留2位小数
        将属性._total_fee修改

        '''
        total_fee = self._total_fee
        return D.round(D.scale(total_fee))

    def _get_date_gap(self):
        '''获取数据总天数
        '''
        frame = self.frame
        begin = frame['datetime'].min()
        end = frame['datetime'].max()
        return begin, end

    @ property
    def month_gap(self):
        '返回描述年月跨度的字符串'
        begin, end = self._get_date_gap()
        year_from = begin.year
        month_from = begin.month
        year_to = end.year
        month_to = end.month
        result = f'{year_from}年'
        if year_from == year_to:
            result += f'{month_from}月'
            if month_from != month_to:
                result += f'至{month_to}月'
        else:
            result += f'{month_from}月至{year_to}年{month_to}月'

        return result

    @ property
    def daily_fee(self):
        '获取日均通行费'
        begin, end = self._get_date_gap()
        total_days = (end - begin).days + 1
        dresult = D.divide(self._total_fee, total_days)
        dresult = D.scale(dresult)
        dresult = D.round(dresult)
        return float(dresult)

    @ property
    def fee_of_all_modes(self):
        df, fig_path = self._get_fee_by_mode((1, 16))

        Draw(df, fig_path).for_all_modes()

        return {'rows': df.to_dict('records'),
                'fig_path': fig_path}

    @property
    def fee_of_cars_and_trucks(self):
        # 获取客车货车总通行费和总占比Dataframe
        df = self.frame[['mode', 'fee']]
        mode_col = df['mode']
        grouped = df.groupby((mode_col <= 4) & (mode_col >= 1), as_index=False)
        cars_vs_trucks_df = grouped.agg(
            mode=('mode', lambda x: '客车' if x.max() <= 4 else '货车'),
            fee=('fee', lambda x: D(x).sum(scale=True, rounding=True)),
            per=('fee', lambda x: D(x).per(self._total_fee)))

        cars_vs_trucks_df['per'] = self.normalize_per(
            cars_vs_trucks_df['per'])
        # 添加客车货车详细信息
        records = cars_vs_trucks_df.to_dict('records')
        for record in records:
            if record['mode'] == '客车':
                fee_of_cars = self._fee_of_cars()
                record['rows'] = fee_of_cars['rows']
                record['fig_path'] = fee_of_cars['fig_path']
            if record['mode'] == '货车':
                fee_of_trucks = self._fee_of_trucks()
                record['rows'] = fee_of_trucks['rows']
                record['fig_path'] = fee_of_trucks['fig_path']

        return records

    def _fee_of_cars(self):
        df, fig_path = self._get_fee_by_mode((1, 4))
        Draw(df, fig_path).for_cars_and_trucks()

        return {'rows': df.to_dict('records'),
                'fig_path': fig_path}

    def _fee_of_trucks(self):
        df, fig_path = self._get_fee_by_mode((11, 16))
        Draw(df, fig_path).for_cars_and_trucks()
        rows = list(df.itertuples(index=False))
        return {'rows': df.to_dict('records'),
                'fig_path': fig_path}

    def _get_fee_by_mode(self, mode):
        '''获取不同车型通行费
        mode: (min_mode, max_mode)最大车型与最小车型
        '''
        min_mode, max_mode = mode
        query = f'(mode >= {min_mode}) & (mode <= {max_mode})'
        df = self.frame.query(query)
        df = self._get_fee_by_group(df, 'mode')
        df['mode'] = df['mode'].map(self.decode_mode)
        fig_path = fp(
            f'fee_of_mode_{min_mode}_to_{max_mode}.png').as_image_file

        return df, fig_path

    @property
    def count_of_all_provinces(self):
        return self.provinces_count()

    def provinces_count(self, mode=(1, 16)):
        '获取所有省份个数'
        mode_min, mode_max = self.get_tuple_or_single_param(mode)
        province_col = self.frame.query(
            f'(mode >= {mode_min} & (mode <= {mode_max}))')['province']
        return province_col.nunique()

    @property
    def fee_of_in_vs_out_province_all_modes(self):
        return self.fee_of_in_vs_out_provinces()

    def fee_of_in_vs_out_provinces(self, mode=(1, 16)):
        mode_min, mode_max = self.get_tuple_or_single_param(mode)
        df = self.frame[['province', 'fee', 'mode']].query(
            f'(mode >= {mode_min}) & (mode <= {mode_max})')
        df = df[['province', 'fee']]
        grouped = df.groupby((df['province'] == 0), as_index=False)
        in_vs_out_df = grouped.agg(
            province=('province', lambda x: '省内' if x.max() == 0 else '省外'),
            fee=('fee', lambda x: D(x).sum(scale=True, rounding=True)),
            per=('fee', lambda x: D(x).per(self._total_fee))
        )
        in_vs_out_df['per'] = self.normalize_per(in_vs_out_df['per'])

        fig_path = fp(f'fee_in_vs_out_{mode_min}_{mode_max}.png').as_image_file
        Draw(in_vs_out_df, fig_path).for_in_vs_out()

        return {'fig_path': fig_path,
                'rows':     in_vs_out_df.to_dict('records')
                }

    @property
    def fee_of_primary_out_provinces_all_modes(self):
        return self.fee_of_primary_out_provinces()

    def fee_of_primary_out_provinces(self, mode=(1, 16)):
        mode_min, mode_max = self.get_tuple_or_single_param(mode)
        df = self.frame[['province', 'fee', 'mode']].query(
            f'(mode >= {mode_min}) & (mode <= {mode_max}) & (province > 0)'
        )
        df = df[['province', 'fee']]
        # 所有省份通行费和占比
        provinces_fee_df = self._get_fee_by_group(df, 'province')
        # 获取主要外省省份
        primary_df = self.get_primary_rows(
            provinces_fee_df, pct=70, max_len=10)

        # decode省份名称
        primary_df['province'] = primary_df['province'].map(
            self.decode_province)

        # 做图
        fig_path = fp(
            f'fee_of_primary_out_provinces_mode_{mode_min}_{mode_max}.png').as_image_file
        Draw(primary_df, fig_path).for_primary()

        return {'count': primary_df.shape[0],
                'fee': D(primary_df['fee']).sum(),
                'per': D(primary_df['per']).sum(),
                # 'rows': primary_df.to_dict('records'),
                'fig_path': fig_path
                }

    @property
    def fee_of_primary_stations_3cats_of_all_modes(self):
        return self.fee_of_primary_stations_3cats()

    def fee_of_primary_stations_3cats(self, mode=(1, 16)):
        result = []
        cats = ['all', 'in', 'out']
        for cat in cats:
            result.append(self._get_fee_of_primary_stations(mode=mode,
                                                            province=cat))
        return result

    def _get_fee_of_primary_stations(self, mode=(1, 16), province='all'):
        '''获取全国，省内，省外，mode对应车型的只要收费站信息
        province: all,in,out分别表示全国，省内，省外

        '''
        # 获取变量
        mode_min, mode_max = self.get_tuple_or_single_param(mode)
        if province == 'in':
            province_min, province_max = 0, 0
            cat = '省内'
        elif province == 'out':
            province_min, province_max = 1, len(self.PROVINCES)
            cat = '省外'
        else:
            province_min, province_max = 0, len(self.PROVINCES)
            cat = '全国'
        # 获取满足条件的df
        query = f'(mode>={mode_min})&(mode<={mode_max})&\
(province>={province_min})&(province<={province_max})'
        # print(query)
        df = self.frame.query(query)[['station', 'fee']]
        # 获取省份范围内的所有收费站数量
        total_count = df['station'].nunique()
        # 获取分组百分比，并取得主要数据
        df = self._get_fee_by_group(df, 'station')
        df = self.get_primary_rows(df, pct=60, max_len=30)
        # decode收费站名称如果是省内，去除'四川'
        df['station'] = df['station'].map(
            lambda x: x[2:] if province == 'in' else x)

        fig_path = fp(
            f'fee_of_primary_stations_{province}_{mode_min}_{mode_max}.png').as_image_file

        Draw(df, fig_path).for_primary()

        return{'cat': cat,
               'total_count': total_count,
               'count': df.shape[0],
               'fee': D(df['fee']).sum(),
               'per': D(df['per']).sum(),
               'rows': df.to_dict('records'),
               'fig_path': fig_path
               }

    @ property
    def fee_of_primary_modes_details(self):
        result = []
        for mode in self._primary_modes:
            detail = {}
            detail['mode'] = self.decode_mode(mode, simplified=False)
            detail['provinces_count'] = self.provinces_count(mode=mode)
            detail['in_vs_out'] = self.fee_of_in_vs_out_provinces(mode=mode)
            detail['primary_out'] = self.fee_of_primary_out_provinces(
                mode=mode)
            detail['primary_stations_3cats'] = self.fee_of_primary_stations_3cats(
                mode=mode)
            result.append(detail)

        return result

    @ property
    def fee_of_topmost_plates_of_primary_modes(self):
        result = []
        for mode in self._primary_modes:
            # 获取并过滤数据
            df = self.frame[self.frame['mode'] == mode]
            df = self._get_topmost_plates(df)
            detail = {}
            # 输出数据
            fig_path = fp(f'topmost_plates_{mode}.png').as_image_file
            Draw(df, fig_path).for_topmost_plates()

            detail['mode'] = self.decode_mode(mode, simplified=False)
            detail['fee'] = D(df['fee']).sum(scale=False)
            detail['per'] = D(df['per']).sum()
            detail['fig_path'] = fig_path
            detail['rows'] = df.to_dict('records')

            result.append(detail)

        return result

    @ property
    def fee_of_topmost_plates(self):
        df = self._get_topmost_plates(self.frame)
        # 输出数据
        fig_path = fp('topmost_plates.png').as_image_file
        Draw(df, fig_path).for_topmost_plates()

        return {'fee': D(df['fee']).sum(scale=False),
                'per': D(df['per']).sum(),
                'fig_path': fig_path,
                'rows': df.to_dict('records')
                }

    def _get_topmost_plates(self, frame):
        '''获取frame中排名靠前的车牌
        返回dataFrame对象，并添加车牌下行次数的列
        '''
        df = self._get_fee_by_group(frame, 'plate',
                                    scale_fee=False,
                                    normalize_per=False)
        # 过滤数据
        df = df[~df['plate'].str.startswith(('默', 'WP'))]

        # 排序并截取数据
        df = df.sort_values(by='fee', ascending=False)
        df = df.iloc[:self.topmost_plates_count]

        # 添加下行次数
        df['count'] = df['plate'].map(
            lambda p: frame[frame['plate'] == p].shape[0])

        return df

    @property
    def primary_modes(self):
        modes = []
        for m in self._get_primary_modes():
            modes.append(self.decode_mode(m, simplified=False))
        return modes

    def _get_primary_modes(self):
        '''获取主要车型，返回主要车型编号的list
        '''
        df = self._get_fee_by_group(self.frame, 'mode')
        df = df[df['per'] >= self.primary_mode_threhold]
        series = df.sort_values(by='per', ascending=False)[
            'mode']
        return list(series.to_dict().values())

    def _get_fee_by_group(self, frame, by, scale_fee=True,
                          normalize_per=True):
        '''获取不同分组中，各组通行费和组内总占比
单组返回数据类型：dataFrame
normalize_per:当数据条数过多时，如按车牌获取，
计算百分比过程中会使用四舍五入，normalize后误差会很大。
大多数情况不会出现，所以默认为True
scale_fee:同样，数据量很大时，缩小10000倍后无意义，因为每个值就很小
'''
        df = frame[[by, 'fee']]
        total_fee = D(df['fee']).sum()
        result = df.groupby(by, as_index=False).agg(
            fee=('fee', lambda x: D(x).sum(scale=scale_fee, rounding=True)),
            per=('fee', lambda x: D(x).per(total_fee)))
        if normalize_per:
            result['per'] = self.normalize_per(result['per'])

        return result

    def show(self):
        # print(self.frame.head(30))
        print(self.frame.info())
        print(self.frame.describe())
        print(self.frame)


if __name__ == '__main__':
    import os
    excel_files_test = ['test_files/12月货车_测试.xlsx', 'test_files/12月客车_测试.xlsx']
    excel_files = ['test_files/12月货车.xlsx', 'test_files/12月客车.xlsx']

    def get_files():
        root = 'test_files/leshanbei_xls_fast'
        # root='test_files/maoqiao01'
        list_of_files = []
        for root, dirs, files in os.walk(root):
            for f in files:
                list_of_files.append(os.path.join(root, f))
        return list_of_files

    vehicles = Vehicles(excel_files_test)
    print(vehicles.frame)
    # print(vehicles.station)
    # print(vehicles.no_source_fee)
    # vehicles.show()
    # print(vehicles.no_source_fee)
    # print(vehicles.total_fee)
    # print(vehicles.daily_fee)
    # print(vehicles.month_gap)
    # print(vehicles.fee_of_all_modes)
    # print(vehicles._fee_of_cars())
    # print(vehicles._fee_of_trucks())
    # print(vehicles.fee_of_cars_and_trucks)
    # print(vehicles.province_count())
    # print(vehicles.fee_in_vs_out_province())
    # print(vehicles.fee_of_primary_out_provinces(mode=16))
    # for cat in ['all', 'in', 'out']:
    # print(vehicles.fee_of_primary_stations_3cats())
    # print(vehicles._get_primary_modes())
    # print(vehicles.fee_of_primary_modes_details)
    # print(vehicles.fee_of_topmost_plates_of_primary_modes)
    # print(vehicles.fee_of_topmost_plates)
