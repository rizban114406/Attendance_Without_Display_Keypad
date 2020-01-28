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
from sasDatabase import sasDatabase
dbObject = sasDatabase()
database = dbObject.connectDataBase()
#appId = '860616'
#key = 'de47d29a0309c4e2c87e'
#secret = '87b85c977153726607e7'

#appId = "924204"
#key = "6d2a9b43bfaaa2a13472"
#secret = "b66493c060ed6685c9cc"
#cluster = "mt1"

#pusherSend = push.Pusher(appId, key, secret)
#pusherReceive = pysher.Pusher(key)
from sasGPIO import sasGPIO
gpioObject = sasGPIO()
from sasFile import sasFile
fileObject = sasFile()
fileObject.updateRequestId("0")
fileObject.updateCurrentTask("1")

from sasAllAPI import sasAllAPI
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

#pusherReceive.connection.bind('pusher:connection_established', connect_handler)
#pusherReceive.connect()

#def sendPusherCommand(hardwareId,command,requestId):
#    deviceInfoData = {"hardwareId" : hardwareId,\
#                      "command"    : command,\
#                      "requestId"  : requestId}
#    commandToSend = json.dumps(deviceInfoData)
#    pusherSend.trigger('enroll-feed-channel', 'enroll-feed-event', commandToSend)

#appId = "924204"
#key = "6d2a9b43bfaaa2a13472"
#secret = "b66493c060ed6685c9cc"
#cluster = "mt1"
while True:
    appId, key, secret, cluster = fileObject.readPusherAppKey()
    print("Pusher appId: {}, Key: {}, secret: {}, cluster: {}".format(appId, key, secret, cluster))
    if len(appId) > 5:
        print("Pusher appId: {}, Key: {}, secret: {}, cluster: {}".format(appId, key, secret, cluster))
        pusherReceive = pysher.Pusher(key)
        pusherReceive.connection.bind('pusher:connection_established', connect_handler)
        pusherReceive.connect()
        while True:
            time.sleep(1)
            deviceId = dbObject.getDeviceId(database)
            if (output != ""):
                print("Output Message From Pusher {}".format(output))
                localOutput = output  
        #        hardwareId = "asdasdas"
                print("Received Message From Server localoutput: {}".format(localOutput))
                hardwareIdRequested = localOutput['data']['hardwareid']
                commandRequested = localOutput['data']['command']
                task = fileObject.readCurrentTask()
                requestId = fileObject.readRequestId()
                if(hardwareId == hardwareIdRequested):
                    apiObjectSecondary = sasAllAPI(2)
                    if (commandRequested == "ONLINE_FLAG"):
                        if task == '1':
                            if (localOutput['data']['inventory'] == 0):
                                apiObjectSecondary.confirmDeviceStatus(hardwareId,0)
                                gpioObject.blinkDevice()
                            elif (localOutput['data']['inventory'] == 1):
                                apiObjectPrimary.confirmDeviceStatus(hardwareId,0)
                                gpioObject.blinkDevice()
                        else:
                            if (localOutput['data']['inventory'] == 0):
                                apiObjectSecondary.confirmDeviceStatus(hardwareId,1)
                            elif (localOutput['data']['inventory'] == 1):
                                apiObjectPrimary.confirmDeviceStatus(hardwareId,1)
                        output = ""
                
                    elif (task == "1" and commandRequested == "ENROLL_USER"):
        #                fileObject.updateRequestId(localOutput['requestId'])
                        fileObject.updateEnrollingUserInfo(localOutput['data']['user_id'])
                        fileObject.updateCurrentTask('2')
                        print("Take Info of the Enrolling User")
                        flag = apiObjectSecondary.replyPusherMessage(deviceId, hardwareId, localOutput['data']['user_id'],"ENROLL_COMMAND_RECEIVED")
                        print("Response Flag: {}".format(flag))
                        output = ""
        #            
                    elif (task == "2" and commandRequested == "TAKE_SECOND_FINGER"):
                        fileObject.updateCurrentTask('3')
                        output = ""
        #                
                    elif (task == "3" and commandRequested == "TAKE_THIRD_FINGER"):
                        fileObject.updateCurrentTask('4')
                        output = ""
        #                
                    elif ((task == "2" or task == "3" or task == "4")\
                          and (commandRequested == "CANCEL_ENROLLMENT")):
                        fileObject.updateCurrentTask('5')
                        uniqueId = fileObject.readEnrollingUserInfo()
                        apiObjectSecondary.replyPusherMessage(deviceId, hardwareId, uniqueId,"ENROLLMENT_CANCELLED")
                        output = ""   
                            
                    if (commandRequested == "SYNC_DEVICE"):
                        if (fileObject.readSyncStatus() == '0'):
                            fileObject.updateSyncStatus('1')
                        output = ""
                    
                    if (commandRequested == "REBOOT_DEVICE"):
                        if (fileObject.readCurrentTask() == '1'):
                            command = "/usr/bin/sudo /sbin/shutdown -r now"
                            import subprocess
                            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                            process.communicate()[0]
                        output = ""
                            
                    if (commandRequested == "UPDATE_DEVICE_INFO"):
                        from sasDatabase import sasDatabase
                        dbObject = sasDatabase()
                        database = dbObject.connectDataBase()
                        if (localOutput['data']['inventory'] == 1 and \
                            dbObject.checkAddressUpdateRequired(1, database) == 0):
                            dbObject.resetUpdatedRequiredStatus(1, database)
                            deviceId = dbObject.getDeviceId(database)
                            apiObjectPrimary.confirmUpdateRequest(deviceId)
                            
                            
                        elif (localOutput['data']['inventory'] == 0 and \
                            dbObject.checkAddressUpdateRequired(2, database) == 0):
                            dbObject.resetUpdatedRequiredStatus(2, database)
                            deviceId = dbObject.getDeviceId(database)
                            apiObjectSecondary.confirmUpdateRequest(deviceId)
                        output = "" 
                    output = ""
    else:
        print("Pusher appId: {}, Key: {}, secret: {}, cluster: {}".format(appId, key, secret, cluster))
        print("No Pusher Key Found")
        time.sleep(5)
