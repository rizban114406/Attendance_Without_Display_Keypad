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
import pusher as push
import json
import RPi.GPIO as GPIO

redLightPin = 21
greenLightPin = 20
blueLightPin = 13
buzzerPin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(redLightPin, GPIO.OUT)
GPIO.setup(greenLightPin, GPIO.OUT)
GPIO.setup(blueLightPin, GPIO.OUT)
GPIO.setup(buzzerPin, GPIO.OUT)


from pyfingerprint.pyfingerprint import PyFingerprint

from sasFile import sasFile
fileObject = sasFile()
appId = '860616'
key = 'de47d29a0309c4e2c87e'
secret = '87b85c977153726607e7'
pusherSend = push.Pusher(appId, key, secret)
def getHardwareId():
    # Extract serial from cpuinfo file
    cpuserial = ""
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            # print line[0:4]
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{getHardwareId}",str(e))
        cpuserial = "Error"
    return cpuserial

hardwareId = getHardwareId()
hardwareId = "asdasdas"
currentTask = '1'
syncStatus = '0'
lock = threading.Lock()
startTime = fileObject.readStartTime()

from sasAllAPI import sasAllAPI
apiObject = sasAllAPI(2)
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
    x = str(employeeInfo[3]).split('-')
    characteristics = []
    for i in range(0,len(x)-1):
        characteristics.append(int(x[i]))
    f.uploadCharacteristics(0x01,characteristics)
    f.storeTemplate(int(employeeInfo[2]),0x01)
#    import re
#    sp = re.split(' |-|',str(employeeInfo[1]))
#    if(len(sp) == 2):
#        employee = sp[1]
#    else:
#        employee = sp[0]

    dbObject.insertNewEmployee(employeeInfo[1], \
                               employeeInfo[2], \
                               employeeInfo[5], \
                               database)
    dbObject.deleteFromTempTableToSync(employeeInfo[1],employeeInfo[2],database)
        

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
        if (len(getDataToDelete) > 0 or len(getDataToSync) > 0):
            for reading in getDataToDelete:
                turnLEDON('R+G')
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[0],reading[1],database)
                f.deleteTemplate(prevId)
                dbObject.deleteFromEmployeeInfoTable(reading[0],reading[1],database)
                dbObject.deleteFromTempTableToSync(reading[0],reading[1],database)
                t.sleep(.3)
                turnLEDON('OFF')
            for reading in getDataToSync:
                turnLEDON('R+G')
                prevId = dbObject.checkEmployeeInfoTableToDelete(reading[1],reading[2],database)
                if prevId > 0:
                    f.deleteTemplate(prevId)
                    dbObject.deleteFromEmployeeInfoTable(reading[1],reading[2],database)
                createNewTemplateToSync(f,reading,dbObject,database)
                t.sleep(.3)
                turnLEDON('OFF')
            updateListOfUsedTemplates(f)
            fileObject.updateSyncStatus('0')
        else:
            print("Device Is Fully Synced With The Server")
            fileObject.updateSyncStatus('0')
            
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{syncUsersToSensor}: ",str(e))
        os.system('sudo pkill -f sasMain.py')
#        fileObject.updateCurrentTask('1')
                         
