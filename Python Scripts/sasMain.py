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
doorLockPin = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(redLightPin, GPIO.OUT)
GPIO.setup(greenLightPin, GPIO.OUT)
GPIO.setup(blueLightPin, GPIO.OUT)
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.setup(doorLockPin, GPIO.OUT)
def doorStatus(status):
    if status == 1:
        GPIO.output(doorLockPin, status)
    else:
        GPIO.output(doorLockPin, status)

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
doorStatus(0)
#hardwareId = "asdasdas"
currentTask = '1'
syncStatus = '0'
lock = threading.Lock()

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
            print("Exception From : {}\n Exception Message: {}".format("configureFingerPrint",str(e)))
            fileObject.updateExceptionMessage("sasMain{configureFingerPrint}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
    return f

def checkCurrentDateTime():
    nowTime = datetime.datetime.now()
    currentTime = nowTime.strftime('%H:%M:%S')
    currentDateTime = nowTime.strftime('%Y-%m-%d %H:%M:%S')
    return (currentDateTime,currentTime)

def createNewTemplateToSync(f,employeeInfo,dbObject,database):
    x = str(employeeInfo[2]).split('-')
    characteristics = []
    for i in range(0,len(x)-1):
        characteristics.append(int(x[i]))
    f.uploadCharacteristics(0x01,characteristics)
    f.storeTemplate(int(employeeInfo[1]),0x01)
#    import re
#    sp = re.split(' |-|',str(employeeInfo[1]))
#    if(len(sp) == 2):
#        employee = sp[1]
#    else:
#        employee = sp[0]

    dbObject.insertNewEmployee(employeeInfo[0], \
                               employeeInfo[1], \
                               database)
    dbObject.deleteFromTempTableToSync(employeeInfo[0],employeeInfo[1],database)
        

def updateListOfUsedTemplates(f):
    print("Inside Function: {}".format("updateListOfUsedTemplates"))
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
    print("Stored Index : {}".format(storedIndex))
    fileObject.updateStoredIndex(storedIndex)
    
def checkEmployeeInfoTable(dbObject,database):
    try:    
        print("Inside Function: {}".format("checkEmployeeInfoTable"))
        templatesStoredSensor = fileObject.readStoredIndex()
        print("templatesStoredSensor Info: {}".format(templatesStoredSensor))
        templateStoredDatabase = dbObject.getEmployeeTemplateNumber(database)
        print("templateStoredDatabase Info: {}".format(templateStoredDatabase))
        notListedTemplateNumber = list(set(templateStoredDatabase) - set(templatesStoredSensor))
        print("Redundent Info: {}".format(notListedTemplateNumber))
        dbObject.deleteFromEmployeeInfoTableToSync(notListedTemplateNumber,database)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("checkEmployeeInfoTable",str(e)))
        fileObject.updateExceptionMessage("sasMain{checkEmployeeInfoTable}: ",str(e))
        
def syncUsersToSensor(f,dbObject,database):
    try:
        global apiObject
        apiObject = sasAllAPI(2)
        print("Inside Function: {}".format("syncUsersToSensor"))
        getDataToDelete = dbObject.getInfoFromTempTableToDelete(database)
        print("Finger Delete Request: {}".format(getDataToDelete))
        getDataToSync = dbObject.getInfoFromTempTableToEnrollOrUpdate(database)
        print("Finger Enrollment Request: {}".format(getDataToSync))
        if (len(getDataToDelete) > 0 or len(getDataToSync) > 0):
            for reading in getDataToDelete:
                turnLEDON('R+G')
                f.deleteTemplate(int(reading[1]))
                dbObject.deleteFromEmployeeInfoTable(reading[0],reading[1],database)
                dbObject.deleteFromTempTableToSync(reading[0],reading[1],database)
                print("Deleted Employee Info: {}".format(reading))
                t.sleep(.2)
#                turnLEDON('OFF')
            for reading in getDataToSync:
                turnLEDON('R+G')
                createNewTemplateToSync(f,reading,dbObject,database)
                print("Enrolled Employee Info: {}".format(reading[0:1]))
                t.sleep(.3)
