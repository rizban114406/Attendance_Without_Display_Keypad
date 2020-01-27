import json
import requests
from sasFile import sasFile
from sasDatabase import sasDatabase
fileObject = sasFile()
class sasAllAPI:
    def __init__(self, locationType):
        dbObject = sasDatabase()
        database = dbObject.connectDataBase()
        desiredDetails = dbObject.getAllConfigurationDetails(locationType,database)
        self.ipAddress = desiredDetails[0]
        self.baseURL = desiredDetails[1]
        self.mainURL = "http://" + self.ipAddress + self.baseURL
        dbObject.databaseClose(database)

    def checkServerStatus(self):
        try:
            mainURL = self.mainURL + "check_server_status"
            print("Sending URL: {}".format(mainURL))
            r = requests.get(mainURL,timeout = 1)
            print("Data Received {}\n".format(r.content))
            status = r.status_code
            if (status == 200):
                return 1
            else:
                return 0
        except Exception as e:
            print("Exception Message: {}, URL: {}".format(str(e),mainURL))
            return 0

    def getFingerId(self,uniqueId,matrix,deviceId):
        try:
            receivedData = []
            mainURL = self.mainURL + "enroll_new_finger"
            print("Sending URL: {}".format(mainURL))
            payload = {"uniqueid"     : uniqueId, \
                       "fingermatrix" : matrix , \
                       "deviceid"     : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload, timeout = 40)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                receivedData.append(output['data']['fingernumber'])
                return ("Success",receivedData)
            else:
                return ("No","")
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{getFingerId}",exceptionMessage)
            return ("Server Error","")

    def sendEventData(self,mainData):
        try:
            mainURL = self.mainURL + "device_event_data"
            print("Sending URL: {}".format(mainURL))
            dataToSend = json.dumps(mainData,sort_keys = True)
            payload = {"data" : dataToSend}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 40)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return "Success"
            else:
                return "Not Successfull"
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{sendEventData}",exceptionMessage)
            return str(e)
        
#    def getTime(self):
#        try:
#            mainURL = self.mainURL + "get_time"
#            r = requests.post(mainURL,timeout = 4)
#            print("Data Received {}".format(r.content))
#            output = json.loads(r.content)
#            if (output['status'] == 'success'):
#                return output['data']
#            else:
#                return "Not Successfull"
#        except Exception as e:
#            fileObject.updateExceptionMessage("sasAllAPI{getTime}",str(e))
#            return "Not Successfull"

    def getDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "sync_fingerprint_info"
            print("Sending URL: {}".format(mainURL))
            dataToSend = json.dumps(receivedData)
            payload = {"data"     : dataToSend,\
                       "deviceid" : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output
            else:
                return "Some Thing Is Wrong"       
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{getDataToSync}",exceptionMessage)
            return "Server Error"

    def getCardDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "sync_rf_info"
            print("Sending URL: {}".format(mainURL))
            dataToSend = json.dumps(receivedData)
            payload = {"data"     : dataToSend,\
                       "deviceid" : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output
            else:
                return "Some Thing Is Wrong"
        
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{getCardDataToSync}",exceptionMessage)
            return "Server Error"
        
    def createDevice(self,hardwareId,osVersion):
        try:
            mainURL = self.mainURL + "create_device"
            print("Sending URL: {}".format(mainURL))
            payload = {"hardwareid" : hardwareId, \
                       "osversion"  : osVersion }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == 1):
                return output['data']
            else:
                return '0'   
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{createDevice}",exceptionMessage)
            return "Server Error"
        
    def checkUpdateRequest(self,deviceId):
        try:
            mainURL = self.mainURL + "check_update_request"
            print("Sending URL: {}".format(mainURL))
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['code'] == 1):
                return 1
            elif (output['code'] == 0):
                return 0
            else:
                return 2   
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{checkUpdateRequest}",exceptionMessage)
            return 2
        
    def confirmUpdateRequest(self,deviceId):
        try:
            mainURL = self.mainURL + "confirm_update_request"
            print("Sending URL: {}".format(mainURL))
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['code'] == 1):
                return 1
            else:
                return 0   
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{confirmUpdateRequest}",exceptionMessage)
            return 0
        
    def confirmSyncStatusReceived(self,hardwareId):
        try:
            mainURL = self.mainURL + "update_sync_status"
            print("Sending URL: {}".format(mainURL))
            payload = {"hardwareid" : hardwareId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}\n".format(r.content))
            if (output['status'] == "success"):
                return '1'
            else:
                return '0'
        
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{confirmSyncStatusReceived}",exceptionMessage)
            return "Server Error"
        
    def getAllConfigurationDetails(self, deviceId):
        try:
            mainURL = self.mainURL + "get_device_info"
            print("Sending URL: {}".format(mainURL))
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == 1):
                return output['data']
            elif output['code'] == 2:
                return '1'
            return '0'
        
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{getAllConfigurationDetails}",exceptionMessage)
            return "Server Error"
        
    def updateDeviceInfoToServer(self,receivedData):
        try:
            mainURL = self.mainURL + "update_device_info"
            print("Sending URL: {}".format(mainURL))
            dataToSend = json.dumps(receivedData)
            payload = {"data" : dataToSend}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}\n".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return 1
            else:
                return 0       
        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{updateDeviceInfoToServer}",exceptionMessage)
            return 0
        
    def confirmDeviceStatus(self,hardwareId,flag):
        try:
            mainURL = self.mainURL + "change_device_status"
            print("Sending URL: {}".format(mainURL))
            payload = {"hardwareid" : hardwareId,\
                       "flag" : flag}
            print("Data To Be Sent: {}\n".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['status'] == "success"):
                return '1'
            else:
                return '0'

        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{confirmDeviceStatus}",exceptionMessage)
            return "Server Error"
    
    def replyPusherMessage(self, deviceId, hardwareId, userId, command):
        try:
            mainURL = self.mainURL + "enroll_finger"
            mainData = {"deviceid"   : deviceId,\
                        "user_id"    : int(userId),\
                        "hardwareid" : hardwareId,\
                        "command"    : command}
            print("Sending URL: {}".format(mainURL))
            print("Sending Data: {}".format(mainData))
            dataToSend = json.dumps(mainData)
            payload = {"data" : dataToSend}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}\n".format(r.content))
            if (output['status'] == "success"):
                return 1
            else:
                return 0

        except Exception as e:
            exceptionMessage = str(e) + "\n" + "URL: " + mainURL + "\n" + "Data: " + str(payload) 
            fileObject.updateExceptionMessage("sasAllAPI{replyPusherMessage}",exceptionMessage)
            return 0
    

