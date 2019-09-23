import time as t
from sasDatabase import sasDatabase
from sasFile import sasFile
from sasAllAPI import sasAllAPI
fileObject = sasFile()
dbObject = sasDatabase()
database = dbObject.connectDataBase()
apiObject = sasAllAPI()
def getFingerPrintInformation(deviceId):
    try:
        receivedData = dbObject.getInfoFromEmployeeInfoTable(database)
#        print("Existig Data {}".format(receivedData))
        receivedDataSync = apiObject.getDataToSync(receivedData,deviceId)
        dbObject.createTableTempTableToSync(database)
        if(receivedDataSync == "Some Thing Is Wrong"):
            return "API Error"
        elif(receivedDataSync == "Server Error"):
            return "Server Down"
        else:
            if(len(receivedDataSync['data']) > 0 or len(receivedDataSync['delete_request_enrollment']) > 0):
                if len(receivedDataSync['data']) > 0:
                    for data in receivedDataSync['data']:
                        dbObject.insertToTempTableToSync(data['employeeid'],\
                                                         data['uniqueid'],\
                                                         data['firstname'],\
                                                         data['fingernumber'],\
                                                         data['matrix'],\
                                                         '1',\
                                                         data['companyid'],\
                                                         database)
                if len(receivedDataSync['delete_request_enrollment']) > 0:
                    for data in receivedDataSync['delete_request_enrollment']:
                        dbObject.insertToTempTableToSync("N",\
                                                         data['uniqueid'],\
                                                         "N",\
                                                         data['fingernumber'],\
                                                         "N",\
                                                         '3',\
                                                         '0',\
                                                         database)
                return "Not Synced"
            else:
                return "Synced"
    except Exception as e:
        fileObject.updateExceptionMessage("sasSyncDevice{getFingerPrintInformation}",str(e))
        return "Error"
        
def getRFCardInformation(deviceId):
    try:
        receivedData = dbObject.getInfoFromEmployeeCardInfoTable(database)
        receivedDataSync = apiObject.getCardDataToSync(receivedData,deviceId)
        if(receivedDataSync == "Some Thing Is Wrong"):
            return "API Error"
        elif(receivedDataSync == "Server Error"):
            return "Server Down"
        else:
            if(len(receivedDataSync['data']) > 0 or len(receivedDataSync['delete_request_enrollment']) > 0):
                if len(receivedDataSync['data']) > 0:
                    for data in receivedDataSync['data']:
                        # print (data['uniqueid']," ",data['companyid'])
                        dbObject.insertIntoEmployeeCardInfoTable(data['employeeid'],\
                                                                 data['uniqueid'],\
                                                                 data['firstname'],\
                                                                 data['cardnumber'],\
                                                                 data['companyid'],\
                                                                 database)
                if len(receivedDataSync['delete_request_enrollment']) > 0:
                    for data in receivedDataSync['delete_request_enrollment']:
                        dbObject.deleteFromEmployeeCardInfoTable(data['uniqueid'],data['cardnumber'],database)
                return "Synced"
            else:
                return "Synced"
    except Exception as e:
        fileObject.updateExceptionMessage("sasSyncDevice{getRFCardInformation}",str(e))
        return "Error"
               
def checkEmployeeInfoTable():
    templatesStoredSensor = fileObject.readStoredIndex()
    templateStoredDatabase = dbObject.getEmployeeTemplateNumber(database)
    notListedTemplateNumber = list(set(templateStoredDatabase) - set(templatesStoredSensor))
    dbObject.deleteFromEmployeeInfoTableToSync(notListedTemplateNumber,database)
    
if __name__ == '__main__':
    try:
        deviceId = dbObject.getDeviceId(database)
        if deviceId != 0:
            fingerStat = "Not Synced"
            cardStat = "Not Synced"  
            while 1:
                checkEmployeeInfoTable()
                if (fingerStat == "Not Synced"):
                    fingerStat = getFingerPrintInformation(deviceId)
                if (cardStat == "Not Synced"):
                    cardStat = getRFCardInformation(deviceId)
                    
                if fingerStat == "Not Synced":
                    while 1:
                        task = fileObject.readDesiredTask()
                        if task == '1':
                            import os
                            os.system('sudo pkill -f sasMain.py')
                            fingerStat = "Synced"
                            t.sleep(1)
                            break
                               
                if fingerStat == "Synced" and cardStat == "Synced":
                    print("Device Is Fully Synced with the Server")
                    break
                t.sleep(5)
            dbObject.databaseClose(database)
    except Exception as e:
        dbObject.databaseClose(database)
        fileObject.updateExceptionMessage("attendanceGetFingerInfo{__main__}",str(e))
