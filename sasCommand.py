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
apiObjectSecondary = sasAllAPI(2)
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
                    if (localOutput['inventory'] == 0):
                        apiObjectSecondary.confirmDeviceStatus(hardwareId,0)
                    elif (localOutput['inventory'] == 1):
                        apiObjectPrimary.confirmDeviceStatus(hardwareId,0)
                else:
                    if (localOutput['inventory'] == 0):
                        apiObjectSecondary.confirmDeviceStatus(hardwareId,1)
                    elif (localOutput['inventory'] == 1):
                        apiObjectPrimary.confirmDeviceStatus(hardwareId,1)
                if (localOutput == output):
                    output = ""
        
            elif (task == "1" and commandRequested == "ENROLL_USER"):
#                fileObject.updateRequestId(localOutput['requestId'])
                fileObject.updateEnrollingUserInfo(localOutput['user_id'])
                fileObject.updateCurrentTask('2')
                print("Take Info of the Enrolling User")
                apiObjectSecondary.replyPusherMessage(hardwareId, localOutput['user_id'],"ENROLL_COMMAND_RECEIVED")
                if (localOutput == output):
                    output = ""
#            
            elif (task == "2" and commandRequested == "TAKE_SECOND_FINGER"):
                fileObject.updateCurrentTask('3')
                if (localOutput == output):
                    output = ""
#                
            elif (task == "3" and commandRequested == "TAKE_THIRD_FINGER"):
                fileObject.updateCurrentTask('4')
                if (localOutput == output):
                    output = ""
#                
            elif ((task == "2" or task == "3" or task == "4")\
                  and (commandRequested == "CANCEL_ENROLLMENT")):
                fileObject.updateCurrentTask('5')
                uniqueId = fileObject.readEnrollingUserInfo()
                apiObjectSecondary.replyPusherMessage(hardwareId, uniqueId,"ENROLLMENT_CANCELLED")
                if (localOutput == output):
                    output = ""   
                    
            if (commandRequested == "SYNC_DEVICE"):
                if (fileObject.readSyncStatus() == '0'):
                    fileObject.updateSyncStatus('1')
                if (localOutput == output):
                    output = ""
                    
            if (commandRequested == "UPDATE_DEVICE_INFO"):
                from sasDatabase import sasDatabase
                dbObject = sasDatabase()
                database = dbObject.connectDataBase()
                if (localOutput['inventory'] == 1 and \
                    dbObject.checkAddressUpdateRequired(1, database) == 0):
                    dbObject.resetUpdatedRequiredStatus(1, database)
                    deviceId = dbObject.getDeviceId(database)
                    apiObjectPrimary.confirmUpdateRequest(deviceId)
                    
                elif (localOutput['inventory'] == 0 and \
                    dbObject.checkAddressUpdateRequired(2, database) == 0):
                    dbObject.resetUpdatedRequiredStatus(2, database)
                if (localOutput == output):
                    output = ""    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
