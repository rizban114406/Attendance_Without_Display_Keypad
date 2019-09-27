import json
import requests
from sasFile import sasFile
from sasDatabase import sasDatabase
fileObject = sasFile()
class sasAllAPI:
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()
    ipAddress = ""
    baseURL = ""
    mainURL = ""
    
    def __init__(self):
        desiredDetails = self.dbObject.getAllConfigurationDetails(self.database)
        self.ipAddress = desiredDetails[1]
        self.baseURL = desiredDetails[2]
        self.mainURL = "http://" + self.ipAddress + self.baseURL
        self.dbObject.databaseClose(self.database)

    def checkServerStatus(self,employeeId,selectedCompany):
        try:
            mainURL = self.mainURL + "valid_employee"
            payload = {"employee"  : employeeId, \
                       "companyid" : selectedCompany}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload, timeout = 40)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success' and output['code'] == "1"):
                return str(output['data'])
            elif(output['status'] == 'failed' and output['code'] == "2"):
                return "Registered"
            elif(output['status'] == 'failed' and output['code'] == "0"):
                return "Invalid"    
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{checkServerStatus}",str(e))
            return "Server Down"

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
                receivedData.append(output['data']['employeeid'])
                receivedData.append(output['data']['uniqueid'])
                receivedData.append(output['data']['firstname'])
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
            dataToSend = json.dumps(receivedData)
            payload = {"data"     : dataToSend,\
                       "deviceid" : deviceId}
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 200)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == 'success'):
                if output['sync_status'] == 0:
                    fileObject.updateConfigUpdateStatus('0')
                return output
            else:
                return "Some Thing Is Wrong"
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getCardDataToSync}",str(e))
            return "Server Error"

    def authenticatePassword(self,password,deviceId):
        try:
            mainURL = self.mainURL + "check_device_auth"
            payload = {"deviceid" : deviceId, \
                       "password"  : password }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success"):
                return "Matched"
            else:
                return "Not Matched"
        
        except Exception as e:
            #print str(e)
            fileObject.updateExceptionMessage("sasAllAPI{authenticatePassword}",str(e))
            return "Server Error"

    def updateDevice(self,deviceId,ipAddress,osVersion,sync_status):
        try:
            mainURL = self.mainURL + "update_device"
            payload = {"deviceid"  : deviceId,   \
                       "ip"        : ipAddress, \
                       "osversion" : osVersion,  \
                       "syncstatus": sync_status }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success" and output['code'] == "1"):
                return '1'
            else:
                return '0'
        
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{updateDevice}",str(e))
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

    def getCompanyDetails(self,deviceId):
        try:
            mainURL = self.mainURL + "get_company"
            payload = {"deviceid" : deviceId }
            print("Data To Be Sent: {}".format(payload))
            r = requests.post(mainURL, data = payload,timeout = 10)
            print("Data Received {}".format(r.content))
            output = json.loads(r.content)
            if (output['status'] == "success"):
                return output['data']
            else:
                return '0'       
        except Exception as e:
            fileObject.updateExceptionMessage("sasAllAPI{getCompanyDetails}",str(e))
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

    def getConfigDetails(self,deviceId):
        try:
            mainURL = self.mainURL + "get_config"
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
            fileObject.updateExceptionMessage("sasAllAPI{getConfigDetails}",str(e))
            return "Server Error"

        
                

