# -*- coding:utf-8 -*-
"""
Created on 2012-1-5

@author: Sean
"""
import re
p = re.compile('(20\d{2}\-\d{2}\-\d{2}\s\d{2}):\d{2}:\d{2},\d{3}\sINFO\sTime\sused:\s(\d+)')
f = open('../log/db_air.log', 'r')
t = open('../log/result.txt', 'w')
while(True):
    l = f.readline()
    if not l: break
    c = p.findall(l)
    if c:
        s = c[0][0] + '\t' + c[0][1] + '\n'
        t.write(s)
f.close()
t.close()
raw_input('耗时 - 日期 对应数据已经提取，文件存放于 D:\\air_sqlite\\log\\result.txt'\
          '\n按任意键退出...')