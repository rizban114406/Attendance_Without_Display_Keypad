from sasDatabase import sasDatabase
from sasAllAPI import sasAllAPI
from sasFile import sasFile
dbObject = sasDatabase()
database = dbObject.connectDataBase()
if __name__ == '__main__':

    try:
        deviceInfo = dbObject.getAllDeviceInfo(database)
        if deviceInfo != '0':
            allEventData = dbObject.getAllEventData(database)
            deviceInfoData = {"deviceid"   : deviceInfo[1],\
                              "companyid"  : deviceInfo[3],\
                              "address"    : deviceInfo[4],\
                              "subaddress" : deviceInfo[5]}
            eventInfoData =[]
            id_count = []
            for reading in allEventData.fetchall():
                id_count.append(reading[0])
                eventInfoData.append({"eventdatetime"       : str(reading[3]),\
                                      "uniqueid"            : str(reading[1]), \
                                      "fingerorcardnumber"  : str(reading[2]),\
                                      "eventtype"           : str(reading[4]) , \
                                      "companyid"           : str(reading[5])})
            mainData = {"deviceinfo" : deviceInfoData, \
                        "eventdata"  : eventInfoData}
                
            if(allEventData.rowcount > 0):       
                apiObject = sasAllAPI()
                message = apiObject.sendEventData(mainData)
                if message == "Success":
                    for Id in id_count :
                        dbObject.deleteFromEventListTable(Id,database)
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
