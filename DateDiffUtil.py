import urllib2
import datetime

# time length between website start service and our program start to scan (in seconds)
TIME_TO_BEGIN = 30


def getServerDate():
    url = 'http://haijia.bjxueche.net'
    res = urllib2.urlopen(url)
    resHeaders = res.info()
    dateStr = resHeaders['Date']
    serverTime = datetime.datetime.strptime(dateStr, '%a, %d %b %Y %X %Z')
    #addTime = datetime.timedelta(hours=8)
    #serverTimeNow = serverTime + addTime
    print 'server time: ',serverTime
    return serverTime


def getLocalPcDate():
    now = datetime.datetime.now()
    print 'local time: ',now
    return now

    
def getWebsiteStartDate():
    today = datetime.datetime.today()
    #startDate = datetime.datetime(today.year,today.month,today.day,1,45)
    startDate = datetime.datetime(today.year,today.month,today.day,23,34)
    print startDate
    return startDate

    
def getTermExeDate():
    today = datetime.datetime.today()
    #endDate = datetime.datetime(today.year,today.month,today.day,1,35)
    endDate = datetime.datetime(today.year,today.month,today.day,23,50)
    print endDate
    return endDate


def calTimerDifferInSeconds():
    serverTime = getServerDate()
    localTime = getLocalPcDate()
    if serverTime > localTime:
        print 'server is faster than local'
        #deltaTime = localTime - serverTime
        #deltaTime = serverTime - localTime
    else:
        print 'server is slower than lcoal'
        #deltaTime = localTime - serverTime
    deltaTime = serverTime - localTime
        
    print deltaTime.total_seconds()
    return deltaTime.total_seconds()


def mergeTimeDiffer():
    timeDiff = calTimerDifferInSeconds()
    print 'time diff: ',timeDiff
    timeLen = getWebsiteStartDate() - getLocalPcDate()
    return timeLen.total_seconds() + timeDiff - TIME_TO_BEGIN

    
if __name__ == '__main__':
    print mergeTimeDiffer()
