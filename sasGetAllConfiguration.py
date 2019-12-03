# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 22:38:17 2019

@author: User
"""

from sasDatabase import sasDatabase
import commands
from sasFile import sasFile
fileObject = sasFile()
from sasAllAPI import sasAllAPI
apiObjectPrimary = sasAllAPI(1)
apiObjectSecondary = sasAllAPI(2)

def getHardwareId():
    cpuserial = ""
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                cpuserial = line[10:26]
        f.close()
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{getHardwareId}",str(e))
        cpuserial = "Error"
    return cpuserial

def getIpAddress():
    ip =  commands.getoutput('hostname -I')
    return ip

hardwareId = getHardwareId()
osVersion = fileObject.readCurrentVersion()

def setWIFINetworkConfiguration(wifiSettings):
    try: 
        lines = fileObject.readWifiSettings()
        dbObject.createTableWifiSettings(database)
        for settings in wifiSettings:
            lines.insert(len(lines),"network={\n")
            ssid = "ssid="+ '"' + settings["ssid"] + '"' + "\n"
            lines.insert(len(lines), ssid)
            password = "psk="+ '"' + settings["password"] + '"' + "\n"
            lines.insert(len(lines), password)
            lines.insert(len(lines),"key_mgmt=WPA-PSK\n")
            priority = "priority="+ '"' + settings["priority"] + '"' + "\n"
            lines.insert(len(lines), priority)
            lines.insert(len(lines), "}\n")
            dbObject.insertIntoWifiSettingsTable(settings["ssid"], settings["password"], settings["priority"], database)
        fileObject.writeWifiSettings(lines)
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{setWIFINetworkConfiguration}: ",str(e))
        return 0
        
def setEthernetConfiguration(staticIPInfo):
    try:
        lines = fileObject.readEthernetSettings()
        i = lines.index('#profile static_eth0\n')
        if staticIPInfo["obtainauto"] == '1':
            del lines[i+1:]
        else:
            staticIP = "static ip_address="+ staticIPInfo["static"]["ip"] + '/' + staticIPInfo["static"]["mask"] + "\n"
            lines.insert(i+1, staticIP)
            staticIP = "static routers="+ staticIPInfo["static"]["gateway"] + "\n"
            lines.insert(i+2, staticIP)
            del lines[i+3:]
        fileObject.writeEthernetSettings(lines)
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{setEthernetConfiguration}: ",str(e))
        return 0
    
try:
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()
except Exception as e:
    fileObject.updateExceptionMessage("sasGetALLConfiguration{DB Error}: ",str(e))
#    myCommands()
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()    

if __name__ == '__main__':
    deviceInfoRowNum = dbObject.countDeviceInfoTable(database)
    if deviceInfoRowNum == 0:
        if(apiObjectPrimary.checkServerStatus() == 1):
            ipAddress = getIpAddress()
            receivedData = apiObjectPrimary.createDevice(hardwareId,osVersion)
            if receivedData != '0' and receivedData != "Server Error":
                dbObject.insertIntoDeviceInfoTable(hardwareId,receivedData['id'],osVersion,ipAddress)
            else:
                print("Device Entry Not Successful")
    else:
        deviceId = dbObject.getDeviceId(database)
        if (dbObject.checkAddressUpdateRequired(1, database)):
            if(apiObjectPrimary.checkServerStatus()):
                requiredDetils = apiObjectPrimary.getAllConfigurationDetails(deviceId)
                if requiredDetils != '0' and requiredDetils != "Server Error":
                    deviceName = requiredDetils['devicename']
                    companyId = requiredDetils['companyid']
                    address = requiredDetils['address']
                    subaddress = requiredDetils['subaddress']
                    baseUrl = requiredDetils['baseurl']
                    subUrl = requiredDetils['suburl']
                    networkSettings = requiredDetils['networksettings']
                    ethernetSetings = setEthernetConfiguration(networkSettings['ethernet'])
                    wifiSettings = setWIFINetworkConfiguration(networkSettings['wifi'])
                    if (dbObject.checkSecondaryAddressAvailable(database)):
                        dbObject.updateConfigurationTable(baseUrl,subUrl,database)
                    else:
                        dbObject.insertIntoConfigurationTable(baseUrl,subUrl,database)
                    deviceInfoUpdateStatus = dbObject.updateDeviceInfoTable(deviceName, address, subaddress, ipAddress, companyId, database)
                    if (deviceInfoUpdateStatus):
                        dbObject.resetServerUpdatedStatus(2)
        elif (dbObject.checkAddressUpdateRequired(2, database)):
            if(apiObjectSecondary.checkServerStatus()):
                requiredDetils = apiObjectSecondary.getAllConfigurationDetails(deviceId)
                if requiredDetils != '0' and requiredDetils != "Server Error":
                    deviceName = requiredDetils['devicename']
                    companyId = requiredDetils['companyid']
                    address = requiredDetils['address']
                    subaddress = requiredDetils['subaddress']
#                    baseUrl = requiredDetils['baseurl']
#                    subUrl = requiredDetils['suburl']
                    networkSettings = requiredDetils['networksettings']
                    ethernetSetings = setEthernetConfiguration(networkSettings['ethernet'])
                    wifiSettings = setWIFINetworkConfiguration(networkSettings['wifi'])
#                    if (dbObject.checkSecondaryAddressAvailable(database)):
#                        dbObject.updateConfigurationTable(baseUrl,subUrl,database)
#                    else:
#                        dbObject.insertIntoConfigurationTable(baseUrl,subUrl,database)
                    deviceInfoUpdateStatus = dbObject.updateDeviceInfoTable(deviceName, address, subaddress, ipAddress, companyId, database)
                    if (deviceInfoUpdateStatus):
                        dbObject.resetServerUpdatedStatus(1)
        elif (dbObject.checkServerUpdateStatus(1, database)):
            deviceDetails = dbObject.getAllDeviceInfo(database)
            serverInfo = dbObject.getSecondaryAddressInfo(database)
            
            
        
            
                        
                    
                    
                
        
    