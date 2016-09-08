# -*- coding:cp936 -*-
"""
Created on 2013-5-12

@author: Sean
"""

import sqlite3
import xlwt
import datetime
from mod_utils import get_cities


def geo():
    cities = get_cities()
    db_to = '../data/geo.db'
    conn_to = sqlite3.connect(db_to)
    conn_to.text_factory = str
    sql = ("CREATE TABLE IF NOT EXISTS site" +
           "(city TEXT, site_name TEXT, address TEXT, longitude TEXT, latitude TEXT)")
    conn_to.execute(sql)

    for city_name in cities:
        db_from = '../data/database/' + city_name + '.db'
        conn_from = sqlite3.connect(db_from)
        conn_from.text_factory = str
        sql_from = "SELECT * FROM tbl_station"
        cur_from = conn_from.cursor()
        rs_from = cur_from.execute(sql_from).fetchall()
        for item in rs_from:
            save_to = ("INSERT OR REPLACE INTO site VALUES ('%s', '%s', '%s', '%s', '%s')" %
                       (city_name, item[1], item[2], item[3], item[4]))
            conn_to.execute(save_to)
        conn_to.commit()
        conn_from.close()
    conn_to.close()


def filtered(city_name):
    db_to = '../data/filtered_db/' + city_name + '.db'
    conn_to = sqlite3.connect(db_to)
    conn_to.text_factory = str

    db_from = '../data/database/' + city_name + '.db'
    conn_from = sqlite3.connect(db_from)
    conn_from.text_factory = str
    cur_from = conn_from.cursor()

    stations = cur_from.execute("SELECT * FROM tbl_station").fetchall()
    for station in stations:
        tbl_src = station[1]
        tbl_name = station[1].decode('UTF-8').encode('GBK')
        print tbl_name.decode('cp936')
        dict_one_station = {}
        sql_to = "CREATE TABLE IF NOT EXISTS %s(date TEXT, so2 TEXT, no2 TEXT, pm10 TEXT)" % (tbl_name)
        conn_to.execute(sql_to)

        sql_from = "SELECT * FROM %s" % (tbl_src)
        rows = cur_from.execute(sql_from).fetchall()
        dates = []
        for row in rows:
            if row[0] not in dates:
                dates.append(row[0])
            mydict = dict_one_station.get(row[0])
            if not mydict:
                mydict = {"so2": [], "no2": [], "pm10": []}
                dict_one_station[row[0]] = mydict
            mydict["so2"].append(row[2])
            mydict["no2"].append(row[3])
            mydict["pm10"].append(row[4])

        for mydate in dates:
            day_avg = {"so2": "NA", "no2": "NA", "pm10": "NA"}
            so2_tt = 0
            so2_cc = 0
            so2_list = dict_one_station[mydate]["so2"]
            for so2 in so2_list:
                if 0 < so2 < 123456:
                    so2_tt += so2
                    so2_cc += 1
                if so2_cc >= 12:
                    so2_avg = so2_tt / so2_cc
                    day_avg["so2"] = "%.2f" % (so2_avg)

            no2_tt = 0
            no2_cc = 0
            no2_list = dict_one_station[mydate]["no2"]
            for no2 in no2_list:
                if 0 < no2 < 123456:
                    no2_tt += no2
                    no2_cc += 1
                if no2_cc >= 12:
                    no2_avg = no2_tt / no2_cc
                    day_avg["no2"] = "%.2f" % (no2_avg)

            pm10_tt = 0
            pm10_cc = 0
            pm10_list = dict_one_station[mydate]["pm10"]
            for pm10 in pm10_list:
                if 0 < pm10 < 123456:
                    if pm10 < 6:
                        pm10 = 6
                    pm10_tt += pm10
                    pm10_cc += 1
                if pm10_cc >= 12:
                    pm10_avg = pm10_tt / pm10_cc
                    day_avg["pm10"] = "%.2f" % pm10_avg

            sql_to = ("INSERT OR REPLACE INTO %s VALUES ('%s', '%s', '%s', '%s')"
                      % (tbl_name, mydate,
                         day_avg["so2"],
                         day_avg["no2"],
                         day_avg["pm10"])
                      )
            conn_to.execute(sql_to)
        conn_to.commit()


def get_daily_avg():
    city = get_cities()
    num = len(city)
    cnt = 0
    for one_city in city:
        cnt += 1
        print (str(cnt) + '/' + str(num) + '\tprocessing: ' + one_city)
        filtered(one_city)

    print ('Job\'s done!')
    raw_input('Press any ENTER to continue...')


