# coding=utf-8
__author__ = 'zhangkai'


######################################
# HaiJia Lesson2 Reservation Software
# Author: zhangkai
# Email:  ocelot1985@163.com
######################################


import random
import time
import datetime
import urllib
import urllib2
import json
import sys
import logging
from xml.dom.minidom import parseString

from bs4 import BeautifulSoup
import OcrKing
import DateDiffUtil


def setupLog():
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='E:\\car\\Version3\\v5.0\\car.log',
                filemode='w')


class myHTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        pass

class RedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self,req,fp,code,msg,hdrs):
        pass

    def http_error_302(self,req,fp,code,msg,hdrs):
        #print 'in my 302 handle'
        print 'in 302'
        print code
        print msg
        print hdrs
        return hdrs

    def http_error_default(self, req, fp, code, msg, hdrs):
        print 'in my default handle'
        pass

# processing image logic.
# it is finished yet.
def getImgCode(map):
    reTry = 3
    URL = 'http://haijia.bjxueche.net/tools/CreateCode.ashx?'
    param1 = 'key=ImgCode'
    param2 = 'random=' + str(random.random())

    HEADER = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Cookie' : map['Cookie'],
        'Accept' : 'image/webp,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate, sdch',
        'Accept-Language' : 'zh-CN,zh;q=0.8',
        'Connection' : 'keep-alive',
        'Host' : 'haijia.bjxueche.net',
        'Referer' : 'http://haijia.bjxueche.net/',
    }
    REQURL = URL + param1 + '&' + param2

    req = urllib2.Request(REQURL, headers=HEADER)
    while reTry > 0:
        try:
            res = urllib2.urlopen(req)
            cookie = res.info()['set-cookie']
            #cookie = res.info()['set-cookie'].split(' ')[0]
            file = open('new.gif', 'wb')
            file.write(res.read())
            file.close()
            return cookie
        except urllib2.URLError as e:
            reTry = reTry - 1
            print 'getImgCode URL Error!', e
            logging.debug('getImgCode URL Error!' + str(e))
            if reTry <= 0:
                sys.exit()


def getCarInfo(cookie, date, way):
    HEADER = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Referer' : 'http://haijia.bjxueche.net/ych2.aspx',
        'Cookie' : cookie
        }
    #pageSize and pageNum usually didnt change.
    #yyrq is date; yysd and xllxID may be changed with book period of day.
    POSTDATA = {
        'yyrq' : date,
        'yysd' : way,
        'xllxID' : '3',
        'pageSize' : 35,
        'pageNum' : 1
    }

    HOSTURL = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/GetCars'

    endata = urllib.urlencode(POSTDATA)
    req = urllib2.Request(HOSTURL,endata,HEADER)
    res = urllib2.urlopen(req)

    info = res.read()
    # check whether response body is invalid json.
    # if not, we need reinput num pic
    #try:
    #eval(info)
    return info
    #except SyntaxError as e:
    #   handleReinputNumPic(info)

def login(valid_code, map, cookie_img):
    #map = accessHomePage()
    #url = 'http://haijia.bjxueche.net/login.aspx'
    url = 'http://haijia.bjxueche.net/Login.aspx?LoginOut=true'
    user = 'YOURNAME'
    passwd = 'YOURPASSWORD'
    data = {
        '__VIEWSTATE' : map['__VIEWSTATE'],
        '__VIEWSTATEGENERATOR' : map['__VIEWSTATEGENERATOR'],
        '__EVENTVALIDATION' : map['__EVENTVALIDATION'],
        'txtUserName' : user,
        'txtPassword' : passwd,
        'txtIMGCode'  : valid_code,
        'BtnLogin'    : '登  录',
    }
    
    #print valid_code
    #print user
    #print passwd
    #print map['__VIEWSTATE']
    #print map['__VIEWSTATEGENERATOR']
    #print map['__EVENTVALIDATION']

    header = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding' : 'gzip,deflate',
        'Upgrade-Insecure-Requests' : 1,
        'Accept-Language' : 'zh-CN,zh;q=0.8',
        'Cache-Control' : 'max-age=0',
        'Connection' : 'keep-alive',
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Cookie' : map['Cookie'] + ' ' + cookie_img[:-1],
        'Host' : 'haijia.bjxueche.net',
        'Origin' : 'http://haijia.bjxueche.net',
        'Referer' : 'http://haijia.bjxueche.net/',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36'
    }


    encoded = urllib.urlencode(data)

    debug_handler = urllib2.HTTPHandler(debuglevel=1)
    opener = urllib2.build_opener(RedirectHandler)

    req = urllib2.Request(url,encoded,header)
    print req.get_data()
    print req.get_full_url()
    print req.get_type()
    print req.get_header('Cookie')

    headers = opener.open(req)
    
    for key in headers:
        print key
        print headers[key]
    cookie_login = headers['Set-Cookie'].split(' ')[0]

    return cookie_login


def accessHomePage():
    reTry = 3
    url = 'http://haijia.bjxueche.net/'

    while reTry > 0:
        try:
            res = urllib2.urlopen(url)
            cookie = res.info()['set-cookie']
            #cookie = res.info()['set-cookie'].split(' ')[0]
            soup = BeautifulSoup(res.read())
            content = soup.find_all('input',id='__VIEWSTATEGENERATOR')
            #print dir(content[0])
            value1 = content[0]['value']
            content2 = soup.find_all('input',id='__EVENTVALIDATION')
            value2 = content2[0]['value']
            content3 = soup.find_all('input', id = '__VIEWSTATE')
            value3 = content3[0]['value']
            return {'__VIEWSTATEGENERATOR' : value1, '__EVENTVALIDATION' : value2, '__VIEWSTATE' : value3, 'Cookie' : cookie}
        except urllib2.URLError as e:
            reTry = reTry - 1
            print 'Access Home Page Error!', e
            if reTry <= 0:
                sys.exit()

    return None


