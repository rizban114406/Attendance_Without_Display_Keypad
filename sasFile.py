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
        
    def readEnrollingUserInfo(self):
        try:           
            file = open('enrollingUserInfo.txt','r')
            requestInfo = file.readline()
            file.close()
            info = requestInfo.split('$')
        except Exception as e:
            self.updateExceptionMessage("sasFile{readEnrollingUserInfo}: ",str(e))
        return (info[0],info[1])
        
    def updateEnrollingUserInfo(self, uniqueId, selectedCompany):
        data = str(uniqueId) + "$" + str(selectedCompany)
        file = open('enrollingUserInfo.txt', 'w+')
        file.write(str(data))
        file.close()
        
    
    def readCurrentVersion(self):
        file = open('currentVersion.txt', 'r')
        version = file.readline()
        version = version.replace('\n','')
        file.close()
        return float(version)
    
    def updateCurrentVersion(self,version):
        file = open('currentVersion.txt', 'w')
        file.write(version)
        file.close()    
        
    def readWifiSettings(self):
        file = open('/etc/wpa_supplicant/wpa_supplicant.conf','r')
        lines = file.readlines()
        file.close()
        return lines
    
    def writeWifiSettings(self,lines):
        file = open('/etc/wpa_supplicant/wpa_supplicant.conf','w')
        file.writelines(lines)
        file.close()
        
    def readEthernetSettings(self):
        file = open('/etc/dhcpcd.conf','r')
        lines = file.readlines()
        file.close()
        return lines
    
    def writeEthernetSettings(self,lines):
        file = open('/etc/dhcpcd.conf','w')
        file.writelines(lines)
        file.close()
        
