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
                                                     fingerId     INTEGER, \
                                                     companyId    INTEGER)")
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

#    def checkEmployeeInfoTable(self,employee,companyId,database): # 
#        curs = database.cursor()
#        curs.execute ("SELECT fingerId \
#                       FROM employeeInfoTable \
#                       WHERE employee = ? and companyId = ?", \
#                      (str(employee),int(companyId),))
#        desiredDetails = curs.fetchone()
#        print(desiredDetails)
#        if (desiredDetails != None):
#            return "Registered"
#        else:
#            return "Not Registered"

    def insertNewEmployee(self,\
                          uniqueId,\
                          fingerId,\
                          companyId,\
                          database):
        
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO employeeInfoTable(uniqueId,\
                                                        fingerId,\
                                                        companyId) VALUES (?,?,?)",\
                                                        (int(uniqueId),\
                                                        int(fingerId),\
                                                        int(companyId),))
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
        curs.execute ("SELECT uniqueId,companyId \
                       FROM employeeInfoTable \
                       WHERE fingerId = ?",(positionNumber,))
        desiredDetails = curs.fetchone()
        print(desiredDetails)
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
#        curs.execute("DROP TABLE IF EXISTS tempTableToSync")
#        self.databaseCommit(database)
#        t.sleep(0.5)        
        curs.execute("CREATE TABLE tempTableToSync(id             INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   uniqueId       INTEGER,\
                                                   fingerId       INTEGER, \
                                                   fingerMatrix   TEXT, \
                                                   desiredTask    NVARCHAR(2), \
                                                   companyId      INTEGER)")
        self.databaseCommit(database)

    def insertToTempTableToSync(self,\
                                uniqueId,\
                                fingerId,\
                                fingerMatrix,\
                                desiredTask,\
                                companyId, \
                                database): # Insert Into Temporary Table To Sync With The Server
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO tempTableToSync(uniqueId,\
                                                      fingerId,\
                                                      fingerMatrix,\
                                                      desiredTask,\
                                                      companyId) VALUES (?,?,?,?,?)",\
                                                      (int(uniqueId),\
                                                      int(fingerId),\
                                                      str(fingerMatrix),\
                                                      str(desiredTask),\
                                                      int(companyId),))
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
            print(desiredDetails)
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
            curs.execute("SELECT * From tempTableToSync Where desiredTask = '1' Limit 200")
            desiredDetails = curs.fetchall()
            print(desiredDetails)
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
#        curs.execute("DROP TABLE IF EXISTS eventListTable")
#        self.databaseCommit(database)
#        t.sleep(0.5)
        curs.execute("CREATE TABLE eventListTable(uniqueId      INTEGER,\
                                                  fingerOrCard  INTEGER,\
                                                  eventDateTime DATETIME,\
                                                  eventType     NVARCHAR(1),\
                                                  companyId     INTEGER)")
        self.databaseCommit(database)

    def truncateEventListTable(self,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("truncate eventListTable")
        self.databaseCommit(database)
        
    def deleteFromEventListTable(self,eventDateTime,database):
        try:
            curs = database.cursor()
            curs.execute("Delete FROM eventListTable WHERE eventDateTime = ?",(eventDateTime,))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{deleteFromEventListTable}: ",str(e))

#    def getAllEventData(self,startTime,database):
#        curs = database.cursor()
#        curs.execute("SELECT * From eventListTable WHERE startTime = ?",(startTime,))
#        desiredDetails = curs.fetchall()
#        print(desiredDetails)
#        if desiredDetails != None:
#            return desiredDetails
#        return []
    
    def getAllEventData(self,database):
        curs = database.cursor()
        curs.execute("SELECT * From eventListTable limit 1000")
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if desiredDetails != None:
            return desiredDetails
        return []
    
#    def checkEventDataStartTime(self,startTime,database):
#        curs = database.cursor()
#        curs.execute("SELECT * From eventListTable WHERE startTime = ?",(startTime,))
#        desiredDetails = curs.fetchone()
#        print(desiredDetails)
#        if (desiredDetails != None):
#            return 1
#        return 0

    def insertEventTime(self,\
                        uniqueId,\
                        fingerOrCard,\
                        EventDateTime,\
                        EventType,\
                        companyId,\
                        database):
        curs = database.cursor()
        curs.execute("INSERT INTO eventListTable(uniqueId,\
                                                 fingerOrCard,\
                                                 EventDateTime,\
                                                 EventType,\
                                                 companyID) VALUES (?,?,?,?,?)",\
                                                (int(uniqueId),\
                                                 int(fingerOrCard),\
                                                 EventDateTime,\
                                                 EventType,\
                                                 int(companyId),))
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
#        curs.execute("DROP TABLE IF EXISTS employeeCardInfo")
#        self.databaseCommit(database)
#        t.sleep(0.5)
        curs.execute("CREATE TABLE employeeCardInfo(id        INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   uniqueId   INTEGER,\
                                                   cardNumber INTEGER, \
                                                   companyId  INTEGER)")
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

#    def checkEmployeeCardInfoTableToDelete(self,uniqueId,companyId,database): # 
#        curs = database.cursor()
#        try:
#            curs.execute ("SELECT cardNumber \
#                           FROM employeeCardInfo \
#                           WHERE uniqueId = ? and companyId = ?",(int(uniqueId),int(companyId),))
#            
#            desiredDetails = curs.fetchone()
#            if (desiredDetails != None):
#                self.deleteFromEmployeeCardInfoTable(uniqueId,0,database)
#                self.databaseCommit(database)
#            return 1
#        except Exception as e:
#            #print str(e)
#            fileObject.updateExceptionMessage("sasDatabase{checkEmployeeCardInfoTableToDelete}",str(e))
#            return 0

    def insertIntoEmployeeCardInfoTable(self,uniqueId,\
                                        cardNumber,\
                                        companyId,\
                                        database):
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO employeeCardInfo(uniqueId,\
                                                       cardNumber,\
                                                       companyId) VALUES (?,?,?)",\
                                                       (int(uniqueId),\
                                                       int(cardNumber),\
                                                       int(companyId),))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{insertIntoEmployeeCardInfoTable}",str(e))

    def getEmployeeDetailsFromCard(self,cardNumber,database):
        curs = database.cursor()
        curs.execute ("SELECT uniqueId,companyId \
                       FROM employeeCardInfo \
                       WHERE cardNumber = ?",(int(cardNumber),))
        self.databaseCommit(database)
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
    ####################### All Functions Regarding Employee Card Info Table ###################

