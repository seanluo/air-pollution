#coding: utf-8
__author__ = 'Sean'

import sqlite3
import xlwt
def make_xls():
    db_path = '../data/harbin.db'
    xls_path = '../result_data_folder_has_a_long_name/harbin.xls'
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    file = xlwt.Workbook(encoding='utf-8')
    sites = [
        u"阿城会宁",
        u"南岗学府路",
        u"太平宏伟公园",
        u"道外承德广场",
        u"香坊红旗大街",
        u"动力和平路",
        u"道里建国路",
        u"平房东轻厂",
        u"呼兰师专",
        u"岭北",
        u"松北商大",
        u"省农科院"
    ]
    for site in sites:
        print site
        per_site(site, conn, file, xls_path)

def per_site(name, conn, file, xls_path):
    table = file.add_sheet(name)
    cur = conn.cursor()
    cur.execute('SELECT * FROM %s' % name)
    rs = cur.fetchall()
    rowcnt = 0
    for result in rs:
        date = result[0]
        time = result[1]
        pm10 = result[7]
        pm25 = result[8]
        table.write(rowcnt, 0, date)
        table.write(rowcnt, 1, time)
        table.write(rowcnt, 2, pm10)
        table.write(rowcnt, 3, pm25)
        rowcnt += 1
    file.save(xls_path)

make_xls()