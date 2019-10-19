# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 15:38:19 2019

@author: Rizban Hussain
"""
import os
import datetime
import time as t
import threading
import serial

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

from pyfingerprint.pyfingerprint import PyFingerprint

from sasFile import sasFile
fileObject = sasFile()

def getDeviceId():
    try:
        from sasDatabase import sasDatabase
        dbObject = sasDatabase()
        database = dbObject.connectDataBase()
        deviceId = dbObject.getDeviceId(database)
        dbObject.databaseClose(database)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{Connect To Database}: ",str(e))
        os.system('sudo pkill -f sasMain.py')
    return deviceId
    
desiredTask = '1'
confStatus = '0'
lock = threading.Lock()
synclock = threading.Lock()
startTime = fileObject.readStartTime()

from sasAllAPI import sasAllAPI
apiObject = sasAllAPI()
REQUESTTIMEOUT = 5
ENROLLMENTTIMEOUT = 150
def configureFingerPrint():
    while True:
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
            if ( f.verifyPassword() == False ):
                raise ValueError('The given fingerprint sensor password is wrong!')
                t.sleep(2)
            else:
                break
        except Exception as e:
            #lcdPrint.printExceptionMessage(str(e))
            fileObject.updateExceptionMessage("sasMain{configureFingerPrint}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
    return f

def checkCurrentDateTime():
    nowTime = datetime.datetime.now()
    currentTime = nowTime.strftime('%H:%M:%S')
    currentDateTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
    return (currentDateTime,currentTime)

def createNewTemplateToSync(f,employeeInfo,dbObject,database):
    x = str(employeeInfo['matrix']).split('-')
    characteristics = []
    for i in range(0,len(x)-1):
        characteristics.append(int(x[i]))
    f.uploadCharacteristics(0x01,characteristics)
    f.storeTemplate(int(employeeInfo[4]),0x01)
    import re
    sp = re.split(' |-|',str(employeeInfo['employeeid']))
    if(len(sp) == 2):
        employee = sp[1]
    else:
        employee = sp[0]

    dbObject.insertNewEmployee(employeeInfo['employeeid'], \
                               employeeInfo['uniqueid'], \
                               employeeInfo['firstname'], \
                               employeeInfo['fingernumber'], \
                               employeeInfo['matrix'], \
                               employeeInfo['companyid'], \
                               employee, \
                               database)
        

def updateListOfUsedTemplates(f):
#    lock.acquire()
    tableIndex1 = f.getTemplateIndex(0)
    tableIndex2 = f.getTemplateIndex(1)
    tableIndex3 = f.getTemplateIndex(2)
    tableIndex4 = f.getTemplateIndex(3)
#    lock.release()
    index = []
    for i in range(0, len(tableIndex1)):
        index.append(tableIndex1[i])
    for i in range(0, len(tableIndex2)):
        index.append(tableIndex2[i])
    for i in range(0, len(tableIndex3)):
        index.append(tableIndex3[i])
    for i in range(0, len(tableIndex4)):
        index.append(tableIndex4[i])
    storedIndex = ""
    for i in range(0, len(index)):
        if (str(index[i]) == "True"):
            storedIndex = storedIndex + str(i) + '-'
    fileObject.updateStoredIndex(storedIndex)
    
def checkEmployeeInfoTable(dbObject,database):
    try:    
        templatesStoredSensor = fileObject.readStoredIndex()
        templateStoredDatabase = dbObject.getEmployeeTemplateNumber(database)
        notListedTemplateNumber = list(set(templateStoredDatabase) - set(templatesStoredSensor))
        dbObject.deleteFromEmployeeInfoTableToSync(notListedTemplateNumber,database)
#        notListedTemplateNumber = list(set(templatesStoredSensor) - set(templateStoredDatabase))
#        for deleteId in notListedTemplateNumber:
#            if deleteId != '':
#                lock.acquire()
#                f.deleteTemplate(int(deleteId))
#                lock.release()
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{checkEmployeeInfoTable}: ",str(e))
        
def syncUsersToSensor(f,dbObject,database):
    try:
        getDataToDelete = dbObject.getInfoFromTempTableToDelete(database)
        getDataToSync = dbObject.getInfoFromTempTableToEnrollOrUpdate(database)
        if (getDataToDelete != "Synced" or getDataToSync != "Synced"):
            for reading in getDataToDelete:
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[0],reading[1],database)
                f.deleteTemplate(prevId)
                dbObject.deleteFromEmployeeInfoTable(reading[0],reading[1],database)
                dbObject.deleteFromTempTableToSync(reading[0],reading[1],database)
                t.sleep(.3)
            for reading in getDataToSync:
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[2],reading[4],database)
                if prevId > 0:
                    f.deleteTemplate(prevId)
                    dbObject.deleteFromEmployeeInfoTable(reading[2],reading[4],database)
                createNewTemplateToSync(f,reading,dbObject,database)
                t.sleep(.3)
            updateListOfUsedTemplates(f)
            fileObject.updateSyncConfStatus('0')
        else:
            print("Device Is Fully Synced With The Server")
            fileObject.updateSyncConfStatus('0')
            
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{syncUsersToSensor}: ",str(e))
        os.system('sudo pkill -f sasMain.py')
#        fileObject.updateDesiredTask('1')
                         
def getRFCardInformation(dbObject,database):
    try:
        print("Current syncronizationProcess getRFCardInformation Thread ID: {}".format(threading.current_thread()))
        print("Program is Here")
        receivedData = dbObject.getInfoFromEmployeeCardInfoTable(database)
        print(receivedData)
        receivedDataSync = apiObject.getCardDataToSync(receivedData,deviceId)
        print(receivedDataSync)
        if(receivedDataSync == "Some Thing Is Wrong"):
            return "API Error"
        elif(receivedDataSync == "Server Error"):
            return "Server Down"
        else:
            if(len(receivedDataSync['data']) > 0 or len(receivedDataSync['delete_request_enrollment']) > 0):
                for data in receivedDataSync['data']:
                    # print (data['uniqueid']," ",data['companyid'])
                    dbObject.insertIntoEmployeeCardInfoTable(data['employeeid'],\
                                                             data['uniqueid'],\
                                                             data['firstname'],\
                                                             data['cardnumber'],\
                                                             data['companyid'],\
                                                             database)
                for data in receivedDataSync['delete_request_enrollment']:
                    dbObject.deleteFromEmployeeCardInfoTable(data['uniqueid'],data['cardnumber'],database)
                return "Synced From Server"   
            else:
                print("Device Is Already Synced With The Server")
                return "Already Synced"
        dbObject.databaseClose(database)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{getRFCardInformation}",str(e))
        return "Error"
#        os.system('sudo pkill -f sasMain.py')
        
def getFingerprintInformation(dbObject,database):
    try:
        print("Current syncronizationProcess getFingerprintInformation Thread ID: {}".format(threading.current_thread()))
#        apiObject = sasAllAPI()
        checkEmployeeInfoTable(dbObject,database)
        receivedData = dbObject.getInfoFromEmployeeInfoTable(database)
        receivedDataSync = apiObject.getDataToSync(receivedData,deviceId)
        print(receivedData)
        if(receivedDataSync == "Some Thing Is Wrong"):
            return "API Error"
        elif(receivedDataSync == "Server Error"):
            return "Server Down"
        else:
            if(len(receivedDataSync['data']) > 0 or len(receivedDataSync['delete_request_enrollment']) > 0):
                for data in receivedDataSync['data']:
                    dbObject.insertToTempTableToSync(data['employeeid'],\
                                                         data['uniqueid'],\
                                                         data['firstname'],\
                                                         data['fingernumber'],\
                                                         data['matrix'],\
                                                         '1',\
                                                         data['companyid'],\
                                                         database)
                    t.sleep(0.1)
                for data in receivedDataSync['delete_request_enrollment']:
                    dbObject.insertToTempTableToSync("N",\
                                                     data['uniqueid'],\
                                                     "N",\
                                                     data['fingernumber'],\
                                                     "N",\
                                                     '3',\
                                                     '0',\
                                                     database)
                    t.sleep(0.1)
                return "Synced From Server"          
            else:
                print("Device Is Already Synced With The Server")
                return "Already Synced"
#        dbObject.databaseClose(database)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{getFingerprintInformation}: ",str(e))
        return "Error"
#        os.system('sudo pkill -f sasMain.py')
        
def syncronizationProcess():
    while True:
        try:
            print("Current syncronizationProcess Thread ID: {}".format(threading.current_thread()))
            if (fileObject.readSyncConfStatus() == '1'):
                from sasDatabase import sasDatabase
                dbObject = sasDatabase()
                database = dbObject.connectDataBase()
#                synclock.acquire()
                getRFCardInformation(dbObject,database)
#                synclock.release()
                fingerSyncStatus = getFingerprintInformation(dbObject,database)
                
                if fingerSyncStatus == "Synced From Server":
                    fileObject.updateSyncConfStatus('2')
                elif fingerSyncStatus == "Already Synced":
                    fileObject.updateSyncConfStatus('0')
                t.sleep(2)
            else:
                t.sleep(5)
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{syncronizationProcess}: ",str(e))
    
        
def calculateTimeDifference(currentDateTime,timeLimit):
    NowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    diffStart = (datetime.datetime.strptime(str(NowTime), '%Y-%m-%d %H:%M:%S') - \
                 datetime.datetime.strptime(str(currentDateTime), '%Y-%m-%d %H:%M:%S'))
    if(diffStart.seconds > timeLimit):
        return 1
    else:
        return 0
    
#####################################Enrollment Process################################

def takeFingerprintToEnroll(f,currentDateTime):
    print("ENROLL COMMAND RECEIVED")
    x = 0 
    while ( f.readImage() == False and x == 0):
        x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
        t.sleep(1)
        pass
    if (x != 1):
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        if ( positionNumber >= 0 ):
            print("FINGER ALREADY EXISTS")
            return "Already Exists"
        else:
            print("FIRST FINGER TAKEN")
            while ( f.readImage() == True and x == 0):
                x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
            if x != 1:
                print("REMOVED")
                while (1):
                    x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
                    desiredTask = fileObject.readDesiredTask()
                    y = calculateTimeDifference(currentDateTime,REQUESTTIMEOUT)
                    if (desiredTask == '5' or desiredTask == '7' or x == 1 or y == 1):
                        break
                    t.sleep(1) 
                    
                if y == 1:
                    return "Request Time Out"
                elif x != 1:
                    while ( f.readImage() == False and x == 0):
                        x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
                        t.sleep(1)
                        pass
                    if x != 1:
                        f.convertImage(0x02)
                        if ( f.compareCharacteristics() == 0):
                            print("FINGERS DO NOT MATCH")
                            return "Finger Did Not Match Second Time"
                        else:
                            print("SECOND FINGER TAKEN")
                            while ( f.readImage() == True and x == 0):
                                x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
                            if x != 1:
                                print("REMOVED")
                                while (1):
                                    x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
                                    desiredTask = fileObject.readDesiredTask()
                                    y = calculateTimeDifference(currentDateTime,REQUESTTIMEOUT)
                                    if (desiredTask == '5' or desiredTask == '7' or x == 1 or y == 1):
                                        break
                                    t.sleep(1)
                                if y == 1:
                                    return "Request Time Out"
                                elif x != 1:
                                    while ( f.readImage() == False and x == 0):
                                        x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
                                        t.sleep(1)
                                        pass
                                    if x != 1:
                                        f.convertImage(0x01)
                                        if ( f.compareCharacteristics() == 0):
                                            print("FINGERS DO NOT MATCH")
                                            return "Finger Did Not Match Third Time"
                                        else:
                                            print("THIRD FINGER TAKEN")
                                            return "Finger Matched"
                                    else:
                                        print("TIME OUT")
                                        return "Time Out"
                                else:
                                    print("TIME OUT")
                                    return "Time Out"
                            else:
                                print("TIME OUT")
                                return "Time Out"                       
                    else:
                        print("TIME OUT")
                        return "Time Out"
                else:
                    print("TIME OUT")
                    return "Time Out"
            else:
                print("TIME OUT")
                return "Time Out"  
    else:
        print("TIME OUT")
        return "Time Out"

def createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId,dbObject,database):
    characterMatrix = f.downloadCharacteristics()
    matrix = ""
    for i in characterMatrix:
        matrix = matrix+ str(i)+ "-"
    apiObject = sasAllAPI() 
    receivedData = apiObject.getFingerId(uniqueId,matrix,selectedCompany,deviceId)
    if receivedData[0] != "Success":
        f.storeTemplate(int(receivedData[1][3]),0x01)
        dbObject.insertNewEmployee(receivedData[1][0], \
                                   receivedData[1][1], \
                                   receivedData[1][2], \
                                   receivedData[1][3], \
                                   matrix, \
                                   selectedCompany, \
                                   employeeId, \
                                   database)
        print("REGISTED SUCCESSFULLY")
        return "1"
    else:
        print("NOT REGISTED SUCCESSFULLY")
        return receivedData[0]
        
def getAllInfo():
    return ("0","0","0")

def enrollNewEmployee(f,deviceId,dbObject,database):
    currentDateTime,currentTime = checkCurrentDateTime()
    uniqueId,selectedCompany,employeeId = getAllInfo()
    try:
        maintainanceStatus = fileObject.readConfigUpdateStatus()
        if maintainanceStatus == '1':
            fingerInput = takeFingerprintToEnroll(f,currentDateTime)
            if fingerInput == "Finger Matched" :
                status = createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId,dbObject,database)
                if status == "1":
                    print("Registered Successfuly")
                    #GPIO INDICATOR
                else:
                    print("Registered Unsuccessfuly")
                    #GPIO INDICATOR
    except Exception as e:
         fileObject.updateExceptionMessage("sasMain{enrollNewEmployee}: ",str(e))

def createEventLogg(employeeCardorFingerNumber,attendanceFlag,dbObject,database):
    currentDateTime,currentTime = checkCurrentDateTime()
    if attendanceFlag == '2':
        employeeDetails = dbObject.getEmployeeDetailsFromCard(employeeCardorFingerNumber,database)
        if employeeDetails == '0':
            GPIO.output(21, 1)
            dbObject.insertEventTime("0",\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     '0',\
                                     startTime,\
                                     database)
            GPIO.output(21, 0)
        else :
            GPIO.output(20, 1)
            dbObject.insertEventTime(employeeDetails[1],\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     employeeDetails[3],\
                                     startTime,\
                                     database)
            GPIO.output(20, 0)
    elif attendanceFlag == '1':
        employeeDetails = dbObject.getEmployeeDetails(employeeCardorFingerNumber,database)
        if employeeDetails != '0':
            dbObject.insertEventTime(employeeDetails[1], \
                                     employeeCardorFingerNumber, \
                                     currentDateTime, \
                                     attendanceFlag, \
                                     employeeDetails[3], \
                                     startTime,\
                                     database)
            GPIO.output(20, 1)
            GPIO.output(20, 0)
            return 1
        else:
            return 0
       
def matchFingerPrint(f,dbObject,database):
    try:
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        print(positionNumber)
        if (positionNumber == -1):
            GPIO.output(21, 1)
            GPIO.output(21, 0)
        else:
            fingerFlag = createEventLogg(positionNumber,'1',dbObject,database)
            if fingerFlag == 0:
                f.deleteTemplate(positionNumber)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{matchFingerPrint}",str(e))
        
def readFromRFIDScanner():
    ser = serial.Serial("/dev/serial0")
    try:
        ser.baudrate = 9600
        readID = ser.read(11)
        ser.close()
        readID = readID.replace("\x02", "" )
        readID = readID.replace("\x03", "" )
        return readID[2:10]
    except Exception as e:
        ser.close()
        fileObject.updateExceptionMessage("sasMain{readFromRFIDScanner}",str(e))
        os.system('sudo pkill -f sasMain.py')
        return "NA"
    
def workWithFingerPrintSensor(f):
    global desiredTask
    global confStatus
    while True:
        try:
            from sasDatabase import sasDatabase
            dbObject = sasDatabase()
            database = dbObject.connectDataBase()
            while True:  
                while (f.readImage() == False):
                    print("Current workWithFingerPrintSensor Thread ID: {}".format(threading.current_thread()))
                    desiredTask = fileObject.readDesiredTask()
                    confStatus = fileObject.readSyncConfStatus()
                    if (desiredTask == '2' or confStatus == '2') :
                        break
                    t.sleep(.8)
                lock.acquire()
                desiredTask = fileObject.readDesiredTask()
                if desiredTask == '1':
                    fileObject.updateDesiredTask('6')
                    desiredTask = '6'
    #            print("Modified Task is {}".format(desiredTask))    
                if desiredTask == '6':
                    matchFingerPrint(f,dbObject,database)
                    fileObject.updateDesiredTask('1')                  
                elif desiredTask == '2':
                    enrollNewEmployee(f,deviceId,dbObject,database)
                    fileObject.updateDesiredTask('1')
                elif confStatus == '2':
                    syncUsersToSensor(f,dbObject,database)
                lock.release()
                t.sleep(1)
    #            print("A finger Is read")
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithFingerPrintSensor}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()
        
def workWithRFSensor():
    global desiredTask
    while True:
        try:
            from sasDatabase import sasDatabase
            dbObject = sasDatabase()
            database = dbObject.connectDataBase()
            while True:
                print("Current workWithRFSensor Thread ID: {}".format(threading.current_thread()))
                rfScannerValue = readFromRFIDScanner()
                employeeCardNumber = int(rfScannerValue,16)
                print(employeeCardNumber)
                lock.acquire()
                desiredTask = fileObject.readDesiredTask()
                if desiredTask == '1':
                    fileObject.updateDesiredTask('7')
                    desiredTask = '7'
                if desiredTask == '7':
    #                print('Card Number is: {}'.format(employeeCardNumber))
                    createEventLogg(employeeCardNumber,'2',dbObject,database)
                    fileObject.updateDesiredTask('1')
                lock.release()
                t.sleep(1)
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithRFSensor}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()

def functionKillProgram():
    #print("Killing Started")
    t.sleep(900)
    task = fileObject.readDesiredTask()
    if task != '1':
        while 1:
            print("Current functionKillProgram Thread ID: {}".format(threading.current_thread()))
            task = fileObject.readDesiredTask()
            if task == '1':
                break
            t.sleep(1)
    os.system('sudo pkill -f sasMain.py')
#    os.system('sudo pkill -f sasSyncDevice.py')
        
if __name__ == '__main__':
    deviceId = getDeviceId()
    deviceId = 1
    if deviceId != 0:
        f = configureFingerPrint()
        fingerPrint = threading.Thread(target = workWithFingerPrintSensor,args = (f,))
        syncFingerPrint = threading.Thread(target = syncronizationProcess)
        rfSensor = threading.Thread(target = workWithRFSensor)
        checkToKill = threading.Thread(target = functionKillProgram)
        
        fingerPrint.start()
        syncFingerPrint.start()
        rfSensor.start()
        checkToKill.start()
        
        fingerPrint.join()
        syncFingerPrint.join()
        rfSensor.join()
        checkToKill.join()
        
    