def getRFCardInformation(deviceId,dbObject,database):
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
                    dbObject.insertIntoEmployeeCardInfoTable(data['uniqueid'],\
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
        fileObject.updateExceptionMessage("sasMain{getRFCardInformation}: ",str(e))
        return "Error"
#        os.system('sudo pkill -f sasMain.py')
        
def getFingerprintInformation(deviceId,dbObject,database):
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
                dbObject.createTableTempTableToSync(database)
                for data in receivedDataSync['data']:
                    dbObject.insertToTempTableToSync(data['uniqueid'],\
                                                     data['fingernumber'],\
                                                     data['matrix'],\
                                                     '1',\
                                                     data['companyid'],\
                                                     database)
                    t.sleep(0.1)
                for data in receivedDataSync['delete_request_enrollment']:
                    dbObject.insertToTempTableToSync(data['uniqueid'],\
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
            if (fileObject.readSyncStatus() == '1'):
                from sasDatabase import sasDatabase
                dbObject = sasDatabase()
                database = dbObject.connectDataBase()
                deviceId = dbObject.getDeviceId()
                if deviceId != 0:
                    getRFCardInformation(deviceId,dbObject,database)
                    fingerSyncStatus = getFingerprintInformation(deviceId,dbObject,database)
                    
                    if fingerSyncStatus == "Synced From Server":
                        fileObject.updateSyncStatus('2')
                    elif fingerSyncStatus == "Already Synced":
                        fileObject.updateSyncStatus('0')
                    t.sleep(2)
                else:
                    t.sleep(5)
            else:
                t.sleep(5)
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{syncronizationProcess}: ",str(e))
    
        
def calculateTimeDifference(currentDateTime,timeLimit):
    NowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    diffStart = (datetime.datetime.strptime(str(NowTime), '%Y-%m-%d %H:%M:%S') - \
                 datetime.datetime.strptime(str(currentDateTime), '%Y-%m-%d %H:%M:%S'))
    if(diffStart.seconds > timeLimit):
        return True
    else:
        return False
    
#####################################Enrollment Process################################
def sendPusherCommand(hardwareId,command,requestId):
    deviceInfoData = {"hardwareId" : hardwareId,\
                      "command"    : command,\
                      "requestId"  : requestId}
    print(deviceInfoData)
    commandToSend = json.dumps(deviceInfoData)
    pusherSend.trigger('enroll-feed-channel', 'enroll-feed-event', commandToSend)
    
def takefingerPrint(f,currentDateTime):
    x = False
    continueEnrollment = False
    try:
        while ( f.readImage() == False and x == False):
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT) # Checking For Time Out
            if (fileObject.readCurrentTask() == "5"): # Checking if Enrollment is Cancelled or Not
                continueEnrollment = False
                turnLEDON('R')
                turnOnBuzzer(0)
                break
            turnLEDON('OFF')
            t.sleep(1)
            turnLEDON('W')
        turnLEDON('OFF')
        return (x,continueEnrollment)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{fingerPrint}: ",str(e))
        continueEnrollment = False
        return (x,continueEnrollment)

def waitToRemoveFinger(f,currentDateTime):
    x = False
    continueEnrollment = False
    try:
        while ( f.readImage() == True and x == False): # Check if the User is Still Keeping the Finger on the Sensor
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
            if (fileObject.readCurrentTask() == "5"):
                continueEnrollment = False
                break
            t.sleep(1)
        print("Finger Removed")
        return (x,continueEnrollment)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{fingerPrint}: ",str(e))
        continueEnrollment = False
        return (x,continueEnrollment)
    
def waitForServerInstructionToCome(desiredCommand, currentDateTime):
    x = False
    y = False
    try:
        currentDateTimeForResponse,currentTimeForResponse = checkCurrentDateTime() 
        while (1): # Waiting Untill Command is Received from the Server or Enrollment Cancelled or Enrollment Timeout or Response Timeout
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
            currentTask = fileObject.readCurrentTask()                       
            y = calculateTimeDifference(currentDateTimeForResponse,REQUESTTIMEOUT) # Checking for Response Timeout
            if (currentTask == desiredCommand or currentTask == '5' or x == True or y == True): # Command Received or Cancelled or Enrollment Timeout or Response Timeout
                break
            t.sleep(0.5)
        return (currentTask, x, y)
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{waitForServerInstructionToCome}: ",str(e))
        y = True
        return (currentTask, x, y)
    
def enrollmentLEDIndicator(color):
    if color == 'R':
        turnLEDON('R')
        turnOnBuzzer(0)
        turnLEDON('OFF')
    elif color == 'G':
        turnLEDON('G')
        turnOnBuzzer(1)
        t.sleep(1) # Wait for the User to Remove the Finger
        turnLEDON('OFF')
        
    
def takeFingerprintToEnroll(f,currentDateTime,requestId):
    x = False # Flag to check Enrollment Timeout
    y = False # Flag to Check Response Timeout
    print(y)
    print(x)
    continueEnrollment = True # Flag to Check If Enrollment Process is Cancelled or Not
    try:
        x,continueEnrollment = takefingerPrint(f,currentDateTime)
        
        if (x == False  and continueEnrollment == True): #If Enrollment is Not Timed Out and Enrollment is Not Cancelled
            print("Convert the Print")
            f.convertImage(0x01) #Save the Fingerprint to Sensor Buffer
            print("Image Converted")
            result = f.searchTemplate() # Search if the Template Already Exists or Not
            positionNumber = result[0]
            
            if ( positionNumber >= 0 ): # If Template Exists positonNumber will be > 0
                sendPusherCommand(hardwareId,"FINGER_ALREADY_EXISTS",requestId) # Send Already Exists Command to the Server
                return "Enrollment Cancelled"
            else:
                sendPusherCommand(hardwareId,"FIRST_FINGER_TAKEN",requestId) # Send First Finger Taken Confirmation to the Server
                enrollmentLEDIndicator('G')
                print("First Finger Taken")
                
                x,continueEnrollment = waitToRemoveFinger(f,currentDateTime)
                    
                if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                    sendPusherCommand(hardwareId,"REMOVED1",requestId) # Send Removed Command To the Server First Time
                    t.sleep(1)
                    print("Removed Sent")
                    
                    currentTask, x, y = waitForServerInstructionToCome('3', currentDateTime)
                    
                    if (currentTask == "5"): # Enrollment Cancelled Check
                        return "Enrollment Cancelled"
                    
                    elif y == True: # Response Timeout Check
                        sendPusherCommand(hardwareId,"TIME_OUT",requestId) # Send Timeout Response to the Server
                        return "Request Time Out"
                    
                    elif x == False : # If Enrollment is Not Timed Out
                        x,continueEnrollment = takefingerPrint(f,currentDateTime)
                        
                        if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                            f.convertImage(0x02)
                            if ( f.compareCharacteristics() == 0): # If First and Second Do Not Matche
                                sendPusherCommand(hardwareId,"FINGERS_DO_NOT_MATCH",requestId) # Send Finger Not Matched to the Server
                                return "Finger Did Not Match Second Time"
                            
                            else:
                                sendPusherCommand(hardwareId,"SECOND_FINGER_TAKEN",requestId) # Send Second Time Finger Taken To the Server
                                enrollmentLEDIndicator('G')
                                
                                x,continueEnrollment = waitToRemoveFinger(f,currentDateTime)
                                
                                if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                                    sendPusherCommand(hardwareId,"REMOVED2",requestId)
                                    t.sleep(1)
                                    
                                    currentTask, x, y = waitForServerInstructionToCome('4', currentDateTime)
                                    
                                    if (currentTask == "5"): # Enrollment Cancelled Check
                                        return "Enrollment Cancelled"
                                    elif y == True: # Response Timeout
                                        sendPusherCommand(hardwareId,"TIME_OUT",requestId) # Send Timeout to the Server 
                                        return "Request Time Out"
                                    elif x == False:
                                        
                                        x,continueEnrollment = takefingerPrint(f,currentDateTime)
                                        
                                        if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                                            f.convertImage(0x01)
                                            if ( f.compareCharacteristics() == 0): # Check Finger Matched 
                                                sendPusherCommand(hardwareId,"FINGERS_DO_NOT_MATCH",requestId) # Send Not Matched to the Server
                                                return "Finger Did Not Match Third Time"
                                            else:
                                                sendPusherCommand(hardwareId,"THIRD_FINGER_TAKEN",requestId) # Send Third Finger Taken to THe Server
                                                enrollmentLEDIndicator('G')
                                                return "Finger Matched"
                                        else:
                                            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                            return "Time Out"
                                    else:
                                        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                        return "Time Out"
                                else:
                                    sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                    return "Time Out"   
                        else:
                            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                            return "Time Out"
                    else:
                        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                        return "Time Out"
                else:
                    sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                    return "Time Out"
        else:
            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
            return "Time Out"
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{takeFingerprintToEnroll}: ",str(e))
        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
        return "Time Out"

def createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId,dbObject,database):
    characterMatrix = f.downloadCharacteristics()
    matrix = ""
    for i in characterMatrix:
        matrix = matrix+ str(i)+ "-"
    receivedData = apiObject.getFingerId(uniqueId,matrix,selectedCompany,deviceId)
    print(receivedData)
    if receivedData[0] == "Success":
        f.storeTemplate(int(receivedData[1][3]),0x01)
        dbObject.insertNewEmployee(receivedData[1][0], \
                                   receivedData[1][1], \
                                   selectedCompany, \
                                   database)
        return "1"
    else:
        return receivedData[0]
        