#    ####################### All Functions Regarding Company Info Table ###################
#    def createTableCompanyListTable(self,database):
#        curs = database.cursor()
#        try:      
#            curs.execute("DROP TABLE companyListTable")
#            self.databaseCommit(database)
#            t.sleep(1)
#        except Exception:
#            print("Does not Exists")
##        curs.execute("DROP TABLE IF EXISTS companyListTable")
##        self.databaseCommit(database)
##        t.sleep(.5)
#        curs.execute("CREATE TABLE companyListTable(id      INTEGER PRIMARY KEY AUTOINCREMENT,\
#                                                  companyId INTEGER,\
#                                                  shortName TEXT)")
#        self.databaseCommit(database)
#
#    def getAllCompanyList(self,database):
#        curs = database.cursor()
#        curs.execute("Select companyId,shortName From companyListTable")
#        self.databaseCommit(database)
#        return curs
#
#    def checkCompanyListTable(self,companyId,database): 
#        curs = database.cursor()
#        curs.execute ("SELECT companyName FROM companyListTable WHERE companyId = ?",(int(companyId),))
#        desiredDetails = curs.fetchone()
#        print(desiredDetails)
#        if (desiredDetails != None):
#            return '1'
#        else:
#            return '0'
#
#    def insertIntoCompanyListTable(self,companyId,\
#                                        shortName,\
#                                        database):
#        curs = database.cursor()
#        curs.execute("INSERT INTO companyListTable(companyId,\
#                                                   shortName) VALUES (?,?)",\
#                                                   (int(companyId),\
#                                                   str(shortName)))
#        self.databaseCommit(database)
#    ####################### All Functions Regarding Company Info Table ###################

    ####################### All Functions Regarding Configuration Info Table ###################

    def createTableConfigInfoTable(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE configurationTable")
            self.databaseCommit(database)
        except Exception:
            print("Does not Exists")
#        curs.execute("DROP TABLE IF EXISTS configurationTable")
#        self.databaseCommit(database)
#        t.sleep(.5)
        curs.execute("CREATE TABLE configurationTable(id             INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                     baseUrl         TEXT,\
                                                     subUrl          TEXT,\
                                                     updateRequired  NVARCHAR(1),\
                                                     serverUpdated   NVARCHAR(1))")
        self.databaseCommit(database)
        
    def getAllConfigurationDetails(self,locationType,database):
        curs = database.cursor()
        curs.execute ("SELECT baseUrl,subUrl, FROM configurationTable WHERE id = ?",(locationType,)) #1=primary, 2=seondary
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return ['0','0']

    def insertIntoConfigurationTable(self,baseUrl,\
                                        subUrl,\
                                        database):
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
        
        
        
        

    def updateOSVersion(self,deviceOSVersion,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET deviceOSVersion = ? \
                                                     WHERE id = 1",\
                                                    (deviceOSVersion))
        self.databaseCommit(database)
    def updateBaseUrl(self,baseUrl,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET baseUrl = ? \
                                                     WHERE id = 1",\
                                                    (baseUrl))
        self.databaseCommit(database)
    def updateSubUrl(self,subUrl,database):
        curs = database.cursor()
        curs.execute ("UPDATE configurationTable SET subUrl = ? \
                                                     WHERE id = 1",\
                                                    (subUrl))
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
#        curs.execute("DROP TABLE IF EXISTS deviceInfoTable")
#        self.databaseCommit(database)
#        t.sleep(.5)
        curs.execute("CREATE TABLE deviceInfoTable(id              INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                   hardwareId      TEXT,\
                                                   deviceId        INTEGER,\
                                                   deviceOSVersion DOUBLE,\
                                                   deviceName      TEXT,\
                                                   address         TEXT,\
                                                   subAddress      TEXT,\
                                                   ipAddress       TEXT,\
                                                   companyId       NVARCHAR(3))")
        self.databaseCommit(database)
        
    def insertIntoDeviceInfoTable(self,hardwareId,\
                                  deviceId,\
                                  osVersion,\
                                  ipAddress,\
                                  database):
        curs = database.cursor()
        try:
            curs.execute("INSERT INTO deviceInfoTable(hardwareId,\
                                                      deviceId,\
                                                      deviceOSVersion,\
                                                      deviceName,\
                                                      address,\
                                                      subAddress,\
                                                      ipAddress,\
                                                      companyId) VALUES (?,?,?,'','','',?,'')",\
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
        curs.execute("Select cout(*) from deviceInfoTable")
        rowNum = curs.fetchone()
        return int(rowNum[0])

    def getDeviceId(self,database):
        curs = database.cursor()
        curs.execute ("SELECT deviceId FROM deviceInfoTable WHERE id = 1")
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return int(desiredDetails[0])
        else:
            return 0
        
        
        
        
        

    def getAllDeviceInfo(self,database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM deviceInfoTable WHERE id = 1")
        desiredDetails = curs.fetchone()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'

    def updateIPAddress(self,ipAddress,database):
        curs = database.cursor()
        curs.execute ("UPDATE deviceInfoTable SET ipAddress = ? \
                                                  WHERE id = 1",\
                                                  (ipAddress))
        self.databaseCommit(database)

    def updateDeviceInfoTable(self,deviceInfo,\
                              ipAddress,\
                              database):
        curs = database.cursor()
        if (deviceInfo['company_id'] is None):
            deviceInfo['company_id'] = ""
        if (deviceInfo['office_address'] is None):
            deviceInfo['office_address'] = ""
        if (deviceInfo['office_sub_address'] is None):
            deviceInfo['office_sub_address'] = ""
        try:
            curs.execute ("UPDATE deviceInfoTable SET companyId = ?, \
                                                  address = ?, \
                                                  subAddress = ?, \
                                                  ipAddress = ? \
                                                  WHERE id = 1",\
                                                  (str(deviceInfo['company_id']),\
                                                   str(deviceInfo['office_address']),\
                                                   str(deviceInfo['office_sub_address']),\
                                                   str(ipAddress)))
            self.databaseCommit(database)
        except Exception as e:
            fileObject.updateExceptionMessage("sasDatabase{updateDeviceInfoTable}",str(e))
        
    ####################### All Functions Regarding Device Info Table ###################
    def createTableTimeConfig(self,database):
        curs = database.cursor()
        try:      
            curs.execute("DROP TABLE timeConfig")
            self.databaseCommit(database)
            t.sleep(1)
        except Exception:
            print("Does not Exists")
        curs.execute("CREATE TABLE timeConfig(startTime   DATETIME,\
                                              restartTime DATETIME,\
                                              duration    TEXT)")
        self.databaseCommit(database)
    
    def insertIntoTimeConfig(self, startTime, database):
        curs = database.cursor()
        curs.execute("INSERT INTO timeConfig(startTime,\
                                             restartTime,\
                                             duration) VALUES (?,"","")",\
                                             (startTime))
        self.databaseCommit(database)
        
    def updateRestartTimeConfig(self, startTime, restartTime, database):
        curs = database.cursor()
        curs.execute ("UPDATE timeConfig SET restartTime = ? \
                       WHERE startTime = ?",(startTime, restartTime))
        self.databaseCommit(database)
    
    def updateDurationTimeConfig(self, startTime, duration, database):
        curs = database.cursor()
        curs.execute ("UPDATE timeConfig SET duration = ? \
                       WHERE startTime = ?",(str(duration), startTime))
        self.databaseCommit(database)
    
    def getRowWithNoDurationTimeConfig(self,database):
        curs = database.cursor()
        curs.execute ("SELECT startTime, restartTime FROM timeConfig WHERE duration = """)
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
    
    def getDataTimeConfig(self,database):
        curs = database.cursor()
        curs.execute ("SELECT * FROM timeConfig WHERE duration != """)
        desiredDetails = curs.fetchall()
        print(desiredDetails)
        if (desiredDetails != None):
            return desiredDetails
        else:
            return '0'
    
    def deleteFromTimeConfig(self,startTime,database): # Delete From Employee Infromation Table After Deleting Employee
        curs = database.cursor()
        curs.execute("Delete FROM timeConfig \
                      WHERE startTime = ?",(startTime))
        self.databaseCommit(database)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