#                turnLEDON('OFF')
            updateListOfUsedTemplates(f)
            fileObject.updateSyncStatus('0')
            print("Finger Info Is Synced To the Device")
        else:
            print("Device Is Fully Synced With The Server")
            fileObject.updateSyncStatus('0')
            
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("syncUsersToSensor",str(e)))
        fileObject.updateExceptionMessage("sasMain{syncUsersToSensor}: ",str(e))
        os.system('sudo pkill -f sasMain.py')
#        fileObject.updateCurrentTask('1')
                         
def getRFCardInformation(deviceId,dbObject,database):
    try:
        print("Inside Function: {}".format("getRFCardInformation"))
        receivedData = dbObject.getInfoFromEmployeeCardInfoTable(database)
        print("Existing Card Data: {}".format(receivedData))
        if (apiObject.checkServerStatus() == 1):
            receivedDataSync = apiObject.getCardDataToSync(receivedData,deviceId)
        else:
            receivedDataSync = "Server Error"
        print("Received Data For Card Sync: {}".format(receivedDataSync))
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
                                                             database)
                    print("New Card Request Entered: {}".format(data))
                for data in receivedDataSync['delete_request_enrollment']:
                    dbObject.deleteFromEmployeeCardInfoTable(data['uniqueid'],data['cardnumber'],database)
                    print("Delete Card Request Entered: {}".format(data))
                print("Card Info Is Synced From Server")
                return "Synced From Server"   
            else:
                print("Device Is Already Synced With The Server")
                return "Already Synced"
        dbObject.databaseClose(database)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("getRFCardInformation",str(e)))
        fileObject.updateExceptionMessage("sasMain{getRFCardInformation}: ",str(e))
        return "Error"
#        os.system('sudo pkill -f sasMain.py')
        
def getFingerprintInformation(deviceId,dbObject,database):
    try:
        print("Inside Function: {}".format("getFingerprintInformation"))
#        apiObject = sasAllAPI()
        checkEmployeeInfoTable(dbObject,database)
        receivedData = dbObject.getInfoFromEmployeeInfoTable(database)
        print("Existing Finger Data: {}".format(receivedData))
        if (apiObject.checkServerStatus() == 1):
            receivedDataSync = apiObject.getDataToSync(receivedData,deviceId)
        else:
            receivedDataSync = "Server Error"
        print("Received Data For Finger Sync: {}".format(receivedDataSync))
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
                                                     database)
                    print("Finger Request: {}".format(data))
                    t.sleep(0.1)
                for data in receivedDataSync['delete_request_enrollment']:
                    dbObject.insertToTempTableToSync(data['uniqueid'],\
                                                     data['fingernumber'],\
                                                     "N",\
                                                     '3',\
                                                     database)
                    print("Finger Delete Request: {}".format(data))
                    t.sleep(0.1)
                print("Card Info Is Synced From Server")
                return "Synced From Server"          
            else:
                print("Device Is Already Synced With The Server")
                return "Already Synced"
#        dbObject.databaseClose(database)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("getFingerprintInformation",str(e)))
        fileObject.updateExceptionMessage("sasMain{getFingerprintInformation}: ",str(e))
        return "Error"
#        os.system('sudo pkill -f sasMain.py')
        
def syncronizationProcess():
    while True:
        try:
#            print("Current syncronizationProcess Thread ID: {}".format(threading.current_thread()))
            if (fileObject.readSyncStatus() == '1'):
                from sasDatabase import sasDatabase
                dbObject = sasDatabase()
                database = dbObject.connectDataBase()
                deviceId = dbObject.getDeviceId(database)
                if deviceId != 0:
                    getRFCardInformation(deviceId,dbObject,database)
                    fingerSyncStatus = getFingerprintInformation(deviceId,dbObject,database)
                    
                    if fingerSyncStatus == "Synced From Server":
                        fileObject.updateSyncStatus('2')
                    elif fingerSyncStatus == "Already Synced":
                        fileObject.updateSyncStatus('0')
                    t.sleep(5)
                else:
                    t.sleep(5)
                dbObject.databaseClose(database)
            else:
                t.sleep(5)
        except Exception as e:
            print("Exception From : {}\n Exception Message: {}".format("syncronizationProcess",str(e)))
            fileObject.updateExceptionMessage("sasMain{syncronizationProcess}: ",str(e))
