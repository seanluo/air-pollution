#coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    module
Date:       2011-12-4
'''

import os
import xlrd
import xlwt
from xlutils.copy import copy
from mod_utils import get_config

def store_to_excel(data_table, city_name = ''):
    if city_name == '':
        average_to_xls(data_table)
    else:
        detail_to_xls(data_table, city_name)

def module_setup():
    data_path = get_config()[-2]['data']
    try:
        os.mkdir("../" + data_path + "/excel")
    except:
        pass
        
def average_to_xls(data_table):
    data_path = get_config()[-2]['data']
    for row in data_table:
        city_name = row[1]
        file_name = '../' + data_path + '/excel/' + city_name.decode('utf-8') + '.xls'
        if os.path.exists(file_name):
            rb = xlrd.open_workbook(file_name, encoding_override="utf-8")
            wb = copy(rb)
            write_to_existent(rb, wb, row, file_name, 2, 'average')
        else:
            wb = xlwt.Workbook(encoding='utf-8')
            write_to_new(wb, row, file_name, 2, 'average')

def detail_to_xls(data_table, city_name):
    data_path = get_config()[-2]['data']
    file_name = '../' + data_path + '/excel/' + city_name + '.xls'
    rb = xlrd.open_workbook(file_name, encoding_override="utf-8")
    wb = copy(rb)
    for row in data_table:
        write_to_existent(rb, wb, row, file_name, 7) 

def write_to_existent(rb, wb, row, file_name, pos, place = ''):
    if place == '':
        place = row[1].decode('utf-8')
    so2 = float(row[pos+0])
    no2 = float(row[pos+1])
    pm10= float(row[pos+2])
    date = row[pos+3]
    time = row[pos+4]
    st_names = rb.sheet_names()
    try:
        pos_place= st_names.index(place)
        w_sheet = wb.get_sheet(pos_place)
        r_sheet = rb.sheet_by_name(place)
        if w_sheet.name == place:
            start_pos = r_sheet.nrows
            last_time = ''
            last_date = ''
            try:
                last_date = r_sheet.cell(start_pos-1, 0).value
                last_time = r_sheet.cell(start_pos-1, 1).value
            except:
                pass
            if (last_date != date) or (last_time != time):
                w_sheet.write(start_pos, 0, date)
                w_sheet.write(start_pos, 1, time)
                w_sheet.write(start_pos, 2, so2)
                w_sheet.write(start_pos, 3, no2)
                w_sheet.write(start_pos, 4, pm10)
                wb.save(file_name)
    except:
        print ('New Station:' + place)
        try:
            write_to_new(wb, row, file_name, pos)
        except:
            pass

def write_to_new(wb, row, file_name, pos, place = ''):  
    if place == '':
        place = row[1].decode('utf-8')
    table = wb.add_sheet(place)
    so2 = float(row[pos])
    no2 = float(row[pos+1])
    pm10= float(row[pos+2])
    date= row[pos+3]
    time= row[pos+4]
    table.write(0,0,date)
    table.write(0,1,time)
    table.write(0,2,so2)
    table.write(0,3,no2)
    table.write(0,4,pm10)
    wb.save(file_name)
    