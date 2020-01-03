import pusher as push
import json
import sys
import time
import pysher
import logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)

#appId = '860616'
#key = 'de47d29a0309c4e2c87e'
#secret = '87b85c977153726607e7'

appId = "924204"
key = "6d2a9b43bfaaa2a13472"
secret = "b66493c060ed6685c9cc"
cluster = "mt1"

pusherSend = push.Pusher(appId, key, secret)
pusherReceive = pysher.Pusher(key)

from sasFile import sasFile
fileObject = sasFile()
fileObject.updateRequestId("0")
fileObject.updateCurrentTask("1")

from sasAllAPI import sasAllAPI
apiObject = sasAllAPI(2)
apiObjectPrimary = sasAllAPI(1)

output = ""

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

def my_func(*args, **kwargs):
    global output
    print(output)
    output = json.loads(args[0])

def connect_handler(data):
    channel = pusherReceive.subscribe(hardwareId)
    channel.bind('my-event', my_func)

pusherReceive.connection.bind('pusher:connection_established', connect_handler)
pusherReceive.connect()

def sendPusherCommand(hardwareId,command,requestId):
    deviceInfoData = {"hardwareId" : hardwareId,\
                      "command"    : command,\
                      "requestId"  : requestId}
    commandToSend = json.dumps(deviceInfoData)
    pusherSend.trigger('enroll-feed-channel', 'enroll-feed-event', commandToSend)

while True:
    time.sleep(1)
    print("Waiting For Message")
    if (output != ""):
        print("Output Message From Pusher {}".format(output))
        localOutput = output  
        hardwareId = "asdasdas"
        print("Received Message From Server localoutput: {}".format(localOutput))
        hardwareIdRequested = localOutput['hardwareid']
        commandRequested = localOutput['command']
        task = fileObject.readCurrentTask()
        requestId = fileObject.readRequestId()
        if(hardwareId == hardwareIdRequested):
            if (commandRequested == "ONLINE_FLAG"):
                if task == '1':
                    apiObject.confirmDeviceStatus(hardwareId,0)
                else:
                    apiObject.confirmDeviceStatus(hardwareId,1)
                if (localOutput == output):
                    output = ""
        
            elif (task == "1" and commandRequested == "ENROLL_USER"):
#                fileObject.updateRequestId(localOutput['requestId'])
                fileObject.updateEnrollingUserInfo(localOutput['user_id'])
                fileObject.updateCurrentTask('2')
                print("Take Info of the Enrolling User")
                sendPusherCommand(hardwareId,"ENROLL_COMMAND_RECEIVED",localOutput['requestId'])          
                output = ""
#            
#        elif (task == "2" and localOutput['hardwareId'] == hardwareId \
#                          and localOutput['command'] == "TAKE_SECOND_FINGER"
#                          and localOutput['requestId'] == requestId):
#            fileObject.updateCurrentTask('3')
#            if (localOutput == output):
#                output = ""
#                
#        elif (task != "1" and localOutput['hardwareId'] == hardwareId \
#                          and localOutput['command'] == "TAKE_THIRD_FINGER"
#                          and localOutput['requestId'] == requestId):
#            fileObject.updateCurrentTask('4')
#            if (localOutput == output):
#                output = ""
#                
#        elif (task == "3" and localOutput['hardwareId'] == hardwareId \
#                          and localOutput['command'] == "CANCEL_ENROLLMENT"
#                          and localOutput['requestId'] == requestId):
#            fileObject.updateCurrentTask('5')
#            sendPusherCommand(hardwareId,"ENROLLMENT_CANCELLED",localOutput['requestId'])
#            if (localOutput == output):
#                output = ""        
#        elif (task == "3" and localOutput['hardwareId'] == hardwareId \
#                          and localOutput['command'] == "TIME_OUT"
#                          and localOutput['requestId'] == requestId):
#            fileObject.updateCurrentTask('5')
#            if (localOutput == output):
#                output = ""     
#        if (localOutput['hardwareId'] == hardwareId \
#            and localOutput['command'] == "SYNC_DEVICE"):
#            if (fileObject.readSyncConfStatus() == '0'):
#                status = apiObject.confirmSyncStatusReceived(hardwareId)
#                if (status == '1'):
#                    fileObject.updateSyncConfStatus('1')
#            else:
#                sendPusherCommand(hardwareId,"DEVICE_IS_BUSY","0")
#            if (localOutput == output):
#                output = ""
#        if (localOutput['hardwareId'] == hardwareId \
#            and localOutput['command'] == "UPDATE_DEVICE_INFO"):
#            from sasDatabase import sasDatabase
#            dbObject = sasDatabase()
#            database = dbObject.connectDataBase()
#            if (localOutput['requestFrom'] == '1' and \
#                dbObject.checkAddressUpdateRequired(1, database) == 0):
#                dbObject.resetUpdatedRequiredStatus(1, database)
#                deviceId = dbObject.getDeviceId(database)
#                apiObjectPrimary.confirmUpdateRequest(deviceId)
#            else:
#                sendPusherCommand(hardwareId,"DEVICE_IS_BUSY","0")
#            if (localOutput['requestFrom'] == '2' and \
#                dbObject.checkAddressUpdateRequired(2, database) == 0):
#                dbObject.resetUpdatedRequiredStatus(2, database)
#            else:
#                sendPusherCommand(hardwareId,"DEVICE_IS_BUSY","0")
#            if (localOutput == output):
#                output = ""    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