#            dbObject.databaseClose()
    
        
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
    print("Inside Function: {}".format("takefingerPrint"))
    x = False
    continueEnrollment = True
    try:
        while ( f.readImage() == False and x == False):
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT) # Checking For Time Out
            if (fileObject.readCurrentTask() == "5"): # Checking if Enrollment is Cancelled or Not
                continueEnrollment = False
                turnLEDON('R')
                turnOnBuzzer(0)
                break
            print("Flag For Device Response x: {}".format(x))
            print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
            turnLEDON('OFF')
            t.sleep(1)
            turnLEDON('W')
        print("Flag For Device Response x: {}".format(x))
        print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
        turnLEDON('OFF')
        return (x,continueEnrollment)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("takefingerPrint",str(e)))
        fileObject.updateExceptionMessage("sasMain{takefingerPrint}: ",str(e))
        continueEnrollment = False
        return (x,continueEnrollment)

def waitToRemoveFinger(f,currentDateTime):
    print("Inside Function: {}".format("waitToRemoveFinger"))
    x = False
    continueEnrollment = True
    try:
        while ( f.readImage() == True and x == False): # Check if the User is Still Keeping the Finger on the Sensor
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
            if (fileObject.readCurrentTask() == "5"):
                print("Device Current Task: {}".format(currentTask))
                continueEnrollment = False
                break
            print("Flag For Device Response x: {}".format(x))
            print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
            t.sleep(1)
        print("Finger Removed")
        print("Flag For Device Response x: {}".format(x))
        print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
        return (x,continueEnrollment)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("waitToRemoveFinger",str(e)))
        fileObject.updateExceptionMessage("sasMain{waitToRemoveFinger}: ",str(e))
        continueEnrollment = False
        return (x,continueEnrollment)
    
def waitForServerInstructionToCome(desiredCommand, currentDateTime):
    print("Inside Function: {}".format("waitForServerInstructionToCome"))
    x = False
    y = False
    try:
        currentDateTimeForResponse,currentTimeForResponse = checkCurrentDateTime() 
        while (1): # Waiting Untill Command is Received from the Server or Enrollment Cancelled or Enrollment Timeout or Response Timeout
            x = calculateTimeDifference(currentDateTime,ENROLLMENTTIMEOUT)
            currentTask = fileObject.readCurrentTask()
            print("Device Current Task: {}".format(currentTask))                      
            y = calculateTimeDifference(currentDateTimeForResponse,REQUESTTIMEOUT) # Checking for Response Timeout
            print("Flag For Server Response y: {}".format(y))
            print("Flag For Device Response x: {}".format(x))
            if (currentTask == desiredCommand or currentTask == '5' or x == True or y == True): # Command Received or Cancelled or Enrollment Timeout or Response Timeout
                break
            t.sleep(0.5)
        return (currentTask, x, y)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("waitToRemoveFinger",str(e)))
        fileObject.updateExceptionMessage("sasMain{waitForServerInstructionToCome}: ",str(e))
        y = True
        return (currentTask, x, y)
    
def enrollmentLEDIndicator(color):
    turnLEDON('OFF')
    if color == 'R':
        turnLEDON('R')
        turnOnBuzzer(0)
#        turnLEDON('OFF')
    elif color == 'G':
        turnLEDON('G')
        turnOnBuzzer(1)
