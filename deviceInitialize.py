from sasDatabase import sasDatabase
dbObject = sasDatabase()
database = dbObject.connectDataBase()
#### Tries to delete the template of the finger
try:
    dbObject.createTableEmployeeInfoTable(database)
    dbObject.createTableEventListTable(database)
    dbObject.createTableEmployeeCardInfo(database)
    dbObject.createTableWifiSettings(database)
    dbObject.createTableDeviceInfoTable(database)
    dbObject.createTableConfigInfoTable(database)
    dbObject.insertIntoConfigurationTable("sas.aqualinkbd.com","/sas-test/api/",database)
    dbObject.databaseClose(database)
    print ("Device Initialized From Main")
except Exception as e:
    print ("Device Not Initialized")
    exit(1)
