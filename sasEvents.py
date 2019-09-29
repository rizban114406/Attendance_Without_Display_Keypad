from sasDatabase import sasDatabase
from sasAllAPI import sasAllAPI
from sasFile import sasFile
dbObject = sasDatabase()
database = dbObject.connectDataBase()
import datetime
apiObject = sasAllAPI()
def setDeviceTime():
    try:
        nowTime = apiObject.getTime()
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{setDEviceTime}",str(e))
    return nowTime

def updateTimeDuration():
    timeToCalculate = dbObject.getRowWithNoDurationTimeConfig(database)
    if timeToCalculate != '0':
        realTime = setDeviceTime()
        if realTime == "Not Successfull":
            for restartTime in timeToCalculate:
                duration = int(datetime.datetime.strptime(str(realTime), '%Y-%m-%d %H:%M:%S') - \
                             datetime.datetime.strptime(str(restartTime[1]), '%Y-%m-%d %H:%M:%S'))
                dbObject.updateDurationTimeConfig(restartTime[0],duration,database)
                return 1
        else:
            return 0
    else:
        return 1
            
if __name__ == '__main__':
    try:
        deviceInfo = dbObject.getAllDeviceInfo(database)
        durationUpdateFlag = updateTimeDuration()()
        if deviceInfo != '0' and durationUpdateFlag == 1:
            timeIntervals = dbObject.getDataTimeConfig(database)
            deviceInfoData = {"deviceid"   : deviceInfo[1],\
                              "companyid"  : deviceInfo[3],\
                              "address"    : deviceInfo[4],\
                              "subaddress" : deviceInfo[5]}
            
            for intervals in timeIntervals:
                allEventData = dbObject.getAllEventData(intervals[0],database)
                eventInfoData =[]
                id_count = []
                for reading in allEventData:
                    id_count.append(reading[0])
                    eventTime = (datetime.datetime.strptime(str(reading[3]), '%Y-%m-%d %H:%M:%S') + \
                                 datetime.timedelta(seconds=int(intervals[2]))).strftime('%Y-%m-%d %H:%M:%S')
                    
                    eventInfoData.append({"eventdatetime"       : str(eventTime),\
                                          "uniqueid"            : str(reading[1]), \
                                          "fingerorcardnumber"  : str(reading[2]),\
                                          "eventtype"           : str(reading[4]) , \
                                          "companyid"           : str(reading[5])})
                    mainData = {"deviceinfo" : deviceInfoData, \
                                "eventdata"  : eventInfoData}
                    message = apiObject.sendEventData(mainData)
                    if message == "Success":
                        for Id in id_count :
                            dbObject.deleteFromEventListTable(Id,database)
                        dbObject.deleteFromTimeConfig(intervals[0],database)
                    elif message == "Not Successfull":
                        print("Something Went Wrong")
                    else:
                        print(message)
            dbObject.databaseClose(database)
    except Exception as e:
        #print str(e)
        fileObject = sasFile()
        dbObject.databaseClose(database)
        fileObject.updateExceptionMessage("sasEvents{__main__}",str(e))