#        t.sleep(1) # Wait for the User to Remove the Finger
#        turnLEDON('OFF')
        
    
def takeFingerprintToEnroll(f,currentDateTime,deviceId,uniqueId,requestId):
    print("Inside Function: {}".format("takeFingerprintToEnroll"))
    x = False # Flag to check Enrollment Timeout
    y = False # Flag to Check Response Timeout
    continueEnrollment = True # Flag to Check If Enrollment Process is Cancelled or Not
    print("Flag For Server Response y: {}".format(y))
    print("Flag For Device Response x: {}".format(x))
    print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
    try:
        x,continueEnrollment = takefingerPrint(f,currentDateTime)
        print("Flag For Device Response x: {}".format(x))
        print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
        if (x == False  and continueEnrollment == True): #If Enrollment is Not Timed Out and Enrollment is Not Cancelled
            print("Convert the Print")
            f.convertImage(0x01) #Save the Fingerprint to Sensor Buffer
            print("Image Converted")
            result = f.searchTemplate() # Search if the Template Already Exists or Not
            positionNumber = result[0]
            
            if ( positionNumber >= 0 ): # If Template Exists positonNumber will be > 0
                print("No Match Found")
#                sendPusherCommand(hardwareId,"FINGER_ALREADY_EXISTS",requestId) # Send Already Exists Command to the Server
                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"FINGER_ALREADY_EXISTS")
                return "Enrollment Cancelled"
            else:
#                sendPusherCommand(hardwareId,"FIRST_FINGER_TAKEN",requestId) # Send First Finger Taken Confirmation to the Server
                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"FIRST_FINGER_TAKEN")
                enrollmentLEDIndicator('G')
                print("First Finger Taken")
                
                x,continueEnrollment = waitToRemoveFinger(f,currentDateTime)
                print("Flag For Device Response x: {}".format(x))
                print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))    
                if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
#                    sendPusherCommand(hardwareId,"REMOVED1",requestId) # Send Removed Command To the Server First Time
                    apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"REMOVED1")
#                    turnLEDON('OFF')
                    turnLEDON('G+B')
                    t.sleep(1)
                    print("Removed Sent")
                    
                    currentTask, x, y = waitForServerInstructionToCome('3', currentDateTime)
                    
                    if (currentTask == "5"): # Enrollment Cancelled Check
                        return "Enrollment Cancelled"
                    
                    elif y == True: # Response Timeout Check
                        sendPusherCommand(hardwareId,"TIME_OUT",requestId) # Send Timeout Response to the Server
                        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                        print("Enrollment Timeout")
                        return "Request Time Out"
                    
                    elif x == False : # If Enrollment is Not Timed Out
                        x,continueEnrollment = takefingerPrint(f,currentDateTime)
                        print("Flag For Device Response x: {}".format(x))
                        print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))    
                        
                        if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                            f.convertImage(0x02)
                            if ( f.compareCharacteristics() == 0): # If First and Second Do Not Matche
#                                sendPusherCommand(hardwareId,"FINGERS_DO_NOT_MATCH",requestId) # Send Finger Not Matched to the Server
                                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"FINGERS_DO_NOT_MATCH")
                                print("Finger Do not match Second Time")
                                return "Finger Did Not Match Second Time"
                            
                            else:
                                print("Second Finger Taken")
#                                sendPusherCommand(hardwareId,"SECOND_FINGER_TAKEN",requestId) # Send Second Time Finger Taken To the Server
                                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"SECOND_FINGER_TAKEN")
                                enrollmentLEDIndicator('G')
                                
                                x,continueEnrollment = waitToRemoveFinger(f,currentDateTime)
                                print("Flag For Device Response x: {}".format(x))
                                print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
                                if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
#                                    sendPusherCommand(hardwareId,"REMOVED2",requestId)
                                    apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"REMOVED2")
#                                    turnLEDON('OFF')
                                    turnLEDON('G+B')
                                    t.sleep(1)
                                    
                                    currentTask, x, y = waitForServerInstructionToCome('4', currentDateTime)
                                    
                                    if (currentTask == "5"): # Enrollment Cancelled Check
                                        return "Enrollment Cancelled"
                                    elif y == True: # Response Timeout
