# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 21:54:47 2019

@author: Rizban Hussain
"""
import json
from sasDatabase import sasDatabase
dbObject = sasDatabase()
database = dbObject.connectDataBase()
from sasFile import sasFile
fileObject = sasFile()
from sasAllAPI import sasAllAPI
apiObjectPrimary = sasAllAPI(1)

dbObject.resetUpdatedRequiredStatus(1, database)
deviceId = dbObject.getDeviceId(database)
apiObjectPrimary.confirmUpdateRequest(deviceId)
osVersion = fileObject.readCurrentVersion()
def generateDataToUpdateInfor():
    deviceInfo = dbObject.getAllDeviceInfo(database)
    urls = dbObject.getAllConfigurationDetails(2,database)
    existingEthernetSettings = fileObject.readCurrentEthernetSettings().split('-')
    gsmFlag = fileObject.readGSMStatus()
    wifiNetworks = dbObject.getWifiConfigs(database)
    wifisettings = []
    wifisettings.append({"ssid" : "AqualinkLTD",\
                         "password" : "aqualink@321",\
                         "priority" : 1})
#    for wifi in wifiNetworks:
#        wifisettings.append({"ssid" : wifi[0],\
#                             "password" : wifi[1],\
#                             "priority" : wifi[2]})
    staticIpSettings = {"ip" : existingEthernetSettings[1],\
                        "mask" : existingEthernetSettings[2],\
                        "gateway" : existingEthernetSettings[3]}
    
    ethernetSettings = {"obtainauto" : existingEthernetSettings[0],\
                        "static" : staticIpSettings}
    
    networkSettings = {"ethernet" : ethernetSettings,\
                       "wifi" : wifisettings,\
                       "gsm" : gsmFlag}
    
    deviceInfoToSend = {"id" : deviceInfo[2],\
                  "uniqueid" : deviceInfo[1],\
                  "osversion" : osVersion,\
                  "devicename" : deviceInfo[4],\
                  "company" : deviceInfo[8],\
                  "address" : deviceInfo[6],\
                  "subaddress" : deviceInfo[6],\
                  "baseurl" : urls[0],\
                  "suburl" : urls[1],\
                  "networksettings" : networkSettings}
    dataToSend = {"data" : deviceInfoToSend}
    print("Device Updated Info: {}".format(dataToSend))
    return dataToSend
#dbObject.createTableWifiSettings(database)
dbObject.setUpdatedRequiredStatus(2, database)
dataToSend2 = generateDataToUpdateInfor()
dataToSend = json.dumps(dataToSend2)
payload = {"data" : dataToSend}
print("Data To Be Sent: {}".format(payload))