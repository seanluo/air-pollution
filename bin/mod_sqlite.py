#coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    module
Date:       2011-12-4
'''

import os
import sqlite3
from mod_utils import get_config
        
def store_to_sqlite(data_table, city_name):
    data_path = get_config()[-2]['data']
    if city_name != '':
        db_name = "../" + data_path + "/database/" + city_name + ".db"
        conn = sqlite3.connect(db_name)
        conn.text_factory = str
        cur = conn.cursor()
        for row in data_table:
            id = row[0]
            if id == '':
                continue
            place = row[1]
            longi = row[2]
            lati = row[3]
            place = place.replace("#","号")
            longi = longi.replace("'","\'")
            lati = lati.replace("'","\'")
            so2 = row[7]
            no2 = row[8]
            pm10 = row[9]
            date = row[10]
            time = row[11]
            cur.execute("SELECT ID FROM tbl_station WHERE name='" + place + "'")
            rs = cur.fetchone()
            if not rs:
                ID = row[0]
                name = row[1]
                longi = row[2]
                lati = row[3]
                name = name.replace("#","号")
                longi.replace("'","\\'")
                lati.replace("'","\\'")
                address = row[4]
                if ID == '':
                    continue
                print ('New station: ' + ID + '\t' + name.decode('utf-8'))
                sql = ("INSERT INTO tbl_station VALUES ('" + 
                       ID + "', '" + name + "', '" + 
                       address + "', '" + 
                       longi + "', '" + 
                       lati + "')")
                conn.execute(sql)
                sql = ("CREATE TABLE IF NOT EXISTS " + name + 
                   "(date DATE, time INTEGER, so2 REAL, no2 REAL, pm10 REAL, " +
                   "PRIMARY KEY(date, time))")
                conn.execute(sql)
            else:
                ID = rs[0]
            sql = ("INSERT OR REPLACE INTO " + place + " VALUES ('" + 
                   date + "', '" + time + "', '" + 
                   so2 + "', '" + no2 + "', '" + pm10 + "')")
            conn.execute(sql)
        conn.commit()
        conn.close()
    else:
        for row in data_table:
            city_name = row[1]
            so2 = row[2]
            no2 = row[3]
            pm10 = row[4]
            date = row[5]
            time = row[6]
            db_name = "../" + data_path + "/database/" + city_name + ".db"
            conn = sqlite3.connect(db_name)
            conn.text_factory = str
            sql = "SELECT * FROM sqlite_master WHERE type='table'"
            rs = conn.execute(sql).fetchall()
            if not rs:
                init_database(conn)
            sql = ("INSERT OR REPLACE INTO tbl_average VALUES ('" + 
                    date + "', '" + time + "', '" + 
                    so2 + "', '" + no2 + "', '" + pm10 + "')")
            conn.execute(sql)
            conn.commit()
            conn.close()
            
def init_database(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tbl_average(
        date DATE,
        time INTEGER,
        so2 REAL,
        no2 REAL,
        pm10 REAL,
        PRIMARY KEY(date, time)
        )
        ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tbl_station(
        id TEXT,
        name TEXT,
        address TEXT,
        longitude TEXT,
        latitude TEXT,
        PRIMARY KEY(id, name)
        )
        ''')
    conn.commit()
    
def module_setup():
    data_path = get_config()[-2]['data']
    try:
        os.mkdir("../" + data_path + "/database")
    except:
        pass