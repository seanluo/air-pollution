#coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    modulize
Date:       2011-12-4
Description: 通过基本库实现数据的获取并处理成内存中的表格，返回给主程序处理
              提供统一存储接口
'''
import urllib2
from mod_utils import convert_to_ug

null = ''

def get_data(server_url):
    '''
    get data from the server, in plain text format
    '''
    req = urllib2.Request(server_url)
    fd = urllib2.urlopen(req)
    data_str=""
    while True:
        data = fd.read(1024)
        data_str += data
        if not len(data):
            break
    return data_str

def add_common_data(row, record, pos_p, pos_c, pos_so2, pos_no2, pos_pm10, pos_dt):
    province = record[pos_p]
    city = record[pos_c]
    SO2 = convert_to_ug(record[pos_so2])
    NO2 = convert_to_ug(record[pos_no2])
    PM10= convert_to_ug(record[pos_pm10])
    date = record[pos_dt][0:10]
    time = record[pos_dt][11:]
    row.append(province)
    row.append(city)
    row.append(SO2)
    row.append(NO2)
    row.append(PM10)
    row.append(date)
    row.append(time)

def add_desc_data(row, record, pos_place, pos_id, pos_addr, pos_long, pos_lat):
    place = record[pos_place]
    id = record[pos_id]
    address = record[pos_addr]
    longitude = record[pos_long]
    latitude = record[pos_lat]
    if not longitude:
        longitude = record[11]
        latitude = record[12]
        if longitude:
            longitude += 'E'
            latitude += 'N'
    else:
        longitude += 'E'
        latitude += 'N'
    if id == '':
        return False
    row.append(id)
    row.append(place)
    row.append(longitude)
    row.append(latitude)
    row.append(address)
    return True

def proceed_data(data_str, city_name = ''):
    '''
    proceed the plain text into format that we can deal with
    '''
    global null
    data_table = []
    if(data_str == ""):
        return data_table
    try:
        data_to_parse = eval (data_str)
    except:
        return data_table
    recordsets = data_to_parse["recordsets"][0]
    records = recordsets["records"]
    for record in records:
        row = []
        record = record["fieldValues"]
        if city_name == '':
            # average value for all stations in one city
            add_common_data(row, record, 0, 1, 2, 3, 4, 6)
        else:
            # detail for each city
            if add_desc_data(row, record, 7, 8, 14, 15, 16):
                add_common_data(row, record, 5, 6, 17, 18, 19, 169)
            else:
                continue
        data_table.append(row)
    return data_table

def store_data(data_table, store_method, city_name = ''):
    '''
    store data
    null city name means we are storing average values
    else for some certain city
    '''
    if(data_table==[]):
        return False
    store_method(data_table, city_name)
    return True
