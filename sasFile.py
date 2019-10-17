import datetime
class sasFile:

    def readDesiredTask(self):
        try:
            file = open('desiredTask.txt','r')
            desiredTask = file.read(1)
            file.close()
        except Exception as e:
            self.updateDesiredTask('1')
            self.updateExceptionMessage("sasFile{readDesiredTask}",str(e))
            desiredTask = '1'
        return desiredTask

    def updateDesiredTask(self,command):
        file = open('desiredTask.txt', 'w+')
        file.write(command)
        file.close()
        
    def readSyncConfStatus(self):
        try:
            file = open('syncConfStatus.txt','r')
            state = file.read(1)
            file.close()
        except Exception as e:
            self.updateSyncConfStatus('0')
            self.updateExceptionMessage("sasFile{readDesiredTask}",str(e))
            state = '0'
        return state
        
    def updateSyncConfStatus(self,state):
        file = open('syncConfStatus.txt', 'w+')
        file.write(state)
        file.close()

    def updateExceptionMessage(self,exceptionScript,exceptionMessage):
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = "Exception From :"     + exceptionScript  + \
                  " Exception Message: " + exceptionMessage + \
                  " Time: "              + str(nowTime)     + "\n"
        file = open('exceptionMessage.txt', 'a+')
        file.write(message)
        file.close()

    def updateConfigUpdateStatus(self,status):
        file = open('configUpdateStatus.txt', 'w+')
        file.write(status)
        file.close()

    def readConfigUpdateStatus(self):
        try:
            file = open('configUpdateStatus.txt','r')
            configStatus = file.read(1)
            file.close()
            return configStatus
        except Exception as e:
            self.updateConfigUpdateStatus('0')
            self.updateExceptionMessage("sasFile{readConfigUpdateStatus}",str(e))
            return '0'

    def readStoredIndex(self):
        try:           
            file = open('storedIndex.txt','r')
            template = file.readline()
            storedTemplate = template.split('-')
            file.close()
        except Exception as e:
            storedTemplate = []
            self.updateStoredIndex("")
            self.updateExceptionMessage("sasFile{readStoredIndex}",str(e))
        return storedTemplate

    def updateStoredIndex(self,storedIndex):
        file = open('storedIndex.txt', 'w+')
        file.write(storedIndex)
        file.close()

    def updateHearBitURL(self,url):
        file = open('heartBitUrl.txt', 'w+')
        file.write(url)
        file.close()
    
    def readStartTime(self):
        try:           
            file = open('startTime.txt','r')
            startTime = file.readline()
            file.close()
        except Exception as e:
            self.updateStartTime("")
            startTime = None
            self.updateExceptionMessage("sasFile{readStartTime}: ",str(e))
        return startTime
    
    def updateStartTime(self,startTime):
        file = open('startTime.txt', 'w+')
        file.write(startTime)
        file.close()
        
    def readRequestId(self):
        try:           
            file = open('requestId.txt','r')
            requestId = file.readline()
            file.close()
        except Exception as e:
            self.updateRequestId("0")
            requestId = "0"
            self.updateExceptionMessage("sasFile{readStartTime}: ",str(e))
        return requestId
    
    def updateRequestId(self,requestId):
        file = open('requestId.txt', 'w+')
        file.write(str(requestId))
        file.close()
        