def enrollNewEmployee(f,deviceId,dbObject,database):
    currentDateTime,currentTime = checkCurrentDateTime()
    uniqueId,selectedCompany= fileObject.readEnrollingUserInfo()
    employeeId = "2-265"
    requestId = fileObject.readRequestId()
    print(uniqueId)
    print(selectedCompany)
    print(requestId)
    try:
        fingerInput = takeFingerprintToEnroll(f,currentDateTime,requestId)
        if fingerInput == "Finger Matched" :
            status = createNewTemplate(f,uniqueId,selectedCompany,employeeId,deviceId,dbObject,database)
            if status == "1":
                sendPusherCommand(hardwareId,"REGISTED_SUCCESSFULLY",requestId)
                enrollmentLEDIndicator('G')
                fileObject.updateRequestId("0")
                print("Registered Successfuly")
                #GPIO INDICATOR
            else:
                sendPusherCommand(hardwareId,"NOT_REGISTED_SUCCESSFULLY",requestId)
                enrollmentLEDIndicator('R')
                fileObject.updateRequestId("0")
                print("Registered Unsuccessfuly")
        else:
            enrollmentLEDIndicator('R')
            fileObject.updateRequestId("0")
    except Exception as e:
         fileObject.updateExceptionMessage("sasMain{enrollNewEmployee}: ",str(e))
         enrollmentLEDIndicator('R')
         fileObject.updateRequestId("0")
         sendPusherCommand(hardwareId,"TIME_OUT",requestId)

