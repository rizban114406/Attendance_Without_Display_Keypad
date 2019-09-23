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

from sasDatabase import sasDatabase
dbObject = sasDatabase()
try:
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()
    deviceId = dbObject.getDeviceId(database)
except Exception as e:
    fileObject.updateExceptionMessage("sasMain{Connect To Database}: ",str(e))
    os.system('sudo pkill -f sasMain.py')
    
desiredTask = '1'
lock = threading.Lock()

from sasAllAPI import sasAllAPI
apiObject = sasAllAPI()
REQUESTTIMEOUT = 5
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

def createNewTemplateToSync(f,employeeInfo):
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
    tableIndex1 = f.getTemplateIndex(0)
    tableIndex2 = f.getTemplateIndex(1)
    tableIndex3 = f.getTemplateIndex(2)
    tableIndex4 = f.getTemplateIndex(3)
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
    
def checkEmployeeInfoTable():
    templatesStoredSensor = fileObject.readStoredIndex()
    templateStoredDatabase = dbObject.getEmployeeTemplateNumber(database)
    notListedTemplateNumber = list(set(templateStoredDatabase) - set(templatesStoredSensor))
    dbObject.deleteFromEmployeeInfoTableToSync(notListedTemplateNumber,database)
    
def syncWithOtherDevices(f):
    checkEmployeeInfoTable()
    try:
        receivedData = dbObject.getInfoFromEmployeeInfoTable(database)
        #        print("Existig Data {}".format(receivedData))
        receivedDataSync = apiObject.getDataToSync(receivedData,deviceId)
        if(receivedDataSync == "Some Thing Is Wrong"):
            return "API Error"
        elif(receivedDataSync == "Server Error"):
            return "Server Down"
        else:
            if len(receivedDataSync['data']) > 0:            
                for data in receivedDataSync['data']:
                    prevId = dbObject.checkEmployeeInfoTableToDelete(data['uniqueid'],data['fingernumber'],database)
                    if prevId > 0:
                        f.deleteTemplate(prevId)
                        dbObject.deleteFromEmployeeInfoTable(data['uniqueid'],data['fingernumber'],database)
                        createNewTemplateToSync(f,data)
                        t.sleep(1)
            if len(receivedDataSync['delete_request_enrollment']) > 0:
                prevId = dbObject.checkEmployeeInfoTableToDelete(data['uniqueid'],data['fingernumber'],database)
                f.deleteTemplate(prevId)
                dbObject.deleteFromEmployeeInfoTable(data['uniqueid'],data['fingernumber'],database)
            else:
                print("Device Is Already Synced With The Server")
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{syncWithOtherDevices}: ",str(e))
        fileObject.updateDesiredTask('1')
        dbObject.databaseClose(database)
        os.system('sudo pkill -f sasMain.py')
        
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
    x = 0 
    while ( f.readImage() == False and x == 0):
        x = calculateTimeDifference(currentDateTime,150)
        t.sleep(1)
        pass
    if (x != 1):
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        if ( positionNumber >= 0 ):
            return "Already Exists"
        else:
            t.sleep(1)
            while (1):
                x = calculateTimeDifference(currentDateTime,150)
                desiredTask = fileObject.readDesiredTask()
                y = calculateTimeDifference(currentDateTime,REQUESTTIMEOUT)
                if (desiredTask == '5' or desiredTask == '7' or x == 1 or y == 1):
                    break
                t.sleep(1)
                
            if y == 1:
                return "Request Time Out"
            elif x != 1:
                while ( f.readImage() == False and x == 0):
                    x = calculateTimeDifference(currentDateTime,150)
                    t.sleep(1)
                    pass
                if x != 1:
                    f.convertImage(0x02)
                    if ( f.compareCharacteristics() == 0):
                        return "Finger Did Not Match Second Time"
                    else:
                        while (fileObject.readDesiredTask() != 5 and x == 0):
                            x = calculateTimeDifference(currentDateTime,150)
                            t.sleep(1)
                            pass
                        if x != 1:
                            while (1):
                                x = calculateTimeDifference(currentDateTime,150)
                                desiredTask = fileObject.readDesiredTask()
                                y = calculateTimeDifference(currentDateTime,REQUESTTIMEOUT)
                                if (desiredTask == '5' or desiredTask == '7' or x == 1 or y == 1):
                                    break
                                t.sleep(1)
                            if y == 1:
                                return "Request Time Out"
                            elif x != 1:
                                f.convertImage(0x01)
                                if ( f.compareCharacteristics() == 0):
                                    return "Finger Did Not Match Third Time"
                                else:
                                    return "Finger Matched"
                        else:
                            return "Time Out"
                else:
                    return "Time Out"
            else:
                return "Time Out"
    else:
        return "Time Out"

def createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId):
    characterMatrix = f.downloadCharacteristics()
    matrix = ""
    for i in characterMatrix:
        matrix = matrix+ str(i)+ "-"
        
    receivedData = apiObject.getFingerId(uniqueId,matrix,selectedCompany,deviceId)
    if receivedData != "no" and receivedData != "Server Error":
        f.storeTemplate(int(receivedData[3]),0x01)
        dbObject.insertNewEmployee(receivedData[0], \
                                   receivedData[1], \
                                   receivedData[2], \
                                   receivedData[3], \
                                   matrix, \
                                   selectedCompany, \
                                   employeeId, \
                                   database)
        return "1"
    else:
        return receivedData
        
def enrollNewEmployee(f,deviceId):
    currentDateTime,currentTime = checkCurrentDateTime()
    x = 0
    try:
        maintainanceStatus = fileObject.readConfigUpdateStatus()
        if maintainanceStatus == '1':
            enteredPassword = getPasswordToEnroll(currentDateTime)
            if (enteredPassword != "Time Out" and len(enteredPassword) != 0):
                severCheckPassword = apiObject.authenticatePassword(enteredPassword,deviceId)
                t.sleep(.5)
                if (severCheckPassword == "Matched"):
                    selectedCompany = selectCompanyToEnroll(currentDateTime)
                    t.sleep(.8)
                    if selectedCompany > 0:
                        employeeId = getEmployeeIdToEnroll(currentDateTime)
                        if (employeeId != "Time Out" and len(employeeId) != 0):
                            #localCheck = dbObject.checkEmployeeInfoTable(employeeId,selectedCompany,database)
                            #print localCheck
                            localCheck = "Not Registered"
                            x = calculateTimeDifference(currentDateTime,150)
                            if (localCheck != "Registered"):
                                serverCheck = apiObject.checkServerStatus(employeeId,selectedCompany)
                                #print serverCheck
                                if (serverCheck != "Registered" and serverCheck != "Invalid" and serverCheck != "Server Down" and x != 1):
                                    uniqueId = int(serverCheck)
                                    fingerInput = takeFingerprintToEnroll(f,currentDateTime)
                                    if fingerInput == 1 :
                                        status = createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId)
                                        if status == "1":
                                            lcdPrint.printSuccessEnrollmentMessage()
                                        else:
                                            lcdPrint.printUnsuccessEnrollmentMessage(status)                                                  
                                else:
                                    lcdPrint.printValidEmployeeNotSuccess(serverCheck,employeeId,x)
                            else:
                                lcdPrint.printValidEmployeeNotSuccess(localCheck,employeeId,x)
                        elif len(employeeId) == 0:
                            lcdPrint.printIDNotGivenOrTimeOutOrCanceled("","",x)
                else:
                    lcdPrint.printPasswordResponse(severCheckPassword,x)
            elif len(enteredPassword) == 0:
                lcdPrint.printPasswordNotGivenOrTimeOutOrCanceled("","",x)
        else:
            lcdPrint.printDeviceMaintanace()
    except Exception as e:
         lcdPrint.printExceptionMessage(str(e))
         fileObject.updateExceptionMessage("sasMain{enrollNewEmployee}",str(e))

def createEventLogg(employeeCardorFingerNumber,attendanceFlag):
    currentDateTime,currentTime = checkCurrentDateTime()
    if attendanceFlag == '2':
        employeeDetails = dbObject.getEmployeeDetailsFromCard(employeeCardorFingerNumber,database)
        if employeeDetails == '0':
            GPIO.output(21, 1)
            dbObject.insertEventTime("0",\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     '0',
                                     database)
            lcdPrint.printIfNoMatchFound()
            GPIO.output(21, 0)
        else :
            GPIO.output(20, 1)
            dbObject.insertEventTime(employeeDetails[1],\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     employeeDetails[3],\
                                     database)
            lcdPrint.printAfterSuccessfullEventLogg(currentTime,employeeDetails)
            GPIO.output(20, 0)
            
    elif attendanceFlag == '1':
        employeeDetails = dbObject.getEmployeeDetails(employeeCardorFingerNumber,database)
        if employeeDetails != '0':
            dbObject.insertEventTime(employeeDetails[1], \
                                     employeeCardorFingerNumber, \
                                     currentDateTime, \
                                     attendanceFlag, \
                                     employeeDetails[3], \
                                     database)
            GPIO.output(20, 1)
            lcdPrint.printAfterSuccessfullEventLogg(currentTime,employeeDetails)        
            GPIO.output(20, 0)
            return 1
        else:
            return 0
       
