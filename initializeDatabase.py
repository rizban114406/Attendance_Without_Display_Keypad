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
    dbObject.createTableTimeConfig(database)
    dbObject.createTableDeviceInfoTable(database)
    dbObject.createTableConfigInfoTable(database)
    dbObject.insertIntoConfigurationTable("1","sas.aqualinkbd.com","/sas-test/api/",database)
    url = "http://" + "sas.aqualinkbd.com" + "/sas-test/api/" + "server_heartbit"
    fileObject.updateHearBitURL(url)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized From Main")
except Exception as e:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableCompanyListTable(database)
    dbObject.createTableTimeConfig(database)
    dbObject.createTableDeviceInfoTable(database)
    dbObject.createTableConfigInfoTable(database)
    dbObject.insertIntoConfigurationTable("1","sas.aqualinkbd.com","/sas-test/api/",database)
    url = "http://" + "sas.aqualinkbd.com" + "/sas-test/api/" + "server_heartbit"
    fileObject.updateHearBitURL(url)
    fileObject.updateConfigUpdateStatus('0')
    dbObject.databaseClose(database)
    print ("Device Initialized")
    exit(1)
