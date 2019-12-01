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
            date_count = []
            for reading in allEventData:
                date_count.append(reading[2])
                eventInfoData.append({"eventdatetime"       : str(reading[2]),\
                                      "uniqueid"            : str(reading[0]), \
                                      "fingerorcardnumber"  : str(reading[1]),\
                                      "eventtype"           : str(reading[3]) , \
                                      "companyid"           : str(reading[4])})
            mainData = {"deviceinfo" : deviceInfoData, \
                        "eventdata"  : eventInfoData}
                
            if(len(allEventData) > 0):       
                apiObject = sasAllAPI(2)
                message = apiObject.sendEventData(mainData)
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
    except Exception as e:
        #print str(e)
        fileObject = sasFile()
        dbObject.databaseClose(database)
        fileObject.updateExceptionMessage("sasEvents{__main__}",str(e))
