from sasDatabase import sasDatabase
from sasFile import sasFile
dbObject = sasDatabase()
database = dbObject.connectDataBase()
fileObject = sasFile()


#### Tries to delete the template of the finger
try:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableCompanyListTable(database)
#    dbObject.createTableTempTableToSync(database)
    dbObject.createTableDeviceInfoTable(database)
    dbObject.createTableConfigInfoTable(database)
    dbObject.insertIntoConfigurationTable("1","103.108.147.49","/SAS-test/public/api/",database)
    url = "http://" + "103.108.147.49" + "/SAS-test/public/api/" + "server_heartbit"
    fileObject.updateHearBitURL(url)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized")
except Exception as e:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableCompanyListTable(database)
#    dbObject.createTableTempTableToSync(database)
    dbObject.createTableDeviceInfoTable(database)
    dbObject.createTableConfigInfoTable(database)
    dbObject.insertIntoConfigurationTable("1","103.108.147.49","/SAS-test/public/api/",database)
    url = "http://" + "103.108.147.49" + "/SAS-test/public/api/" + "server_heartbit"
    fileObject.updateHearBitURL(url)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized")
    exit(1)
