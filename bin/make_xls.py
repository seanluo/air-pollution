# coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    module
Date:       2011-12-1
'''

import sqlite3
import xlwt
import os
from mod_utils import get_cities


def make_xls(city_name):
    db_path = '../data/database/' + city_name + '.db'
    xls_path = '../result_data_folder_has_a_long_name/' + city_name + '.xls'
    conn = sqlite3.connect(db_path)
    conn.text_factory = str
    file = xlwt.Workbook(encoding='utf-8')
    table = file.add_sheet('average')
    print ('Average')
    cur = conn.cursor()
    cur.execute('SELECT * FROM tbl_average')
    rs = cur.fetchall()
    rowcnt = 0
    for result in rs:
        date = result[0]
        time = result[1]
        so2 = result[2]
        no2 = result[3]
        pm10 = result[4]
        table.write(rowcnt, 0, date)
        table.write(rowcnt, 1, time)
        table.write(rowcnt, 2, so2)
        table.write(rowcnt, 3, no2)
        table.write(rowcnt, 4, pm10)
        rowcnt += 1
    file.save(xls_path)
    cur.execute('SELECT * FROM tbl_station')
    rs = cur.fetchall()
    for result in rs:
        id = result[0]
        name = result[1]
        print id, name.decode('utf-8')
        cur.execute('SELECT * FROM ' + name)
        rset = cur.fetchall()
        table = file.add_sheet(name)
        rowcnt = 0
        for r in rset:
            date = r[0]
            time = r[1]
            so2 = r[2]
            no2 = r[3]
            pm10 = r[4]
            table.write(rowcnt, 0, date)
            table.write(rowcnt, 1, time)
            table.write(rowcnt, 2, so2)
            table.write(rowcnt, 3, no2)
            table.write(rowcnt, 4, pm10)
            rowcnt += 1
        file.save(xls_path)
    cur.close()
    conn.close()


def main():
    city = get_cities()
    num = len(city)
    cnt = 0
    for one_city in city:
        cnt += 1
        print (str(cnt) + '/' + str(num) + '\tMake XLS for: ' + one_city)
        try:
            make_xls(one_city)
        except:
            print('Make XLS failed for:' + one_city)
    print ('Job\'s done!')
    raw_input('Press any ENTER to continue...')


if __name__ == '__main__':
    try:
        os.mkdir('../result_data_folder_has_a_long_name')
        main()
    except:
        answer = raw_input('Excel files exist, overwrite? (y/N)')
        if answer != 'y':
            pass
        else:
            main()