#                                        sendPusherCommand(hardwareId,"TIME_OUT",requestId) # Send Timeout to the Server
                                        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                                        print("Enrollment Timeout")
                                        return "Request Time Out"
                                    elif x == False:
                                        
                                        x,continueEnrollment = takefingerPrint(f,currentDateTime)
                                        print("Flag For Device Response x: {}".format(x))
                                        print("Flag For Continue Enrollment Response continueEnrollment: {}".format(continueEnrollment))
                                        if (x == False  and continueEnrollment == True): # If Enrollment is Not Timed Out and Enrollment is Not Cancelled
                                            f.convertImage(0x01)
                                            if ( f.compareCharacteristics() == 0): # Check Finger Matched 
#                                                sendPusherCommand(hardwareId,"FINGERS_DO_NOT_MATCH",requestId) # Send Not Matched to the Server
                                                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"FINGERS_DO_NOT_MATCH")
                                                print("Finger Do not match Third Time")
                                                return "Finger Did Not Match Third Time"
                                            else:
                                                print("Finger Matched")
#                                                sendPusherCommand(hardwareId,"THIRD_FINGER_TAKEN",requestId) # Send Third Finger Taken to THe Server
                                                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"THIRD_FINGER_TAKEN")
                                                enrollmentLEDIndicator('G')
                                                return "Finger Matched"
                                        else:
#                                            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                            apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                                            return "Time Out"
                                    else:
#                                        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                                        return "Time Out"
                                else:
#                                    sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                                    apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                                    return "Time Out"   
                        else:
#                            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                            apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                            return "Time Out"
                    else:
#                        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                        return "Time Out"
                else:
#                    sendPusherCommand(hardwareId,"TIME_OUT",requestId)
                    apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
                    return "Time Out"
        else:
#            sendPusherCommand(hardwareId,"TIME_OUT",requestId)
            apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
            return "Time Out"
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("takeFingerprintToEnroll",str(e)))
        fileObject.updateExceptionMessage("sasMain{takeFingerprintToEnroll}: ",str(e))
#        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")
        return "Time Out"

def createNewTemplate(f,uniqueId,deviceId,dbObject,database):
    print("Inside Function: {}".format("createNewTemplate"))
    characterMatrix = f.downloadCharacteristics()
    matrix = ""
    for i in characterMatrix:
        matrix = matrix+ str(i)+ "-"
    receivedData = apiObject.getFingerId(uniqueId,matrix,deviceId)
    print("Received Data {}: ".format(receivedData))
    if receivedData[0] == "Success":
        f.storeTemplate(int(receivedData[1][0]),0x01)
        dbObject.insertNewEmployee(uniqueId, \
                                   receivedData[1][0], \
                                   database)
        print("Employee Added Successfully")
        return "1"
    else:
        return receivedData[0]
        
def enrollNewEmployee(f,deviceId,dbObject,database):
    global apiObject
    apiObject = sasAllAPI(2)
    print("Inside Function: {}".format("enrollNewEmployee"))
    currentDateTime,currentTime = checkCurrentDateTime()
    print("Current Datetime: {}".format(currentDateTime))
    print("Current time: {}".format(currentTime))
    uniqueId = fileObject.readEnrollingUserInfo()
    requestId = fileObject.readRequestId()
    print("UniqueId Received: {}".format(uniqueId))
#    print("Selected Company: {}".format(selectedCompany))
    print("Request ID: {}".format(requestId))
 
    try:
        fingerInput = takeFingerprintToEnroll(f,currentDateTime,deviceId,uniqueId,requestId)
        if fingerInput == "Finger Matched" :
            turnLEDON('G+B')
            status = createNewTemplate(f,uniqueId,deviceId,dbObject,database)
            print("Registration Status: {}".format(status))
            if status == "1":
#                sendPusherCommand(hardwareId,"REGISTED_SUCCESSFULLY",requestId)
                updateListOfUsedTemplates(f)
                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"REGISTED_SUCCESSFULLY")
                enrollmentLEDIndicator('G')
                fileObject.updateRequestId("0")
