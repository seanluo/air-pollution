# coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    module
Date:       2011-12-4
'''

import os
from mod_utils import get_config


def store_to_text(data_table, city_name):
    data_path = get_config()[-2]['data']
    date_time = str(data_table[0][-2]) + str(data_table[0][-1])
    if city_name == '':
        file_name = "../" + data_path + "/average/" + date_time + ".txt"
    else:
        try:
            os.mkdir("../" + data_path + "/detail/" + date_time)
        except:
            pass
        file_name = "../" + data_path + "/detail/" + date_time + "/" + city_name + ".txt"

    fd = open(file_name, 'w')
    for row in data_table:
        line = ""
        for item in row:
            line += item
            line += "\t"
        line += "\n"
        fd.write(line)
    fd.close()


def module_setup():
    data_path = get_config()[-2]['data']
    try:
        os.mkdir("../" + data_path + "/average")
    except:
        pass
    try:
        os.mkdir("../" + data_path + "/detail")
    except:
        pass
