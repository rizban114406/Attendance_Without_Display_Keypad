import sqlite3
from sasFile import sasFile
import time as t
fileObject = sasFile()
class sasDatabase:
    databaseName = "attendanceDB"

    def databaseCommit(self,database):
        database.commit()

    def databaseClose(self,database):
        database.close()

    def connectDataBase(self):
        database = sqlite3.connect(self.databaseName)
        return database

    ####################### All Functions Regarding Employee Information Table ###################
    def createTableEmployeeInfoTable(self,database): # Create Employee Information Table
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE IF EXISTS employeeInfoTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
#        curs.execute("DROP TABLE IF EXISTS employeeInfoTable")
#        self.databaseCommit(database)
#        t.sleep(0.5)
        curs.execute("CREATE TABLE employeeInfoTable(id           INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                     uniqueId     INTEGER,\
                                                     fingerId     INTEGER)")
        self.databaseCommit(database)

    def deleteFromEmployeeInfoTable(self,uniqueId,fingerId,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("Delete FROM employeeInfoTable \
                      WHERE uniqueId = ? and fingerId = ?",(int(uniqueId),int(fingerId),))
        self.databaseCommit(database)

    def deleteFromEmployeeInfoTableToSync(self,notListedTemplateNumber,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        for fingerId in notListedTemplateNumber:
            curs.execute("Delete FROM employeeInfoTable \
                          WHERE fingerId = ?",(int(fingerId),))
        self.databaseCommit(database)

    def truncateEmployeeInfoTable(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate employeeInfoTable")
        self.databaseCommit(database)

    def getInfoFromEmployeeInfoTable(self,database): # Get Data From Employee Info Table To Send It To The Server
        try:
            curs = database.cursor()
            curs.execute("SELECT uniqueId,fingerId From employeeInfoTable")
            receivedData = []
            data = {"data": receivedData}
            for reading in curs.fetchall():
                receivedData.append({"uniqueid"     : reading[0], \
                                     "fingernumber" : reading[1]})
            if (len(receivedData) == 0):
                receivedData.append({"uniqueid"     : 0, \
                                     "fingernumber" : 0})
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{getInfoFromEmployeeInfoTable}: ",str(e))
        return data

    def dropEmployeeInfoTable(self,database): # Drop Employee Information Table
        curs = database.cursor()
        curs.execute("Drop Table employeeInfoTable")
        self.databaseCommit(database)

    def countEmployeeInfoTable(self,database): # Drop Employee Information Table
        curs = database.cursor()
        curs.execute("Select cout(*) from employeeInfoTable")
        employeeNumber = curs.fetchone()
        return int(employeeNumber[0])

    def checkEmployeeInfoTableToDelete(self,uniqueId,fingerId,database): # 
        curs = database.cursor()
        curs.execute ("SELECT fingerId \
                       FROM employeeInfoTable \
                       WHERE uniqueId = ? and fingerId = ?", \
                      (int(uniqueId),\
                       int(fingerId),))
        employeeFingerId = curs.fetchone()
        print(employeeFingerId)
        if (employeeFingerId != None):
            return int(employeeFingerId[0])
        else:
            return 0

    def insertNewEmployee(self,\
                          uniqueId,\
                          fingerId,\
                          database):
        
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO employeeInfoTable(uniqueId,\
                                                        fingerId) VALUES (?,?)",\
                                                        (int(uniqueId),\
                                                        int(fingerId),))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertNewEmployee}: ",str(e))
            
    def getEmployeeTemplateNumber(self,database):
        curs = database.cursor()
        curs.execute ("SELECT fingerId \
                       FROM employeeInfoTable \
                       ORDER BY fingerId")
        storedTemplates = []
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if (desiredDetails != None):
            for reading in desiredDetails:
                storedTemplates.append(str(reading[0]))

        return storedTemplates
        
    def getEmployeeDetails(self,positionNumber,database):
        curs = database.cursor()
        curs.execute ("SELECT uniqueId\
                       FROM employeeInfoTable \
                       WHERE fingerId = ?",(positionNumber,))
        desiredDetails = curs.fetchone()
#        print("Desired Details of Employee: {}".format(desiredDetails))
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
    ####################### All Functions Regarding Employee Information Table ###################
    
    def createTableTempTableToSync(self,database): # Create A Temporary Table To Sync With The Server
        curs = database.cursor()
        try:      
            curs.execute("Drop Table tempTableToSync")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")        
        curs.execute("CREATE TABLE tempTableToSync(id             INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   uniqueId       INTEGER,\
                                                   fingerId       INTEGER, \
                                                   fingerMatrix   TEXT, \
                                                   desiredTask    NVARCHAR(2))")
        self.databaseCommit(database)

    def insertToTempTableToSync(self,\
                                uniqueId,\
                                fingerId,\
                                fingerMatrix,\
                                desiredTask,\
                                database): # Insert Into Temporary Table To Sync With The Server
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO tempTableToSync(uniqueId,\
                                                      fingerId,\
                                                      fingerMatrix,\
                                                      desiredTask) VALUES (?,?,?,?)",\
                                                      (int(uniqueId),\
                                                      int(fingerId),\
                                                      str(fingerMatrix),\
                                                      str(desiredTask),))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertToTempTableToSync}: ",str(e))

    def deleteFromTempTableToSync(self,uniqueId,fingerId,database): # Delete From Temporary Table After Synced
        curs = database.cursor()
        curs.execute("Delete FROM tempTableToSync \
                      WHERE uniqueId = ? and fingerId = ?",(int(uniqueId),int(fingerId),))
        self.databaseCommit(database)

    def getInfoFromTempTableToDelete(self,database): # Get Data From Temporary Table To Sync With The Server
        curs = database.cursor()
        try:     
            curs.execute("SELECT uniqueId,fingerId From tempTableToSync Where desiredTask = '3'")
            desiredDetails = curs.fetchall()
            print("Data To Delete: {}".format(desiredDetails))
            if (desiredDetails != None):
                return desiredDetails
            else:
                return []
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{getInfoFromTempTableToDelete}: ",str(e))
            return []

    def getInfoFromTempTableToEnrollOrUpdate(self,database): # Get Data From Temporary Table To Sync With The Server
        curs = database.cursor()
        try:        
            curs.execute("SELECT uniqueId,fingerId,fingerMatrix From tempTableToSync Where desiredTask = '1' Limit 500")
            desiredDetails = curs.fetchall()
            print("Data To Enroll: {}".format(desiredDetails))
            if (desiredDetails != None):
                return desiredDetails
            else:
                return []
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{getInfoFromTempTableToEnrollOrUpdate}",str(e))
            return []
    
    ######################### All Functions Regarding Event Information Table ####################
    def createTableEventListTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE eventListTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE eventListTable(uniqueId      INTEGER,\
                                                  fingerOrCard  INTEGER,\
                                                  eventDateTime DATETIME,\
                                                  eventType     NVARCHAR(1))")
        self.databaseCommit(database)

    def truncateEventListTable(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("DELETE FROM eventListTable")
        self.databaseCommit(database)
        
    def deleteFromEventListTable(self,eventDateTime,database):
        try:
            curs = database.cursor()
            curs.execute("Delete FROM eventListTable WHERE eventDateTime = ?",(eventDateTime,))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{deleteFromEventListTable}: ",str(e))
    
    def getAllEventData(self,database):
        curs = database.cursor()
        curs.execute("SELECT * From eventListTable limit 1000")
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if desiredDetails != None:
            return desiredDetails
        return []

    def insertEventTime(self,\
                        uniqueId,\
                        fingerOrCard,\
                        eventDateTime,\
                        eventType,\
                        database):
        curs = database.cursor()
        curs.execute("INSERT INTO eventListTable(uniqueId,\
                                                 fingerOrCard,\
                                                 eventDateTime,\
                                                 eventType) VALUES (?,?,?,?)",\
                                                (int(uniqueId),\
                                                 int(fingerOrCard),\
                                                 eventDateTime,\
                                                 eventType,))
        self.databaseCommit(database)
#    ######################### All Functions Regarding Event Information Table ####################

    ####################### All Functions Regarding Employee Card Info ###################
    def createTableEmployeeCardInfo(self,database): # Create Employee Card Info Table
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE employeeCardInfo")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE employeeCardInfo(id        INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   uniqueId   INTEGER,\
                                                   cardNumber INTEGER)")
        self.databaseCommit(database)

    def deleteFromEmployeeCardInfoTable(self,uniqueId,cardNumber,database): # Delete From Employee Card Info Table After Deleting Employee
        curs = database.cursor()
        if (cardNumber == 0):
            curs.execute("Delete FROM employeeCardInfo \
                          WHERE uniqueId = ?",(int(uniqueId),))
        else:
            curs.execute("Delete FROM employeeCardInfo \
                          WHERE uniqueId = ? and cardNumber = ?", \
                         (int(uniqueId),int(cardNumber),))
            
        self.databaseCommit(database)

    def truncateEmployeeCardInfoTable(self,database): # Delete From Employee Card Info Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate employeeCardInfo")
        self.databaseCommit(database)

    def getInfoFromEmployeeCardInfoTable(self,database): # Get Data From Employee Card Info Table To Send It To The Server
        curs = database.cursor()
        curs.execute("Select uniqueId, cardNumber \
                      From employeeCardInfo")
        receivedData = []
        data = {"data" : receivedData}
        for reading in curs.fetchall():
            receivedData.append({"uniqueid" : reading[0], "cardnumber" : reading[1]})
        
        if (len(receivedData) == 0):
            receivedData.append({"uniqueid" : 0, "cardnumber" : 0})
        return data

    def dropEmployeeCardInfoTable(self,database): # Drop Employee Card Info Table
        curs = database.cursor()
        curs.execute("Drop Table employeeCardInfo")
        self.databaseCommit(database)

    def insertIntoEmployeeCardInfoTable(self,uniqueId,\
                                        cardNumber,\
                                        database):
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO employeeCardInfo(uniqueId,\
                                                       cardNumber) VALUES (?,?)",\
                                                       (int(uniqueId),\
                                                       int(cardNumber)))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertIntoEmployeeCardInfoTable}",str(e))

    def getEmployeeDetailsFromCard(self,cardNumber,database):
        curs = database.cursor()
        curs.execute ("SELECT uniqueId\
                       FROM employeeCardInfo \
                       WHERE cardNumber = ?",(int(cardNumber),))
        desiredDetails = curs.fetchone()
