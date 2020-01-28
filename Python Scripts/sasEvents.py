import time
from sasDatabase import sasDatabase
from sasAllAPI import sasAllAPI
from sasFile import sasFile
from sasGPIO import sasGPIO

gpioObject = sasGPIO()
fileObject = sasFile()
dbObject = sasDatabase()
database = dbObject.connectDataBase()
apiObjectPrimary = sasAllAPI(1)
apiObjectSecondary = sasAllAPI(2)
if __name__ == '__main__':
    global apiObjectSecondary
    deviceId = dbObject.getDeviceId(database)
    gpioObject.turnLEDON('R+B')
    if deviceId != 0:
        if (dbObject.checkSecondaryAddressAvailable(database) == 1 and\
            fileObject.readSyncStatus() == '0'):
            fileObject.updateSyncStatus('1')
        if(apiObjectPrimary.checkUpdateRequest(deviceId) == 0 and \
           dbObject.checkAddressUpdateRequired(1, database) == 0):
            print("Primary Check Update Request Server: 0, Check Update Required Local: 0\n")
            dbObject.resetUpdatedRequiredStatus(1,database)
            apiObjectPrimary.confirmUpdateRequest(deviceId)
            
        if(dbObject.checkSecondaryAddressAvailable(database) == 1 and \
           dbObject.checkAddressUpdateRequired(2, database) == 0):
            print("Secondary Address Available: 1, Check Update Required Local: 0")
            if (apiObjectSecondary.checkUpdateRequest(deviceId) == 0):
                print("Secondary Check Update Required Server: 0\n")
                dbObject.resetUpdatedRequiredStatus(2,database)
                apiObjectSecondary.confirmUpdateRequest(deviceId)
        dbObject.databaseClose(database)           
        while True:
            primary, secondary = fileObject.readNetworkStatus().split('-')
            print("Primary Network: {}, Secondary Network: {}".format(primary,secondary))
            primaryStatus = apiObjectPrimary.checkServerStatus()
            print("Primary Network: {}".format(primaryStatus))
            database = dbObject.connectDataBase()
            if (primaryStatus == 1):
                print("Network is Available")
                if (fileObject.readCurrentTask() == '1'):
                    gpioObject.turnLEDON('OFF')
                    gpioObject.turnLEDON('B')
            elif (primaryStatus == 0):
                print("Network is Not Available")
                if (fileObject.readCurrentTask() == '1'):
                    gpioObject.turnLEDON('OFF')
                    gpioObject.turnLEDON('R+B')
            if (primaryStatus == 0 and primary == '1'):
                primary = '0'
                fileObject.updateNetworkStatus(primary,secondary)
                
            elif (primaryStatus == 1 and primary == '0'):
                if(apiObjectPrimary.checkUpdateRequest(deviceId) == 0 and \
                   dbObject.checkAddressUpdateRequired(1, database) == 0):
                    print("Primary Check Update Request Server: 0, Check Update Required Local: 0")
                    dbObject.resetUpdatedRequiredStatus(1, database)
                    apiObjectPrimary.confirmUpdateRequest(deviceId)
                primary = '1'
                fileObject.updateNetworkStatus(primary,secondary)
            
            if (dbObject.checkSecondaryAddressAvailable(database) == 1):
                print("Secondary Address Available: 1")
                apiObjectSecondary = sasAllAPI(2)
                secondaryStatus = apiObjectSecondary.checkServerStatus()
                print("Secondary Network: {}".format(secondaryStatus))
                if (secondaryStatus == 0 and secondary == '1'):
                    secondary = '0'
                    fileObject.updateNetworkStatus(primary,secondary)
                    
                elif (secondaryStatus == 1 and secondary == '0'):
                    if fileObject.readSyncStatus() == '0':
                        fileObject.updateSyncStatus('1')
                    if(apiObjectSecondary.checkUpdateRequest(deviceId) == 0 and \
                       dbObject.checkAddressUpdateRequired(2, database) == 0):
                        print("Secondary Check Update Required Server: 1, Check Update Required Local: 0")
                        dbObject.resetUpdatedRequiredStatus(2, database)
                        apiObjectSecondary.confirmUpdateRequest(deviceId)
                    secondary = '1'
                    fileObject.updateNetworkStatus(primary,secondary)
                
                if (secondaryStatus == 1):
                    try:
                        deviceInfo = dbObject.getAllDeviceInfo(database)
                        if deviceInfo != '0':
                            allEventData = dbObject.getAllEventData(database)
                            deviceInfoData = {"deviceid"   : deviceInfo[2],\
                                              "companyid"  : deviceInfo[8],\
                                              "address"    : deviceInfo[3],\
                                              "subaddress" : deviceInfo[6],\
                                              "devicename" : deviceInfo[4]}
                            eventInfoData =[]
                            date_count = []
                            for reading in allEventData:
                                date_count.append(reading[2])
                                eventInfoData.append({"eventdatetime"       : str(reading[2]),\
                                                      "uniqueid"            : str(reading[0]), \
                                                      "fingerorcardnumber"  : str(reading[1]),\
                                                      "eventtype"           : str(reading[3])})
                            mainData = {"deviceinfo" : deviceInfoData, \
                                        "eventdata"  : eventInfoData}
                            print("Event Data: {}".format(mainData))
                            if(len(allEventData) > 0):
                                message = apiObjectSecondary.sendEventData(mainData)
                                print(message)
                                if message == "Success":
                                    print("Sent Successfully")
                                    print(date_count)
                                    for date in date_count :
                                        print(date)
                                        dbObject.deleteFromEventListTable(date,database)
                                elif message == "Not Successfull":
                                    print("Something Went Wrong")
                                else:
                                    print(message)
                                dbObject.databaseClose(database)
                        time.sleep(20)
                        continue
                    except Exception as e:
                        #print str(e)
#                        dbObject.databaseClose(database)
                        fileObject.updateExceptionMessage("sasEvents{__main__}",str(e))
                
            else:
                print("Secondary Address Available: 0")
                dbObject.truncateEventListTable(database)
                time.sleep(20)
                apiObjectSecondary = sasAllAPI(2)
            