def matchFingerPrint(f):
    try:
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        print(positionNumber)
        if (positionNumber == -1):
            GPIO.output(21, 1)
            lcdPrint.printIfNoMatchFound()
            GPIO.output(21, 0)
        else:
            fingerFlag = createEventLogg(positionNumber,'1')
            if fingerFlag == 0:
                f.deleteTemplate(positionNumber)
                lcdPrint.printAfterSuccessfullEventLoggButNoEmployeeID()
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
    
def workWithFingerPrintSensor():
    global desiredTask
    while True:
        try:
            f = configureFingerPrint()
            lock.acquire()
            fileObject.updateDesiredTask('4')
            syncWithOtherDevices(f)
            fileObject.updateDesiredTask('1')
            lock.release()
            lcdPrint.printInitialMessage()
            while True:  
                while (f.readImage() == False):
                    desiredTask = fileObject.readDesiredTask()
                    if (desiredTask == '2') :
                        break
                    t.sleep(.8)
                lock.acquire()
                desiredTask = fileObject.readDesiredTask()
                if desiredTask == '1':
                    fileObject.updateDesiredTask('6')
                    desiredTask = '6'
    #            print("Modified Task is {}".format(desiredTask))    
                if desiredTask == '6':
                    lcdPrint.printPleaseWait()
                    matchFingerPrint(f)
                    fileObject.updateDesiredTask('1')
                    lcdPrint.printInitialMessage()
                    
                elif desiredTask == '2':
                    lcdPrint.printPleaseWait()
                    enrollNewEmployee(f,deviceId)
                    fileObject.updateDesiredTask('1')
                    lcdPrint.printInitialMessage()     
                lock.release()
                t.sleep(1)
    #            print("A finger Is read")
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithFingerPrintSensor}",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()
        
def workWithRFSensor():
    global desiredTask
    while True:
        try:
            while True:
                rfScannerValue = readFromRFIDScanner()
                employeeCardNumber = int(rfScannerValue,16)
                print(employeeCardNumber)
                lock.acquire()
                desiredTask = fileObject.readDesiredTask()
                if desiredTask == '1':
                    fileObject.updateDesiredTask('7')
                    desiredTask = '7'
                if desiredTask == '7':
                    lcdPrint.printPleaseWait()
    #                print('Card Number is: {}'.format(employeeCardNumber))
                    createEventLogg(employeeCardNumber,'2')
                    fileObject.updateDesiredTask('1')
                    lcdPrint.printInitialMessage()
                lock.release()
                t.sleep(1)
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithRFSensor}",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()

def functionKillProgram():
    #print("Killing Started")
    t.sleep(900)
    task = fileObject.readDesiredTask()
    if task != '1':
        while 1:
            task = fileObject.readDesiredTask()
            if task == '1':
                break
            t.sleep(1)
    os.system('sudo pkill -f sasMain.py')
    os.system('sudo pkill -f sasSyncDevice.py')

def setDeviceTime():
    try:
        nowTime = apiObject.getTime()
        if nowTime != "Not Successfull":
            command = "sudo date -s "+ '"'+nowTime+'"'
            os.system(command)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{setDEviceTime}",str(e))
        
if __name__ == '__main__':
    setDeviceTime()
    if deviceId != 0:
        lcdPrint.printInitialMessage()     
        fingerPrint = threading.Thread(target = workWithFingerPrintSensor)
        rfSensor = threading.Thread(target = workWithRFSensor)
        checkToKill = threading.Thread(target = functionKillProgram)
        
        fingerPrint.start()
        rfSensor.start()
        checkToKill.start()
        
        fingerPrint.join()
        rfSensor.join()
        checkToKill.join()
    