def xls_avg(city_name):
    db = '../data/filtered_db/' + city_name + '.db'
    xls = '../data/filtered_xls/' + city_name + '.xls'
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()

    myfile = xlwt.Workbook(encoding='utf-8')
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    rs = cur.fetchall()
    for result in rs:
        name = result[0]
        print name.decode('utf-8')
        cur.execute('SELECT * FROM ' + name)
        rset = cur.fetchall()
        table = myfile.add_sheet(name)
        rowcnt = 0
        d_enter = d = datetime.datetime.strptime("2012-01-01", '%Y-%m-%d')
        d_exit = d = datetime.datetime.strptime("2013-01-01", '%Y-%m-%d')
        d_last = d_enter
        for r in rset:
            mydate = r[0][:-1]
            if mydate == "2010-11-21": continue
            # this is a bug from data source
            d = datetime.datetime.strptime(mydate, '%Y-%m-%d')
            diff = (d - d_last).days
            if diff < 0: continue
            if diff > 1:
                for td in xrange(diff - 1):
                    delta = datetime.timedelta(days=td + 1)
                    ai_day = (d_last + delta).strftime('%Y-%m-%d')
                    table.write(rowcnt, 0, ai_day)
                    table.write(rowcnt, 1, "NA")
                    table.write(rowcnt, 2, "NA")
                    table.write(rowcnt, 3, "NA")
                    rowcnt += 1
            d_last = d
            if (d - d_exit).days >= 0: break
            so2 = r[1]
            no2 = r[2]
            pm10 = r[3]
            table.write(rowcnt, 0, mydate)
            table.write(rowcnt, 1, so2)
            table.write(rowcnt, 2, no2)
            table.write(rowcnt, 3, pm10)
            rowcnt += 1
        myfile.save(xls)
    cur.close()
    conn.close()


def get_xls_avg():
    city = get_cities()
    num = len(city)
    cnt = 0
    for one_city in city:
        cnt += 1
        print (str(cnt) + '/' + str(num) + '\tprocessing: ' + one_city)
        try:
            xls_avg(one_city)
        except:
            print('fail for:' + one_city)
    print ('Job\'s done!')
    raw_input('Press any ENTER to continue...')


