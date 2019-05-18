'''python
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 23:03:06 2019

@author: Administrator
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Funnel

#导入数据
data = pd.read_csv('tianchi_mobile_recommend_train_user.csv')

#查看数据基本情况
#data.info()
#查看前5行数据
data.head()

#查看数据缺失情况
data.isnull().any()
#计算缺失率
data_count = data.count()
na_count = len(data) - data_count
na_rate = na_count/len(data)
print(na_rate)

'''
数据预处理
1.数值转化：为方便查看，将'behavior_type'的四种行为类型（现分别用1,2,3,4代表）转为pv,collect,cart,buy
2.缺失值处理：'user_geohash'地理位置列，68%为NULL，且信息被加密处理，剔除，后面不做地理位置的研究
3.数据类型转化：'time'列为object，为方便分析，由该字段衍生2个新字段，日期列和小时列
'''

#数值转化
data.loc[data['behavior_type']==1,'behavior_type'] = 'pv'
data.loc[data['behavior_type']==2,'behavior_type'] = 'collect'
data.loc[data['behavior_type']==3,'behavior_type'] = 'cart'
data.loc[data['behavior_type']==4,'behavior_type'] = 'buy'
#查看各行为计数
#data.groupby(['behavior_type']).count()

#缺失值处理
data.drop('user_geohash',axis=1,inplace=True)

#数据类型转化
data = pd.merge(data,pd.DataFrame(data['time'].str.split(' ',expand=True)),how='left',left_index=True,right_index=True)
data.rename(columns={0:'day',1:'hour'},inplace=True)
data['time'] = pd.to_datetime(data['time'])
data['weekday_name'] = data['time'].dt.weekday_name  #提取周名称信息

'''
数据分析
1.基础数据统计（总体、周、日、小时用户行为PV,UV；有购买行为用户数，复购率）
2.用户行为转化漏斗
3.畅销品类（销售次数前10的品类）
'''

#基础数据统计
#(1.1)总体PV,UV
data.groupby(['behavior_type']).count() #PV(访问总量)，用户每刷新一次即被计算一次
data.drop_duplicates('user_id').count() #UV(独立访客)，固定周期内相同的客户端只被计算一次
#(1.2)周PV
data_week = data.groupby('weekday_name').count()
data_week.index = [1,2,3,4,5,6,7]

#可视化
fig = plt.figure(figsize=(10,4))
plt.rcParams['font.sans-serif']=['SimHei'] #显示中文标签
#plt.xticks(range(0,len(data_week.index)),data_week.index)
#plt.ylim((1500000,2000000))
plt.plot(data_week.index,data_week['user_id'])

#周三到周五的用户行为逐渐增加，周五-周日达到一个稳定值，周一周二用户行为明显减少，周三为一周最低，周三后开始逐渐增加

#(1.3)日PV&UV
PV = data.groupby('day')['user_id'].count().reset_index().rename(columns={'user_id':'PV'})
UV = data.groupby('day')['user_id'].nunique().reset_index().rename(columns={'user_id':'UV'})
PV.plot(x='day',y='PV',title='PV日浏览量分布')
UV.plot(x='day',y='UV',title='UV日浏览量分布')

#(1.4)小时PV&UV
PV_hour = data.groupby('hour')['user_id'].count().reset_index().rename(columns={'user_id':'PV_hour'})
UV_hour = data.groupby('hour')['user_id'].count().reset_index().rename(columns={'user_id':'UV_hour'})
PV_hour.plot(x='hour',y='PV_hour',title='PV小时浏览量分布')
UV_hour.plot(x='hour',y='UV_hour',title='UV小时浏览量分布')

#2.用户行为转化漏斗
data_beh = data.groupby('behavior_type')['user_id'].count()
pv_num = data_beh['pv']
fav_num = data_beh['collect'] + data_beh['cart']
buy_num = data_beh['buy']

#计算总体转化率
pv_to_pv = pv_num/pv_num
pv_to_fav = fav_num/pv_num
pv_to_buy = buy_num/pv_num

#绘制漏斗图
funnel = (
        Funnel()
        .add("环节",[('pv',pv_to_pv),('fav',pv_to_fav),('buy',pv_to_buy)])
        .set_global_opts(title_opts=opts.TitleOpts(title="总体转化漏斗图"))
        )
funnel.render()

#3.复购率
df=data[data['behavior_type']=='buy']
df.groupby('item_category').count().sort_values('user_id',ascending=False)
