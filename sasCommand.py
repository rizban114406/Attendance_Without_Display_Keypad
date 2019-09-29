import time as t
import json
import sys
import time
import pysher
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)

from sasFile import sasFile
fileObject = sasFile()

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
pusher = pysher.Pusher('de47d29a0309c4e2c87e')

def my_func(*args, **kwargs):
    output = json.loads(args[0])
    print(output['hardware_id'])
    print(output['user_id'])
    

def connect_handler(data):
    channel = pusher.subscribe('enroll-channel')
    channel.bind('enroll-event', my_func)

pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

while True:
    time.sleep(1)



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