def xls_month_avg(city_name):
    all_year = ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12")
    db = '../data/filtered_db/' + city_name + '.db'
    xls = '../data/filtered_month_xls/' + city_name + '.xls'
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    my_file = xlwt.Workbook(encoding='utf-8')
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    sites = cur.fetchall()
    table = my_file.add_sheet("sheet0")
    row_cnt = 0
    for site in sites:
        name = site[0]
        print name.decode('utf-8')
        cur.execute('SELECT * FROM ' + name)
        daily_records = cur.fetchall()
        d_enter = datetime.datetime.strptime("2012-01-01", '%Y-%m-%d')
        d_exit = datetime.datetime.strptime("2013-01-01", '%Y-%m-%d')
        so2 = {}
        no2 = {}
        pm10 = {}
        c_so2 = {}
        c_no2 = {}
        c_pm10 = {}
        row_cnt += 1
        for month in all_year:
            month_key = "2012-%s" % month
            so2[month_key] = 0
            no2[month_key] = 0
            pm10[month_key] = 0
            c_so2[month_key] = 0
            c_no2[month_key] = 0
            c_pm10[month_key] = 0
        for daily_record in daily_records:
            my_date = daily_record[0][:-1]
            if my_date == "2010-11-21":
                # this is a bug from data source
                continue
            try:
                d = datetime.datetime.strptime(my_date, '%Y-%m-%d')
            except:
                continue
            if ((d - d_exit).days >= 0) or ((d - d_enter).days < 0):
                continue
            month_key = my_date[:7]
            if daily_record[1] != "NA":
                so2[month_key] += float(daily_record[1])
                c_so2[month_key] += 1
            if daily_record[2] != "NA":
                no2[month_key] += float(daily_record[2])
                c_no2[month_key] += 1
            if daily_record[3] != "NA":
                pm10[month_key] += float(daily_record[3])
                c_pm10[month_key] += 1
        table.write(row_cnt, 0, name)
        for month in all_year:
            month_key = "2012-%s" % month
            col = 3 * (int(month) - 1)
            if c_so2[month_key] == 0:
                so2_avg = "NA"
            else:
                so2_avg = so2[month_key] / c_so2[month_key]
            if c_no2[month_key] == 0:
                no2_avg = "NA"
            else:
                no2_avg = no2[month_key] / c_no2[month_key]
            if c_pm10[month_key] == 0:
                pm10_avg = "NA"
            else:
                pm10_avg = pm10[month_key] / c_pm10[month_key]
            table.write(row_cnt, col + 1, so2_avg)
            table.write(row_cnt, col + 2, no2_avg)
            table.write(row_cnt, col + 3, pm10_avg)
        # ---- Spring ----
        col = 38
        count_so2 = 0
        sum_so2 = 0
        count_no2 = 0
        sum_no2 = 0
        count_pm10 = 0
        sum_pm10 = 0
        months = ["2012-%s" % i for i in ("03", "04", "05")]
        for month in months:
            count_so2 += c_so2[month]
            sum_so2 += so2[month]
            count_no2 += c_no2[month]
            sum_no2 += no2[month]
            count_pm10 += c_pm10[month]
            sum_pm10 += pm10[month]
        if count_so2 == 0:
            so2_avg = "NA"
        else:
            so2_avg = sum_so2 / count_so2
        if count_no2 == 0:
            no2_avg = "NA"
        else:
            no2_avg = sum_no2 / count_no2
        if count_pm10 == 0:
            pm10_avg = "NA"
        else:
            pm10_avg = sum_pm10 / count_pm10
        table.write(row_cnt, col, so2_avg)
        table.write(row_cnt, col + 1, no2_avg)
        table.write(row_cnt, col + 2, pm10_avg)
        # ---- Summer ----
        col = 41
        count_so2 = 0
        sum_so2 = 0
        count_no2 = 0
        sum_no2 = 0
        count_pm10 = 0
        sum_pm10 = 0
        months = ["2012-%s" % i for i in ("06", "07", "08")]
        for month in months:
            count_so2 += c_so2[month]
            sum_so2 += so2[month]
            count_no2 += c_no2[month]
            sum_no2 += no2[month]
            count_pm10 += c_pm10[month]
            sum_pm10 += pm10[month]
        if count_so2 == 0:
            so2_avg = "NA"
        else:
            so2_avg = sum_so2 / count_so2
        if count_no2 == 0:
            no2_avg = "NA"
        else:
            no2_avg = sum_no2 / count_no2
        if count_pm10 == 0:
            pm10_avg = "NA"
        else:
            pm10_avg = sum_pm10 / count_pm10
        table.write(row_cnt, col, so2_avg)
        table.write(row_cnt, col + 1, no2_avg)
        table.write(row_cnt, col + 2, pm10_avg)
        # ---- Autumn ----
        col = 44
        count_so2 = 0
        sum_so2 = 0
        count_no2 = 0
        sum_no2 = 0
        count_pm10 = 0
        sum_pm10 = 0
        months = ["2012-%s" % i for i in ("09", "10", "11")]
        for month in months:
            count_so2 += c_so2[month]
            sum_so2 += so2[month]
            count_no2 += c_no2[month]
            sum_no2 += no2[month]
            count_pm10 += c_pm10[month]
            sum_pm10 += pm10[month]
        if count_so2 == 0:
            so2_avg = "NA"
        else:
            so2_avg = sum_so2 / count_so2
        if count_no2 == 0:
            no2_avg = "NA"
        else:
            no2_avg = sum_no2 / count_no2
        if count_pm10 == 0:
            pm10_avg = "NA"
        else:
            pm10_avg = sum_pm10 / count_pm10
        table.write(row_cnt, col, so2_avg)
        table.write(row_cnt, col + 1, no2_avg)
        table.write(row_cnt, col + 2, pm10_avg)
        # ---- Winter ----
        col = 47
        count_so2 = 0
        sum_so2 = 0
        count_no2 = 0
        sum_no2 = 0
        count_pm10 = 0
        sum_pm10 = 0
        months = ["2012-%s" % i for i in ("01", "02", "12")]
        for month in months:
            count_so2 += c_so2[month]
            sum_so2 += so2[month]
            count_no2 += c_no2[month]
            sum_no2 += no2[month]
            count_pm10 += c_pm10[month]
            sum_pm10 += pm10[month]
        if count_so2 == 0:
            so2_avg = "NA"
        else:
            so2_avg = sum_so2 / count_so2
        if count_no2 == 0:
            no2_avg = "NA"
        else:
            no2_avg = sum_no2 / count_no2
        if count_pm10 == 0:
            pm10_avg = "NA"
        else:
            pm10_avg = sum_pm10 / count_pm10
        table.write(row_cnt, col, so2_avg)
        table.write(row_cnt, col + 1, no2_avg)
        table.write(row_cnt, col + 2, pm10_avg)
        # ---- Whole year ----
        col = 50
        count_so2 = 0
        sum_so2 = 0
        count_no2 = 0
        sum_no2 = 0
        count_pm10 = 0
        sum_pm10 = 0
        months = ["2012-%s" % i for i in all_year]
        for month in months:
            count_so2 += c_so2[month]
            sum_so2 += so2[month]
            count_no2 += c_no2[month]
            sum_no2 += no2[month]
            count_pm10 += c_pm10[month]
            sum_pm10 += pm10[month]
        if count_so2 == 0:
            so2_avg = "NA"
        else:
            so2_avg = sum_so2 / count_so2
        if count_no2 == 0:
            no2_avg = "NA"
        else:
            no2_avg = sum_no2 / count_no2
        if count_pm10 == 0:
            pm10_avg = "NA"
        else:
            pm10_avg = sum_pm10 / count_pm10
        table.write(row_cnt, col, so2_avg)
        table.write(row_cnt, col + 1, no2_avg)
        table.write(row_cnt, col + 2, pm10_avg)
    my_file.save(xls)
    cur.close()
    conn.close()


def get_xls_month_avg():
    city = get_cities()
    num = len(city)
    cnt = 0
    for one_city in city:
        cnt += 1
        print (str(cnt) + '/' + str(num) + '\tprocessing: ' + one_city)
        # try:
        xls_month_avg(one_city)
        # except:
        # print('fail for:' + one_city)
    print ('Job\'s done!')
    raw_input('Press any ENTER to continue...')


get_daily_avg()