#                turnLEDON('OFF')
                print("Registered Successfuly")
                #GPIO INDICATOR
            else:
#                sendPusherCommand(hardwareId,"NOT_REGISTED_SUCCESSFULLY",requestId)
                apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"NOT_REGISTED_SUCCESSFULLY")
                enrollmentLEDIndicator('R')
                fileObject.updateRequestId("0")
#                turnLEDON('OFF')
                print("Registered Unsuccessfuly")
        else:
            enrollmentLEDIndicator('R')
#            turnLEDON('OFF')
            fileObject.updateRequestId("0")
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("enrollNewEmployee",str(e)))
        fileObject.updateExceptionMessage("sasMain{enrollNewEmployee}: ",str(e))
        enrollmentLEDIndicator('R')
#        fileObject.updateRequestId("0")
#        sendPusherCommand(hardwareId,"TIME_OUT",requestId)
        apiObject.replyPusherMessage(deviceId, hardwareId, uniqueId,"TIME_OUT")

def turnLEDON(color):
    print("Requested Color: {}".format(color))
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
        t.sleep(.4)
    else:
        t.sleep(.1)
        GPIO.output(buzzerPin, 0)
        t.sleep(.1)
        GPIO.output(buzzerPin, 1)
        t.sleep(.1)
    GPIO.output(buzzerPin, 0)
    
def createEventLogg(employeeCardorFingerNumber,attendanceFlag,dbObject,database):
    print("Inside Function: {}".format("createEventLogg"))
    currentDateTime,currentTime = checkCurrentDateTime()
    print("Current Datetime: {}".format(currentDateTime))
    print("Current time: {}".format(currentTime))
    if attendanceFlag == '2':
        employeeDetails = dbObject.getEmployeeDetailsFromCard(employeeCardorFingerNumber,database)
        print("Punched Employee ID: {}".format(employeeDetails))
        if employeeDetails == '0':
            print("No Card Record Found")
            dbObject.insertEventTime("0",\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     database)
            print("No Card Record Found")
            accessDenied()
#            turnLEDON('OFF') #OFF
        else :
            print("Card Record Found")
            GPIO.output(greenLightPin, 1)
            dbObject.insertEventTime(employeeDetails[0],\
                                     employeeCardorFingerNumber,\
                                     currentDateTime,\
                                     attendanceFlag,\
                                     database)
            print("Event Created Successfully")
            accessGranted()
#            turnLEDON('OFF') #OFF
    elif attendanceFlag == '1': #################################################Check For Secondary Address in event script######
        employeeDetails = dbObject.getEmployeeDetails(employeeCardorFingerNumber,database)
        print("Punched Employee ID: {}".format(employeeDetails))
        if employeeDetails != '0':
            print("Finger Record Found")
            dbObject.insertEventTime(employeeDetails[0], \
                                     employeeCardorFingerNumber, \
                                     currentDateTime, \
                                     attendanceFlag, \
                                     database)
            print("Event Created Successfully")
            accessGranted()
            return 1
        else:
            print("No Finger Record Found")
            accessDenied()
            return 0

def accessDenied():
    turnLEDON('R') #RED
    turnOnBuzzer(0)
#    t.sleep(.5)
#    turnLEDON('OFF') #OFF
    
def accessGranted():
    doorStatus(0)
    turnLEDON('G') #GREEN
    turnOnBuzzer(1)
#    t.sleep(.5)
#    turnLEDON('OFF') #OFF
    
def matchFingerPrint(f,dbObject,database):
    try:
        print("Inside Function: {}".format("matchFingerPrint"))
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        print("Position Number Found: {}".format(positionNumber))
        if (positionNumber == -1):
            print("No Finger Record Found")
            accessDenied()
        else:
            fingerFlag = createEventLogg(positionNumber,'1',dbObject,database)
            if fingerFlag == 0:
                f.deleteTemplate(positionNumber)
    except Exception as e:
        print("Exception From : {}\n Exception Message: {}".format("matchFingerPrint",str(e)))
        fileObject.updateExceptionMessage("sasMain{matchFingerPrint}",str(e))
    