#        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
    ####################### All Functions Regarding Employee Card Info Table ###################

    ####################### All Functions Regarding Configuration Info Table ###################

    def createTableConfigInfoTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE configurationTable")
            self.databaseCommit(database)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE configurationTable(id             INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                     baseUrl         TEXT,\
                                                     subUrl          TEXT,\
                                                     updateRequired  NVARCHAR(1),\
                                                     serverUpdated   NVARCHAR(1))")
        self.databaseCommit(database)
        
    def getAllConfigurationDetails(self,locationType,database):
        curs = database.cursor()
        curs.execute ("SELECT baseUrl,subUrl FROM configurationTable WHERE id = ?",(locationType,)) #1=primary, 2=seondary
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return ['','']

    def insertIntoConfigurationTable(self,baseUrl,\
                                        subUrl,\
                                        database):
        if (baseUrl is None):
            baseUrl = ""
        if (subUrl is None):
            subUrl = ""
        curs = database.cursor()
        curs.execute("INSERT INTO configurationTable(baseUrl,\
                                                     subUrl,\
                                                     updateRequired,\
                                                     serverUpdated) VALUES (?,?,'1','1')",\
                                                    (str(baseUrl),\
                                                     str(subUrl),))
        self.databaseCommit(database)
        
    def checkAddressUpdateRequired(self, locationType, database):
        curs = database.cursor()
        curs.execute ("SELECT updateRequired FROM configurationTable WHERE id = ? and updateRequired = '0'",(locationType,)) #1=primary, 2=seondary
        desiredDetails = curs.fetchone()
        if (desiredDetails != None):
            return 1
        else:
            return 0
        
    def checkServerUpdateStatus(self, locationType, database):
        curs = database.cursor()
        curs.execute ("SELECT serverUpdated FROM configurationTable WHERE id = ? and serverUpdated = '0'",(locationType,)) #1=primary, 2=seondary
        desiredDetails = curs.fetchone()
        if (desiredDetails != None):
            return 1
        else:
            return 0
        
    def checkSecondaryAddressAvailable(self, database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM configurationTable WHERE id = 2") #1=primary, 2=seondary
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return 1
        else:
            return 0
        
    def updateConfigurationTable(self, baseURL, subURL, database):
        curs = database.cursor()
        if (baseURL is None):
            baseURL = ""
        if (subURL is None):
            subURL = ""
        curs.execute ("UPDATE configurationTable SET baseUrl = ?, \
                                                     subUrl = ?, \
                                                     updateRequired = '1',\
                                                     serverUpdated = '1'\
                                                     WHERE id = 2",\
                                                    (baseURL,\
                                                     subURL,))
        self.databaseCommit(database)
    
    def setServerUpdatedStatus(self,locationType,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET serverUpdated = '1' \
                                                     WHERE id = ?",\
                                                    (locationType,))
        self.databaseCommit(database)
        
    def resetServerUpdatedStatus(self,locationType,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET serverUpdated = '0' \
                                                     WHERE id = ?",\
                                                    (locationType,))
        self.databaseCommit(database)
        
    def setUpdatedRequiredStatus(self,locationType,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET updateRequired = '1' \
                                                     WHERE id = ?",\
                                                    (locationType,))
        self.databaseCommit(database)
        
    def resetUpdatedRequiredStatus(self,locationType,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET updateRequired = '0' \
                                                     WHERE id = ?",\
                                                    (locationType,))
        self.databaseCommit(database)
    
    ####################### All Functions Regarding Configuration Info Table ###################

    ####################### All Functions Regarding Device Info Table ###################

    def createTableDeviceInfoTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE deviceInfoTable")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE deviceInfoTable(id              INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   hardwareId      TEXT,\
                                                   deviceId        INTEGER,\
                                                   deviceOSVersion DOUBLE,\
                                                   deviceName      TEXT,\
                                                   address         TEXT,\
                                                   subAddress      TEXT,\
                                                   ipAddress       TEXT,\
                                                   companyId       INTEGER)")
        self.databaseCommit(database)
        
    def insertIntoDeviceInfoTable(self,hardwareId,\
                                  deviceId,\
                                  osVersion,\
                                  ipAddress,\
                                  database): # Insert Device Info into Database
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO deviceInfoTable(hardwareId,\
                                                      deviceId,\
                                                      deviceOSVersion,\
                                                      deviceName,\
                                                      address,\
                                                      subAddress,\
                                                      ipAddress,\
                                                      companyId) VALUES (?,?,?,'','','',?,0)",\
                                                      (str(hardwareId),\
                                                       int(deviceId),\
                                                       float(osVersion),\
                                                       str(ipAddress),))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertIntoDeviceInfoTable}",str(e))
            
    def getOSVersion(self,database):
        curs = database.cursor()
        curs.execute ("SELECT deviceOSVersion FROM deviceInfoTable WHERE id = 1")
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return float(desiredDetails[0])
        else:
            return '0'
        
    def countDeviceInfoTable(self,database): # Drop Employee Information Table
        curs = database.cursor()
        curs.execute("Select count(*) from deviceInfoTable")
        rowNum = curs.fetchone()
        return int(rowNum[0])

    def getDeviceId(self,database): # Get Device Id From Database
        curs = database.cursor()
        curs.execute ("SELECT deviceId FROM deviceInfoTable WHERE id = 1")
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return int(desiredDetails[0])
        else:
            return 0
    
    def getAllDeviceInfo(self,database): # Get All Device Info from Database
        curs = database.cursor()
        curs.execute ("SELECT * FROM deviceInfoTable WHERE id = 1")
        desiredDetails = curs.fetchone()
        print("Event Data To Be Sent: {}".format(desiredDetails))
        if (len(desiredDetails) > 0):
            return desiredDetails
        else:
            return '0'
    
    def updateDeviceInfoTable(self,deviceName,\
                              address,\
                              subAddress,\
                              ipAddress,\
                              companyId,\
                              deviceOSVersion,\
                              database):
        curs = database.cursor()
        if (deviceName is None):
            deviceName = ""
        if (address is None):
            address = ""
        if (subAddress is None):
            subAddress = ""
        if (companyId is None):
            companyId = ""
        try:
            curs.execute ("UPDATE deviceInfoTable SET deviceName = ?, \
                                                      address = ?, \
                                                      subAddress = ?, \
                                                      ipAddress = ?, \
                                                      companyId = ?, \
                                                      deviceOSVersion = ?\
                                                      WHERE id = 1",\
                                                      (str(deviceName),\
                                                       str(address),\
                                                       str(subAddress),\
                                                       str(ipAddress),\
                                                       (companyId),\
                                                       float(deviceOSVersion),))
            self.databaseCommit(database)
            return 1
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{updateDeviceInfoTable}",str(e))
            return 0
        
    ####################### All Functions Regarding Device Info Table ###################
     
    ####################### All Functions Regarding Wifi Networks Info Table ###################
    
    def createTableWifiSettings(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE wifiSettings")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE wifiSettings(id        INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                ssid      TEXT,\
                                                password  TEXT,\
                                                priority  DOUBLE)")
        self.databaseCommit(database)
        
    def insertIntoWifiSettingsTable(self,ssid,\
                                    password,\
                                    priority,\
                                    database):
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO wifiSettings(ssid,\
                                                   password,\
                                                   priority) VALUES (?,?,?)",\
                                                   (str(ssid),\
                                                    str(password),\
                                                    float(priority),))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertIntoWifiSettingsTable}: ",str(e))
        
    def getWifiConfigs(self,database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM wifiSettings")
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
        
    def countWifiConfigs(self,database):
        curs = database.cursor()
        curs.execute ("SELECT count(*) FROM wifiSettings")
        rowNum = curs.fetchone()
        return int(rowNum[0])
        
    def checkWifiConfigsChange(self, ssid, password, priority, database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM wifiSettings WHERE ssid = ? and \
                                                        password = ? and \
                                                        priority = ?",\
                                                        (str(ssid),\
                                                         str(password),\
                                                         float(priority),))
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if (len(desiredDetails) > 0):
            return 1
        else:
            return 0
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
