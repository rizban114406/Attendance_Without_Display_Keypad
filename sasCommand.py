import time as t
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

appId = '860616'
key = 'de47d29a0309c4e2c87e'
secret = '87b85c977153726607e7'

pusherSend = push.Pusher(appId, key, secret)
pusherReceive = pysher.Pusher(key)

from sasFile import sasFile
fileObject = sasFile()

from sasAllAPI import sasAllAPI
apiObject = sasAllAPI()

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
    output = json.loads(args[0])
#    task = fileObject.readDesiredTask()
#    requestId = fileObject.readRequestId()
#    print()
#    if (output['command'] == "ONLINE_FLAG" and \
#        output['hardwareid'] == hardwareId):
#        if task == '1':
#            apiObject.confirmDeviceStatus(hardwareId)
#            print("Sent")
#        else:
#            print("DEVICE IS BUSY")
        
#    elif (task == "1" and output['hardware_id'] == hardwareId \
#                      and output['command'] == "ENROLL_USER" \
#                      and requestId == "0"):
#        fileObject.updateDesiredTask('2')
#        fileObject.updateRequestId(output['request_id'])
#                    
#    elif (task == "2" and output['hardware_id'] == hardwareId \
#                      and output['command'] == "TAKE_SECOND_FINGER"
#                      and output['request_id'] == requestId):
#        fileObject.updateDesiredTask('3')
#        
#    elif (task == "3" and output['hardware_id'] == hardwareId \
#                      and output['command'] == "TAKE_THIRD_FINGER"
#                      and output['request_id'] == requestId):
#        fileObject.updateDesiredTask('4')
#        
#    elif (task != "1" and output['hardware_id'] == hardwareId \
#                      and output['command'] == "CANCEL_ENROLLMENT"
#                      and output['request_id'] == requestId):
#        fileObject.updateDesiredTask('8')
#        
#    elif (task != "1" and output['hardware_id'] == hardwareId \
#                      and output['command'] == "TIME_OUT"
#                      and output['request_id'] == requestId):
#        fileObject.updateDesiredTask('8')
        
#    elif (task != "1" and output['hardware_id'] == hardwareId):
#        
#
#            
#    print(output)
#    print(output['hardware_id'])
#    print(output['user_id'])
    

def connect_handler(data):
    channel = pusherReceive.subscribe('enroll-channel')
    channel.bind('enroll-event', my_func)

pusherReceive.connection.bind('pusher:connection_established', connect_handler)
pusherReceive.connect()

while True:
    time.sleep(1)
    print("At The Start")
    global output
    if (output != ""):
        localOutput = output  
        hardwareId = "asdasdas"
        command = localOutput['command']
#        print(hardwareId)
#        print(command)
        task = fileObject.readDesiredTask()
        requestId = fileObject.readRequestId()
        if (command == "ONLINE_FLAG" and \
            hardwareId == hardwareId):
            if task == '1':
                apiObject.confirmDeviceStatus(hardwareId)
                print(localOutput)
                print(output)
                if (localOutput == output):
                    output = ""
            else:
                print("DEVICE IS BUSY")
        elif (task == "1" and localOutput['hardwareId'] == hardwareId \
                          and localOutput['command'] == "ENROLL_USER" \
                          and requestId == "0"):
            fileObject.updateDesiredTask('2')
            fileObject.updateRequestId(output['requestId'])
            deviceInfoData = {"hardwareId"   : hardwareId,\
                              "command"  : "ENROLL_COMMAND_RECEIVED",\
                              "requestId"    : output['requestId']}
            commandToSend = json.dumps(deviceInfoData)
            print(commandToSend)
            pusherSend.trigger('enroll-feed-channel', 'enroll-feed-event', commandToSend)
            output = ""



#if __name__ == '__main__':
#    command = '1'
#    fileObject.updateDesiredTask('1')
#    while True:
#      try:
#        ch = digit()
#        print("Pressed Key is {}".format(ch))
#        if (ch == '#'):
#            fileObject.updateDesiredTask('2')
#            while 1:
#                task = fileObject.readDesiredTask()
#                if task == '1':
#                    break
#                else:
#                    pass
#                t.sleep(1)
#        t.sleep(1)
#      except Exception as e:
#          fileObject.updateExceptionMessage("sasCommand",str(e))
#          t.sleep(5)
