import datetime 
from sasFile import sasFile
fileObject = sasFile()
from sasDatabase import sasDatabase
dbObject = sasDatabase()
database = dbObject.connectDataBase()
from sasAllAPI import sasAllAPI
apiObject = sasAllAPI()
import os
timeToStart = 10
def setDeviceTime():
    try:
        nowTime = apiObject.getTime()
        if nowTime != "Not Successfull":
            command = "sudo date -s "+ '"'+nowTime+'"'
            os.system(command)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{setDEviceTime}",str(e))
    return nowTime
        
if __name__ == '__main__':
    NowTime = (datetime.datetime.now() - datetime.timedelta(seconds=timeToStart)).strftime('%Y-%m-%d %H:%M:%S')
    startTime = fileObject.readStartTime()
    if startTime != None:
        dbObject.updateRestartTimeConfig(startTime,NowTime,database)
    realTime = setDeviceTime()
    if realTime == "Not Successfull": 
        NowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dbObject.insertIntoTimeConfig(NowTime, database)
        fileObject.updateStartTime(NowTime)
    else:
        dbObject.insertIntoTimeConfig(realTime, database)
        fileObject.updateStartTime(realTime)
        
    