def workWithFingerPrintSensor():
    global currentTask
    global syncStatus
    while True:
        try:
            f = configureFingerPrint()
            print("Connected With Fingerprint Sensor From workWithFingerPrintSensor")
            from sasDatabase import sasDatabase
            dbObject = sasDatabase()
            database = dbObject.connectDataBase()
            print("Connected With Database From workWithFingerPrintSensor")
            while True:
                turnLEDON('OFF')
                doorStatus(1)
                while (f.readImage() == False):
#                    print("Current workWithFingerPrintSensor Thread ID: {}".format(threading.current_thread()))
                    currentTask = fileObject.readCurrentTask()
                    syncStatus = fileObject.readSyncStatus()
                    print("Device Current Task: {}".format(currentTask))
                    print("Device Syncronization Request Flag: {}".format(syncStatus))
                    if (currentTask == '2' or syncStatus == '2'):
                        break
                    t.sleep(.01)
                lock.acquire()
                print("Inside Finger Recognition Part")
                currentTask = fileObject.readCurrentTask()
                if currentTask == '1'and syncStatus != '2':
                    fileObject.updateCurrentTask('6')
                    currentTask = '6'
                print("Modified Task is: {}".format(currentTask))    
                if currentTask == '6':
                    print("Inside Finger Match Part")
                    matchFingerPrint(f,dbObject,database)
                    fileObject.updateCurrentTask('1')                  
                elif currentTask == '2': # Check Command Script
                    deviceId = dbObject.getDeviceId(database)
                    print("Inside Finger Enrollment Part")
                    if deviceId != 0:
                        enrollNewEmployee(f,deviceId,dbObject,database)
                    ##########################################################################################
                    fileObject.updateCurrentTask('1')
                elif syncStatus == '2':
                    print("Inside Finger Sync Process")
                    syncUsersToSensor(f,dbObject,database)
                lock.release()
                t.sleep(1)
    #            print("A finger Is read")
        except Exception as e:
            print("Exception From : {}\n Exception Message: {}".format("matchFingerPrint",str(e)))
            fileObject.updateExceptionMessage("sasMain{workWithFingerPrintSensor}: ",str(e))
            os.system('sudo pkill -f sasMain.py')
            lock.release()
            
def readFromRFIDScanner():
    print("Inside Function: {}".format("readFromRFIDScanner"))
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
    
def workWithRFSensor():
    global currentTask
    while True:
        try:
            from sasDatabase import sasDatabase
            dbObject = sasDatabase()
            database = dbObject.connectDataBase()
            while True:
#                print("Current workWithRFSensor Thread ID: {}".format(threading.current_thread()))
                turnLEDON('OFF')
                doorStatus(1)
                rfScannerValue = readFromRFIDScanner()
                employeeCardNumber = int(rfScannerValue,16)
                print("Read Card Number: {}".format(employeeCardNumber))
                if len(rfScannerValue) < 10:
                    lock.acquire()
                    currentTask = fileObject.readCurrentTask()
                    if currentTask == '1':
                        fileObject.updateCurrentTask('7')
                        currentTask = '7'
                    if currentTask == '7':
                        print('Event for Card Number: {}'.format(employeeCardNumber))
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
    t.sleep(3600)
    apiObjectPrimary = sasAllAPI(1)
    if(apiObjectPrimary.checkServerStatus()):
        os.system("hwclock -w")
    if fileObject.readCurrentTask() != '1':
        while 1:
            print("Current functionKillProgram Thread ID: {}".format(threading.current_thread()))
            if fileObject.readCurrentTask() == '1':
                break
            t.sleep(1)
    os.system('sudo pkill -f sasMain.py')
        
if __name__ == '__main__':
    try:
        fingerPrint = threading.Thread(target = workWithFingerPrintSensor)
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
        
    