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
        self.ipAddress = desiredDetails[1]
        self.baseURL = desiredDetails[2]
        self.mainURL = "http://" + self.ipAddress + self.baseURL
        dbObject.databaseClose(database)

    def checkServerStatus(self):
        try:
            mainURL = self.mainURL + "server_heartbit"
            r = requests.get(mainURL,timeout = 5)
            print("Data Received {}".format(r.content))
            status = r.status_code
            if (status == 200):
                return 1
            else:
                return 0
        except Exception as e:
            print("Exception Message: {}".format(str(e)))
            return 0

    def getFingerId(self,uniqueId,matrix,selectedCompany,deviceId):
        try:
            receivedData = []
            mainURL = self.mainURL + "fingerprint_enrollment"
            payload = {"uniqueid"     : uniqueId, \
                       "fingermatrix" : matrix , \
                       "deviceid"     : deviceId, \
                       "companyid"    : selectedCompany}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload, timeout = 40)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                receivedData.append(output['data']['fingernumber'])
                return ("Success",receivedData)
            else:
                return ("No","")
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getFingerId}",str(e))
            return ("Server Error","")

    def sendEventData(self,mainData):
        try:
            mainURL = self.mainURL + "device_data"
            dataToSend = json.dumps(mainData,sort_keys = True)
            payload = {"data" : dataToSend}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 40)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return "Success"
            else:
                return "Not Successfull"
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{sendEventData}",str(e))
            return str(e)
        
    def getTime(self):
        try:
            mainURL = self.mainURL + "get_time"
            r = requests.post(mainURL,timeout = 4)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output['data']
            else:
                return "Not Successfull"
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getTime}",str(e))
            return "Not Successfull"

    def getDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "fingerprint_sync"
            dataToSend = json.dumps(receivedData)
            payload = {"data"     : dataToSend,\
                       "deviceid" : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output
            else:
                return "Some Thing Is Wrong"       
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getDataToSync}",str(e))
            return "Server Error"

    def getCardDataToSync(self,receivedData,deviceId):
        try:
            mainURL = self.mainURL + "rfid_sync"
            print(mainURL)
            dataToSend = json.dumps(receivedData)
            payload = {"data"     : dataToSend,\
                       "deviceid" : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return output
            else:
                return "Some Thing Is Wrong"
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getCardDataToSync}",str(e))
            return "Server Error"

    def getDeviceInfo(self,deviceId):
        try:
            mainURL = self.mainURL + "get_device"
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['status'] == "success" and output['code'] == "1"):
                return output['data']
            else:
                return '0'
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getDeviceInfo}",str(e))
            return "Server Error"

    def createDevice(self,hardwareId,osVersion):
        try:
            mainURL = self.mainURL + "create_device"
            payload = {"hardwareid" : hardwareId, \
                       "osversion"  : osVersion }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == "1"):
                return output['data']
            else:
                return '0'   
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{createDevice}",str(e))
            return "Server Error"
        
    def checkUpdateRequest(self,deviceId):
        try:
            mainURL = self.mainURL + "check_update_request"
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['code'] == 1):
                return 1
            elif (output['code'] == 0):
                return 0
            else:
                return 2   
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{checkUpdateRequest}: ",str(e))
            return 2
        
    def confirmUpdateRequest(self,deviceId):
        try:
            mainURL = self.mainURL + "confirm_update_request"
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['code'] == 1):
                return 1
            else:
                return 0   
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{confirmUpdateRequest}: ",str(e))
            return 0
        
    def confirmSyncStatusReceived(self,hardwareId):
        try:
            mainURL = self.mainURL + "update_sync_status"
            payload = {"hardwareid" : hardwareId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['status'] == "success"):
                return '1'
            else:
                return '0'
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{confirmDeviceStatus}: ",str(e))
            return "Server Error"
        
    def getAllConfigurationDetails(self, deviceId):
        try:
            mainURL = self.mainURL + "get_device_info"
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 3)
            output = json.loads(r.content)
            print("Data Received {}".format(r.content))
            if (output['status'] == "success" and output['code'] == 1):
                return output['data']
            elif output['code'] == 2:
                return '1'
            return '0'
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{confirmDeviceStatus}: ",str(e))
            return "Server Error"
        
    def updateDeviceInfoToServer(self,receivedData):
        try:
            mainURL = self.mainURL + "update_device_info"
            dataToSend = json.dumps(receivedData)
            payload = {"data" : dataToSend}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                return 1
            else:
                return 0       
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getDataToSync}",str(e))
            return 0
                