def turnLEDON(color):
    if color == 'R':
        GPIO.output(redLightPin, 1)
        GPIO.output(greenLightPin, 0)
        GPIO.output(blueLightPin, 0)
    elif color == 'G':
        GPIO.output(redLightPin, 0)
        GPIO.output(greenLightPin, 1)
        GPIO.output(blueLightPin, 0)
    elif color == 'B':
        GPIO.output(redLightPin, 0)
        GPIO.output(greenLightPin, 0)
        GPIO.output(blueLightPin, 1)
    elif color == 'W':
        GPIO.output(redLightPin, 1)
        GPIO.output(greenLightPin, 1)
        GPIO.output(blueLightPin, 1)
    elif color == 'R+G':
        GPIO.output(redLightPin, 1)
        GPIO.output(greenLightPin, 1)
        GPIO.output(blueLightPin, 0)
    elif color == 'G+B':
        GPIO.output(redLightPin, 0)
        GPIO.output(greenLightPin, 1)
        GPIO.output(blueLightPin, 1)
    elif color == 'R+B':
        GPIO.output(redLightPin, 1)
        GPIO.output(greenLightPin, 0)
        GPIO.output(blueLightPin, 1)
    elif color == 'OFF':
        GPIO.output(redLightPin, 0)
        GPIO.output(greenLightPin, 0)
        GPIO.output(blueLightPin, 0)
    
def turnOnBuzzer(access):
    GPIO.output(buzzerPin, 1)
    if access == 1:
        t.sleep(.5)
    else:
        t.sleep(1)
    GPIO.output(buzzerPin, 0)
    
