# coding: utf-8
'''
Author:     Sean Luo
Email:      Sean.S.Luo@gmail.com
Version:    module
Date:       2011-12-1
Description:通过基本库实现日志功能，网址生成，邮件发送，单位转换和配置文件读取
'''

# import datetime
import urllib
import logging
import smtplib
import ConfigParser
import xml.dom.minidom
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

server_avg_url = "http://58.68.130.147/IS/AjaxDemo/query.ashx?map=China&method=QueryBySql&queryParam=%7b%22customParams%22%3a%22%22%2c%22expectCount%22%3anull%2c%22hasGeometry%22%3afalse%2c%22highlight%22%3anull%2c%22queryAllLayer%22%3afalse%2c%22queryLayers%22%3a%5b%7b%22groupClause%22%3a%22%22%2c%22layerId%22%3a0%2c%22layerName%22%3a%22CityStation_ORG1%40China400%22%2c%22returnFields%22%3a%5b%22CHINESE_CH%22%2c%22NAME%22%2c%22SO2%E5%AE%9E%E6%97%B6%22%2c%22NO2%E5%AE%9E%E6%97%B6%22%2c%22PM10%E5%AE%9E%E6%97%B6%22%2c%22API%22%2c%22DATATIME%22%5d%2c%22sortClause%22%3a%22order+by+SHOWINDEX%22%2c%22whereClause%22%3a%22%22%2c%22relQueryTableInfos%22%3anull%7d%5d%2c%22networkType%22%3a0%2c%22returnFields%22%3anull%2c%22startRecord%22%3a0%2c%22whereClause%22%3a%22%22%2c%22returnCenterAndBounds%22%3atrue%2c%22returnShape%22%3atrue%7d&trackingLayerIndex=-1&userID=%227837598d-49e3-4578-9c94-4bdfa933e529%22&"

prefix_ch = u'http://58.68.130.147/IS/AjaxDemo/query.ashx?map=China&method=QueryBySql&queryParam=%7b%22customParams%22%3a%22%22%2c%22expectCount%22%3anull%2c%22hasGeometry%22%3atrue%2c%22highlight%22%3anull%2c%22queryAllLayer%22%3afalse%2c%22queryLayers%22%3a%5b%7b%22groupClause%22%3a%22%22%2c%22layerId%22%3a0%2c%22layerName%22%3a%22CityStation_Now_ORG1%40China400%22%2c%22returnFields%22%3anull%2c%22sortClause%22%3a%22%22%2c%22whereClause%22%3a%22CHINESE_CH%3d\''
prefix_na = u'http://58.68.130.147/IS/AjaxDemo/query.ashx?map=China&method=QueryBySql&queryParam=%7b%22customParams%22%3a%22%22%2c%22expectCount%22%3anull%2c%22hasGeometry%22%3atrue%2c%22highlight%22%3anull%2c%22queryAllLayer%22%3afalse%2c%22queryLayers%22%3a%5b%7b%22groupClause%22%3a%22%22%2c%22layerId%22%3a0%2c%22layerName%22%3a%22CityStation_Now_ORG1%40China400%22%2c%22returnFields%22%3anull%2c%22sortClause%22%3a%22%22%2c%22whereClause%22%3a%22NAME%3d\''
postfix = u'\'%22%2c%22relQueryTableInfos%22%3anull%7d%5d%2c%22networkType%22%3a0%2c%22returnFields%22%3anull%2c%22startRecord%22%3a0%2c%22whereClause%22%3a%22%22%2c%22returnCenterAndBounds%22%3atrue%2c%22returnShape%22%3atrue%7d&trackingLayerIndex=-1&userID=%222c44ab3a-2c09-46b2-8e85-addf40d8c6d9%22&'


def is_mu_city(city_name):
    return city_name in [u'北京', u'上海', u'天津', u'重庆']


def make_url(city_name):
    quoted_city = urllib.quote(city_name.encode('utf-8'))
    if is_mu_city(city_name):
        # special cities have special URLs
        server_url = prefix_ch + quoted_city + postfix
    else:
        server_url = prefix_na + quoted_city + postfix
    return server_url


def init_logger():
    '''
    initialize the logging system
    '''
    global logger
    log_path = get_config()[-2]['log']
    # logfile = '../log/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
    logfile = '../' + log_path + '/db_air.log'
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger


def get_config():
    cfg = ConfigParser.ConfigParser()
    cfg.read('../etc/air.ini')
    ins_mod = cfg.options('module')
    enable_mod = []
    for mod in ins_mod:
        if cfg.getboolean('module', mod):
            enable_mod.append(mod)
    interval = cfg.getint('param', 'interval')
    ins_mail = cfg.options('email')
    mail_list = []
    for mail in ins_mail:
        if cfg.getboolean('email', mail):
            mail_list.append(mail)
    path = {'data': cfg.get('path', 'data'),
            'log': cfg.get('path', 'log')}
    result = [enable_mod, interval, path, mail_list]
    return result


def get_cities():
    city = []
    try:
        doc = xml.dom.minidom.parse('../etc/city.xml')
        nodes = doc.getElementsByTagName('field')
    except:
        print("Cannot resolve city names from XML.")
        return []
    for node in nodes:
        city_name = node.childNodes[0].nodeValue
        city.append(city_name)
    return city


def convert_to_ug(str_value):
    '''
    convert mg to ug, return in string format
    '''
    if not str_value:
        return '0.0'
    else:
        if str_value != '123456':
            str_value = str(float(str_value) * 1000)
        return str_value


def sendEmail(authInfo, fromAdd, toAdd, subject, plainText):
    strFrom = fromAdd
    strTo = ','.join(toAdd)
    server = authInfo.get('server')
    user = authInfo.get('user')
    passwd = authInfo.get('password')

    if not (server and user and passwd):
        print 'incomplete login info, exit now'
        return
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = strFrom
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgText = MIMEText(plainText, 'plain', 'utf-8')
    msgAlternative.attach(msgText)

    smtp = smtplib.SMTP()
    smtp.set_debuglevel(0)
    smtp.connect(server)
    smtp.login(user, passwd)
    smtp.sendmail(strFrom, strTo, msgRoot.as_string())
    smtp.quit()
    return


def send_mail(iSubject, iContent):
    authInfo = {}
    authInfo['server'] = 'smtp.163.com'
    authInfo['user'] = 'fudan_data'
    authInfo['password'] = '!@#@!2011'
    fromAdd = 'fudan_data@163.com'
    toAdd = get_config()[-1]
    subject = iSubject
    plainText = iContent
    sendEmail(authInfo, fromAdd, toAdd, subject, plainText)