#@Function: Reserve car
#@Return: 0 for successful, 1 for fail
def bookCar(cookie, date, sd, carnum):
    #cookie = readFirefoxCookie()
    result = 1
    HEADER = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Referer' : 'http://haijia.bjxueche.net/ych2.aspx',
        'Cookie' : cookie
        }

    POSTDATA = {
        'yyrq' : date,
        'xnsd' : sd,
        'cnbh' : carnum,
        'imgCode' : '',
        'KMID' : '3'
    }

    HOSTURL = 'http://haijia.bjxueche.net/Han/ServiceBooking.asmx/BookingCar'

    endata = urllib.urlencode(POSTDATA)
    req = urllib2.Request(HOSTURL,endata,HEADER)
    res = urllib2.urlopen(req)

    # retrieve data from xml body data.
    body = res.read()
    dom = parseString(body)
    root = dom.documentElement
    data = root.firstChild.data
    info = json.loads(data)
    if info[0]['Result'] == True:
        result = 0

    return result


def handleXmlResult(xmlResult):
    dom = parseString(xmlResult)
    root = dom.documentElement
    itemlist = root.getElementsByTagName('Result')
    return itemlist[0].firstChild.data


def handleXmlStatus(xmlResult):
    dom = parseString(xmlResult)
    root = dom.documentElement
    itemlist = root.getElementsByTagName('Status')
    status = itemlist[0].firstChild.data
    if status == 'false':
        return 1
    if status == 'true':
        return 0
    
def waitForWebsiteStart():
    waitInSecs = DateDiffUtil.mergeTimeDiffer()
    print 'sleep in N seconds, ' + str(waitInSecs)
    logging.debug('sleep in N seconds, ' + str(waitInSecs))
    time.sleep(waitInSecs)
    
    
#Param:
#   @way(str type) is when you want to train in a day.
#   For example, 0 for morning, 1 for afternoon, 2 for night.
#   default value 9, program will try 0, 1, 2 in sequence way.
def loopCar(date, way='9'):
    choice = ['711','1216','1720']
    info = ['morning','afternoon','night']
    cnt = 0
    retryd = 8
    retry = 5

    #waitForWebsiteStart()
    map = accessHomePage()
    while True:
    #while retryd > 0:
        cookie = getImgCode(map)
        print 'imgcookie: ', cookie
        xmlresult = OcrKing.drive()
        flag = handleXmlStatus(xmlresult)
        if flag == 1:
            print "OcrKing recognize Imgcode fail!"
            logging.debug('OcrKing recognize Imgcode fail!')
            time.sleep(1) 
            #retryd -= 1
            continue
        # flag==0, begin to login
        valid_code = handleXmlResult(xmlresult)
        try:
            cook_login = login(valid_code, map, cookie)
            print "finished login!"
            logging.debug('finished login!')
            break
        except AttributeError as e:
            print "login error! ", e
            logging.debug('login error! ' + str(e))
            # the website cannot login, because of service is not available
            time.sleep(3)
            #retryd -= 1
            
    if retryd <= 0:
        print "Cannot login! Because of Imgcode dont recognized correctly!"
        logging.debug("Cannot login! Because of Imgcode dont recognized correctly!")
        exit();

    while True:
        MorningOrAfter = cnt % 2
        dom = parseString(getCarInfo(cook_login, date, choice[MorningOrAfter]))
        root = dom.documentElement
        if '[]_0' == str(root.firstChild.data):
            print "%s dont have car to book. keep trying..." % info[MorningOrAfter]
            logging.debug("%s dont have car to book. keep trying..." % info[MorningOrAfter])
            cnt = cnt + 1
            timeNow = datetime.datetime.now()
            timeEnd = DateDiffUtil.getTermExeDate()
            if timeNow > timeEnd:
                sys.exit()
        else:
            data = root.firstChild.data[0:-2]
            #info is a list of json array
            info = json.loads(data)
            print info
            random.seed()
            indx = random.randint(0,len(info)) - 1
            #info = json.loads(root.firstChild.data[0:-3])
            #print info
            #info[0] is first json data
            #in the response json data, there's 3 key-value pairs
            key = info[indx].keys()
            #print key[0], info[0][key[0]]
            #print key[1], info[0][key[1]]
            #print key[2], info[0][key[2]]
            flag = bookCar(cook_login, info[indx]["YYRQ"], info[indx]["XNSD"], info[indx]["CNBH"])
            if flag == 0:
                print "Book Car successfully!!"
                logging.debug("Book Car successfully!!")
                break
        print 'in while'
        logging.debug('in while')
        #print type(root.firstChild.data)
        #time.sleep(1)

def usage():
    print "Usage: car.py param"
    print "param is the date when you want to reserve a training car."
    print "For example,  car.py 20141224"


if __name__ == '__main__':
    setupLog()
    if (len(sys.argv) < 2):
        starttime = datetime.datetime.now()
        booktime = starttime + datetime.timedelta(days=7)
        bookdate = booktime.strftime('%Y%m%d')
        loopCar(bookdate)
    elif(len(sys.argv) == 2):
        loopCar(sys.argv[1])
    else:
        loopCar(sys.argv[1], sys.argv[2])
    print 'end of main'