def createEventLogg(employeeCardorFingerNumber,attendanceFlag,dbObject,database):
    currentDateTime,currentTime = checkCurrentDateTime()
    if attendanceFlag == '2':
        employeeDetails = dbObject.getEmployeeDetailsFromCard(employeeCardorFingerNumber,database)
        print("Punched Employee ID: {}".format(employeeDetails))
        if employeeDetails == '0':
            print("No Card Record Found")
            dbObject.insertEventTime("0",\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     '0',\
                                     database)
            turnLEDON('R') #RED
            turnOnBuzzer(0)
            t.sleep(.5)
            turnLEDON('OFF') #OFF
        else :
            print("Card Record Found")
            GPIO.output(greenLightPin, 1)
            dbObject.insertEventTime(employeeDetails[0],\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     employeeDetails[1],\
                                     database)
            turnLEDON('G') #GREEN
            turnOnBuzzer(1)
            t.sleep(.5)
            turnLEDON('OFF') #OFF
    elif attendanceFlag == '1': #################################################Check For Secondary Address in event script######
        employeeDetails = dbObject.getEmployeeDetails(employeeCardorFingerNumber,database)
        print("Punched Employee ID: {}".format(employeeDetails))
        if employeeDetails != '0':
            print("Finger Record Found")
            dbObject.insertEventTime(employeeDetails[0], \
                                     employeeCardorFingerNumber, \
                                     currentDateTime, \
                                     attendanceFlag, \
                                     employeeDetails[1], \
                                     database)
            turnLEDON('G') #GREEN
            turnOnBuzzer(1)
            t.sleep(.5)
            turnLEDON('OFF') #OFF
            return 1
        else:
            print("No Finger Record Found")
            turnLEDON('R') #RED
            turnOnBuzzer(0)
            t.sleep(.5)
            turnLEDON('OFF') #OFF
            return 0
        
def matchFingerPrint(f,dbObject,database):
    try:
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        print(positionNumber)
        if (positionNumber == -1):
            print("No Finger Record Found")
            turnLEDON('R') #RED
            turnOnBuzzer(0)
            t.sleep(.5)
            turnLEDON('OFF') #OFF
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
    global currentTask
    global syncStatus
    while True:
        try:
            from sasDatabase import sasDatabase
            dbObject = sasDatabase()
            database = dbObject.connectDataBase()
            while True:  
                while (f.readImage() == False):
#                    print("Current workWithFingerPrintSensor Thread ID: {}".format(threading.current_thread()))
                    currentTask = fileObject.readCurrentTask()
                    syncStatus = fileObject.readSyncStatus()
                    print(currentTask)
                    print(syncStatus)
                    if (currentTask == '2' or syncStatus == '2') :
                        break
                    t.sleep(.8)
                lock.acquire()
                currentTask = fileObject.readCurrentTask()
                if currentTask == '1'and syncStatus != '2':
                    fileObject.updateCurrentTask('6')
                    currentTask = '6'
    #            print("Modified Task is {}".format(currentTask))    
                if currentTask == '6':
                    matchFingerPrint(f,dbObject,database)
                    fileObject.updateCurrentTask('1')                  
                elif currentTask == '2':
                    deviceId = dbObject.getDeviceId()
                    enrollNewEmployee(f,deviceId,dbObject,database)
                    fileObject.updateCurrentTask('1')
                elif syncStatus == '2':
                    print("Sync Process")
                    syncUsersToSensor(f,dbObject,database)
                lock.release()
                t.sleep(1)
    #            print("A finger Is read")
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithFingerPrintSensor}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()
        
def workWithRFSensor():
    global currentTask
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
                if len(rfScannerValue) < 10:
                    lock.acquire()
                    currentTask = fileObject.readCurrentTask()
                    if currentTask == '1':
                        fileObject.updateCurrentTask('7')
                        currentTask = '7'
                    if currentTask == '7':
        #                print('Card Number is: {}'.format(employeeCardNumber))
                        createEventLogg(employeeCardNumber,'2',dbObject,database)
                        fileObject.updateCurrentTask('1')
                    lock.release()
                    t.sleep(1)
        except Exception as e:
            fileObject.updateExceptionMessage("sasMain{workWithRFSensor}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()

def functionKillProgram():
    #print("Killing Started")
    t.sleep(900)
    task = fileObject.readCurrentTask()
    if task != '1':
        while 1:
            print("Current functionKillProgram Thread ID: {}".format(threading.current_thread()))
            task = fileObject.readCurrentTask()
            if task == '1':
                break
            t.sleep(1)
    os.system('sudo pkill -f sasMain.py')
        
if __name__ == '__main__':
    try:
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
    except Exception as e:
        fileObject.updateExceptionMessage("sasMain{__main__}: ",str(e))
        os.system('sudo pkill -f sasMain.py')
        
    