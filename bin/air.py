#coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    modulize
Date:       2011-12-4
'''

import time, datetime
import sys
import os
from mod_utils import server_avg_url, get_config
from mod_utils import init_logger, get_cities, make_url, send_mail
from mod_rawdata import get_data, proceed_data,store_data

error_message = []
data_path = get_config()[-2]['data']
log_path = get_config()[-2]['log']
once   = False
stable = False

def common_steps(data_url, city_name):
    if not city_name:
        myname = 'Average data'
    else:
        myname = city_name
    try:
        data_str = get_data(data_url)
        if data_str == '': raise
    except:
        error = 'Unable to get data from the website for: %s' % myname
        logger.error(error)
        error_message.append(error)
        return False
    try:
        data_table = proceed_data(data_str, city_name)
        if data_table == []: raise
    except:
        error = ('Error occured when proceeding data: %s' % myname)
        logger.error(error)
        error_message.append(error)
        return False
    print ('Saving Data ...')
    all_ok = True
    for module in en_mod:
        store_method = ''
        imp_str = 'from mod_%s import store_to_%s as store_method' % (module, module)
        exec(imp_str)
        try:
            store_data(data_table, store_method, city_name)
            mod_status = True
        except:
            error = ('Unable to store data via module %s for city %s' %
                     (module, myname))
            logger.error(error)
            error_message.append(error)
            mod_status = False
        all_ok = all_ok and mod_status
    return all_ok

def get_detail():
    city = get_cities()
    if city == []:
        print ("Fatal error, cannot get city list, " +
               "restart the programme and try again.")
        return
    all_ok = True
    counter = 0
    sum = len(city)
    for one_city in city:
        counter += 1
        server_detail_url = make_url(one_city)
        status = common_steps(server_detail_url, one_city)
        if status:
            print str(counter) + '/' + str(sum) + '\t' + one_city + "\tok"
        all_ok = all_ok and status
    if(all_ok):
        logger.info('Detail: SUCCESS.')
        print ('************** Detail: SUCCESS. **************')
    
def get_average():
    status = common_steps(server_avg_url, '')
    if status:
        logger.info('Average: SUCCESS.')
        print ('************** Average: SUCCESS. **************')
    
def scan_daemon():
    '''
    Automatically check and get data from server every 30 minutes
    '''
    global en_mod
    while(1):
        global error_message  #12.12 Fix
        t_start = datetime.datetime.now()
        # ----------------- MAIN ----------------- #
        (en_mod, interval, _) = get_config()
        print ('Loop interval: ' + str(interval))
        module_install()
        logger.info('======= START ======')
        #get_average()
        get_detail()
        t_end = datetime.datetime.now()
        logger.info('======= END  =======')
        # ------------- ERROR HANDLING ----------- #
        if error_message != []:
            errors = '\n'.join(error_message)
            subject = time.strftime('Error Report: %Y-%m-%d %H')
            print errors
            try:
                send_mail(subject, errors)
                error_message = []
                print "Send mail OK."
            except:
                logger.error('Network down, cannot send email...')
        t_used = (t_end - t_start).seconds
        t_towait = interval - t_used
        if t_towait < 0:
            t_towait = 1
        logger.info("Time used: " + str(t_used))
        print ("Time used: " + str(t_used))
        # ------------------- END ---------------- #
        if once:
            break
        logger.info('Start to wait,' + str(t_towait) + ' seconds')
        print 'Start to wait for new data, ' + str(t_towait) + ' seconds ...'
        time.sleep(t_towait)
        logger.info('Wait complete, parse data again.')
    
def module_install():
    for module in en_mod:
        module_setup = ''
        imp_str = 'from mod_%s import module_setup as module_setup' % module
        exec(imp_str)
        module_setup()
    
def main(argv):
    try:
        cc = argv[1]
        print cc
        global once
        if cc == 'once':
            once = True
    except:
        module_install()
    scan_daemon()

try:
    os.mkdir("../" + data_path)
except:
    pass
try:
    os.mkdir("../" + log_path)
except:
    pass
logger = init_logger()
(en_mod, interval, _) = get_config()

if __name__ == '__main__':
    main(sys.argv)
    