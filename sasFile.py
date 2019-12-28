import datetime
class sasFile:

    def readCurrentTask(self):
        try:
            file = open('currentTask.txt','r')
            currentTask = file.read(1)
            file.close()
        except Exception as e:
            self.updateCurrentTask('1')
            self.updateExceptionMessage("sasFile{readCurrentTask}",str(e))
            currentTask = '1'
        return currentTask

    def updateCurrentTask(self,command):
        file = open('currentTask.txt', 'w+')
        file.write(command)
        file.close()
    
    def readGSMStatus(self):
        try:
            file = open('gsmStatus.txt','r')
            gsmStatus = file.read(1)
            file.close()
        except Exception as e:
            self.updateGSMStatus('0')
            self.updateExceptionMessage("sasFile{readGSMStatus}",str(e))
            gsmStatus = '0'
        return gsmStatus

    def updateGSMStatus(self,gsmStatus):
        file = open('gsmStatus.txt', 'w+')
        file.write(gsmStatus)
        file.close()
        
    def readSyncStatus(self):
        try:
            file = open('syncStatus.txt','r')
            state = file.read(1)
            file.close()
        except Exception as e:
            self.updateSyncConfStatus('0')
            self.updateExceptionMessage("sasFile{readSyncConfStatus}: ",str(e))
            state = '0'
        return state
        
    def updateSyncStatus(self,state):
        file = open('syncStatus.txt', 'w+')
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
        
    def readRequestId(self):
        try:           
            file = open('requestId.txt','r')
            requestId = file.readline()
            requestId = requestId.replace('\n','')
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
            self.updateEnrollingUserInfo("0","0")
            self.updateExceptionMessage("sasFile{readEnrollingUserInfo}: ",str(e))
            info = ["0","0"]
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
        
    def readCurrentEthernetSettings(self):
        try:           
            file = open('ethernet.txt','r')
            ethernet = file.readline()
            ethernet = ethernet.replace('\n','')
            file.close()
        except Exception as e:
            self.writeCurrentEthernetSettings("1-")
            ethernet = "1-0-0-0"
            self.updateExceptionMessage("sasFile{readCurrentEthernetSettings}: ",str(e))
        return ethernet
    
    def writeCurrentEthernetSettings(self,lines):
        file = open('ethernet.txt','w+')
        file.writelines(lines)
        file.close()
        
    def readNetworkStatus(self):
        try:
            file = open('networkStatus.txt','r')
            networkStatus = file.readline()
            networkStatus = networkStatus.replace('\n','')
            file.close()
        except Exception as e:
            self.updateExceptionMessage("sasFile{readNetworkStatus}: ",str(e))
            self.updateNetworkStatus("1","1")
            networkStatus = '1-1'
        return networkStatus
    
    def updateNetworkStatus(self,primary,secondary):
        networkStatus = primary + '-' + secondary
        file = open('networkStatus.txt', 'w+')
        file.writelines(networkStatus)
        file.close()
        
