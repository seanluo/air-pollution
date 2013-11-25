#coding: utf-8
'''
Created on 2011-12-13

@author: Sean
'''
import unittest
import os
import shutil
import sqlite3
from mod_utils import convert_to_ug, get_config
from mod_rawdata import proceed_data
from mod_sqlite import store_to_sqlite

class UtilsTest(unittest.TestCase):

    def testConvertToUG(self):
        invalid = '123456'
        self.assertEqual('123456', convert_to_ug(invalid))
        null_value = ''
        self.assertEqual('0.0', convert_to_ug(null_value))
        normal_0 = '0.027'
        self.assertEqual('27.0', convert_to_ug(normal_0))
        normal_0 = '0.0275'
        self.assertEqual('27.5', convert_to_ug(normal_0))
    def testGetConfig(self):
        my_cfg = get_config()
        self.assertEqual( 4, len(my_cfg))
        enmod = my_cfg[0]
        self.assertEqual('sqlite', enmod[0])
        interval = my_cfg[1]
        self.failIf(interval<=0, 'Invalid Interval Value')
        path = my_cfg[-2]
        #self.assertEqual('data', path['data'])
        self.assertEqual('log', path['log'])
        mails = my_cfg[-1]
        self.assertEqual('sean.s.luo@gmail.com', mails[0])

class RawDataTest(unittest.TestCase):
    
    def loadData(self, fname):
        fd = open('../testdata/' + fname, 'r')
        datastr = fd.read(-1)
        fd.close()
        return datastr
    
    def testAll(self):
        all = self.loadData('all.txt')
        data_table = proceed_data(all)
        self.assertEqual(120, len(data_table))
        row = data_table[0]
        self.assertEqual('北京', row[0])
        self.assertEqual('46.0', row[3])
        self.assertEqual('2011-11-30', row[5])
        row = data_table[119]
        self.assertEqual('克拉玛依', row[1])
        self.assertEqual('12.0', row[3])
        self.assertEqual('2011-11-30', row[5])
    
    def testShanghai(self):
        shanghai = self.loadData('shanghai.txt')
        data_table = proceed_data(shanghai, "上海")
        row0 = data_table[0]
        self.assertNotEqual('', row0[0])
        self.assertEqual('普陀',row0[1])
        self.assertEqual('121.397003E', row0[2])
        self.assertEqual('上海',row0[5])
        self.assertEqual('2011-11-30',row0[10])
        self.assertEqual('18',row0[11])
    
    def testShenyang(self):
        shanghai = self.loadData('shenyang.txt')
        data_table = proceed_data(shanghai, "沈阳")
        self.assertEqual(9, len(data_table))
        row0 = data_table[0]
        self.assertEqual('000221010000200', row0[0])
        self.assertEqual('太原街',row0[1])
        self.assertEqual('123.399722E', row0[2])
        self.assertEqual('41.797222N', row0[3])
        self.assertEqual('和平区太原街二段2号', row0[4])
        self.assertEqual('辽宁',row0[5])
        self.assertEqual('沈阳',row0[6])
        self.assertEqual('72.0',row0[7])
        self.assertEqual('32.0',row0[8])
        self.assertEqual('41.0',row0[9])
        self.assertEqual('2011-12-13',row0[10])
        self.assertEqual('19',row0[11])

class SQLiteTest(unittest.TestCase):
    
    def setUp(self):
        os.rename('../etc/air.ini', '../etc/air.ini.bak')
        os.rename('../etc/air.ini.test', '../etc/air.ini')
    def tearDown(self):
        os.rename('../etc/air.ini', '../etc/air.ini.test')
        os.rename('../etc/air.ini.bak', '../etc/air.ini')
    def test0NewAll(self):
        shutil.rmtree('../testdata/database', True)
        try:
            os.mkdir('../testdata/database')
        except:
            pass
        data_table = [['北京', '北京', '26.0', '46.0', '38.0', '2011-11-30', '18'],
                      ['河北', '保定', '82.0', '53.0', '85.0', '2011-11-30', '18'],
                      ['上海', '上海', '80.0', '50.0', '80.0', '2011-11-30', '18']]
        store_to_sqlite(data_table, '')
        conn = sqlite3.connect('../testdata/database/北京.db')
        rs = conn.execute('select * from tbl_average').fetchall()
        conn.close()
        rs = rs[0]
        self.assertEqual('2011-11-30', rs[0])
        self.assertEqual(18, rs[1])
        self.assertEqual(26.0, rs[2])
        self.assertEqual(46.0, rs[3])
        self.assertEqual(38.0, rs[4])
    def test1ExistAll(self):
        data_table = [['北京', '北京', '35.0', '55.0', '68.0', '2011-11-30', '19'],
                      ['河北', '保定', '13.0', '17.0', '10.0', '2011-11-30', '19'],
                      ['上海', '上海', '93.0', '77.0', '90.0', '2011-11-30', '19']]
        store_to_sqlite(data_table, '')
        conn = sqlite3.connect('../testdata/database/北京.db')
        rs = conn.execute('select * from tbl_average').fetchall()
        conn.close()
        self.assertEqual(2, len(rs))
        rs = rs[1]
        self.assertEqual('2011-11-30', rs[0])
        self.assertEqual(19, rs[1])
        self.assertEqual(35.0, rs[2])
        self.assertEqual(55.0, rs[3])
        self.assertEqual(68.0, rs[4])
    def test2CityNewStation(self):
        data_table = [['000231000005100', '普陀', '121.397003E', '31.2423N', 
                       '普陀区曹阳新村街道', '上海', '上海市', '11.1', '45.5', 
                       '11.8', '2011-11-30', '18']]
        store_to_sqlite(data_table, '上海')
        conn = sqlite3.connect('../testdata/database/上海.db')
        rs = conn.execute('select * from 普陀').fetchall()
        conn.close()
        rs = rs[0]
        self.assertEqual('2011-11-30', rs[0])
        self.assertEqual(18, rs[1])
        self.assertEqual(11.1, rs[2])
        self.assertEqual(45.5, rs[3])
        self.assertEqual(11.8, rs[4])
    def test3CityExistStationNewRecord(self):
        data_table = [['000231000005100', '普陀', '121.397003E', '31.2423N', 
                       '普陀区曹阳新村街道', '上海', '上海市', '111.1', '145.5', 
                       '111.8', '2011-11-30', '19']]
        store_to_sqlite(data_table, '上海')
        conn = sqlite3.connect('../testdata/database/上海.db')
        rs = conn.execute('select * from 普陀').fetchall()
        conn.close()
        self.assertEqual(2, len(rs))
        rs = rs[1]
        self.assertEqual('2011-11-30', rs[0])
        self.assertEqual(19, rs[1])
        self.assertEqual(111.1, rs[2])
        self.assertEqual(145.5, rs[3])
        self.assertEqual(111.8, rs[4])
    def test4CityExistStationExistRecord(self):
        data_table = [['000231000005100', '普陀', '121.397003E', '31.2423N', 
                       '普陀区曹阳新村街道', '上海', '上海市', '111.1', '145.5', 
                       '111.8', '2011-11-30', '19']]
        store_to_sqlite(data_table, '上海')
        conn = sqlite3.connect('../testdata/database/上海.db')
        rs = conn.execute('select * from 普陀').fetchall()
        conn.close()
        self.assertEqual(2, len(rs))
        rs = rs[1]
        self.assertEqual('2011-11-30', rs[0])
        self.assertEqual(19, rs[1])
        self.assertEqual(111.1, rs[2])
        self.assertEqual(145.5, rs[3])
        self.assertEqual(111.8, rs[4])
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()