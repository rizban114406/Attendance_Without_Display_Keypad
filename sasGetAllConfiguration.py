# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 22:38:17 2019

@author: User
"""
import urllib
import tarfile
from shutil import copyfile
import os
import struct
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

def restart():
    dbObject.databaseClose(database)
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.communicate()[0]

def updateToNewCode(deviceCodeName,deviceCodeURL):
    
    downloadURL = "http://" + deviceCodeURL + deviceCodeName
    try:
        testfile = urllib.URLopener()     
        testfile.retrieve(downloadURL, deviceCodeName)       
        try:
            tar = tarfile.open(deviceCodeName)
            tar.extractall()
            tar.close()
        except struct.error as e:
            fileObject.updateExceptionMessage("sasGetAllConfiguration{updateToNewCode 1}",str(e))
        except tarfile.TarError as e:
            fileObject.updateExceptionMessage("sasGetAllConfiguration{updateToNewCode 2}",str(e))
        os.system('chmod 755 *')
        if os.path.exists("/root/rc.local"):
            copyfile("/root/rc.local", "/etc/rc.local")
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{updateToNewCode}",str(e))
        return 0

def setWIFINetworkConfiguration(wifiSettings):
    try:
        isChangeRequired = 0
        print("New Wifi Settings: {}".format(wifiSettings))
        index = 0
        for settings in wifiSettings:
            print(settings)
            print(dbObject.checkWifiConfigsChange(settings["ssid"],\
                                               settings["password"],\
                                               settings["priority"],\
                                               database))
            if(dbObject.checkWifiConfigsChange(settings["ssid"],\
                                               settings["password"],\
                                               settings["priority"],\
                                               database)):
                del wifiSettings[index]
                continue
            else:
                isChangeRequired = 1
                break      
        if isChangeRequired == 1:
            lines = fileObject.readWifiSettings()
            dbObject.createTableWifiSettings(database)
            i = lines.index('}\n')
            for settings in wifiSettings:
                lines.insert(i+1,"network={\n")
                ssid = "ssid="+ '"' + settings["ssid"] + '"' + "\n"
                lines.insert(i+2, ssid)
                password = "psk="+ '"' + settings["password"] + '"' + "\n"
                lines.insert(i+3, password)
                lines.insert(i+4,"key_mgmt=WPA-PSK\n")
                priority = "priority=" + str(settings["priority"]) + "\n"
                lines.insert(i+5, priority)
                lines.insert(i+6, "}\n")
                i = i + 6
                dbObject.insertIntoWifiSettingsTable(settings["ssid"], \
                                                     settings["password"], \
                                                     settings["priority"], \
                                                     database)
            del lines[i+1:]
            fileObject.writeWifiSettings(lines)
            print("Wifi Settings: {}".format(lines))
            return 2
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{setWIFINetworkConfiguration}: ",str(e))
        return 0
        
def setEthernetConfiguration(staticIPInfo):
    try:
        existingEthernetSettings = fileObject.readCurrentEthernetSettings().split('-')
        print("Existing Ethernet Settings: {}".format(existingEthernetSettings))
        isChangeRequired = 0
        if staticIPInfo["obtainauto"] == '1':
            if staticIPInfo["obtainauto"] != existingEthernetSettings[0]:
                isChangeRequired = 1
        
        elif staticIPInfo["obtainauto"] == '0':
            if staticIPInfo["static"]["ip"] != existingEthernetSettings[1] or \
               staticIPInfo["static"]["mask"] != existingEthernetSettings[2] or \
               staticIPInfo["static"]["gateway"] != existingEthernetSettings[3]:
                  isChangeRequired = 1
        
        if isChangeRequired == 1:
            lines = fileObject.readEthernetSettings()
            i = lines.index('#profile static_eth0\n')
            if staticIPInfo["obtainauto"] == '1':
                currentEthernetSettings = "1-0-0-0"
                del lines[i+1:]
            else:
                staticIP = "static ip_address="+ staticIPInfo["static"]["ip"] + '/' + staticIPInfo["static"]["mask"] + "\n"
                lines.insert(i+1, staticIP)
                staticGateway = "static routers="+ staticIPInfo["static"]["gateway"] + "\n"
                lines.insert(i+2, staticGateway)
                currentEthernetSettings = "0-" + staticIPInfo["static"]["ip"] +\
                                           "-" + staticIPInfo["static"]["mask"] +\
                                           "-" + staticIPInfo["static"]["gateway"]
                del lines[i+3:]
            print("Updated Ethernet Settings: {}".format(existingEthernetSettings))
            fileObject.writeCurrentEthernetSettings(currentEthernetSettings)
            fileObject.writeEthernetSettings(lines)
            print("Ethernet Settings: {}".format(lines))
            return 2
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{setEthernetConfiguration}: ",str(e))
        return 0
    
try:
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()
except Exception as e:
    fileObject.updateExceptionMessage("sasGetALLConfiguration{DB Error}: ",str(e))
    
def checkForFirmwareUpdate(runningOsVersion, deviceCodeUrl, deviceCodeName):
    if float(runningOsVersion) > float(osVersion):
        codeUpdateFlag = updateToNewCode(str(deviceCodeName),\
                                         str(deviceCodeUrl))
        if codeUpdateFlag == 1:
            fileObject.updateCurrentVersion(runningOsVersion)
            restart()
            
def checkForChangeinDeviceInfo(requiredDetils,deviceInfo):
    try:
        ipAddress = getIpAddress()
        print("Existing Device Info: {}".format(deviceInfo))
        print("Change In Device Info: {}".format(requiredDetils))
        isChangeRequired = 0
        if (requiredDetils['devicename'] is not None and requiredDetils['devicename'] != deviceInfo[4]):
            isChangeRequired = 1
        if (requiredDetils['address'] is not None and requiredDetils['address'] != deviceInfo[5]):
            isChangeRequired = 1
        if (requiredDetils['subaddress'] is not None and requiredDetils['subaddress'] != deviceInfo[6]):
            isChangeRequired = 1
        if (requiredDetils['companyid'] is not None and requiredDetils['companyid'] != int(deviceInfo[8])):
            isChangeRequired = 1
        if isChangeRequired == 1:
            dbObject.updateDeviceInfoTable(requiredDetils['devicename'],\
                                           requiredDetils['address'],\
                                           requiredDetils['subaddress'],\
                                           ipAddress, \
                                           requiredDetils['companyid'],\
                                           osVersion,\
                                           database)
            return 2
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{checkForChangeinDeviceInfo}: ",str(e))
        return 0
    
def checkForServerAddressInfo(requiredDetils):
    try:
        print("Change In Device Server Info: {}".format(requiredDetils))
        if (requiredDetils['baseurl'] is not None and requiredDetils['baseurl'] is not None):    
            if (dbObject.checkSecondaryAddressAvailable(database)):
                confDetails = dbObject.getAllConfigurationDetails(2,database)
                print("Device Current Server Info: {}".format(confDetails))
                isChangeRequired = 0
                if (requiredDetils['baseurl'] != confDetails[0]):
                    isChangeRequired = 1
                if (requiredDetils['suburl'] != confDetails[1]):
                    isChangeRequired = 1
                if isChangeRequired == 1:
                    dbObject.updateConfigurationTable(requiredDetils['baseurl'],\
                                                      requiredDetils['suburl'],\
                                                      database)
                    return 2
            else:
                dbObject.insertIntoConfigurationTable(requiredDetils['baseurl'],\
                                                      requiredDetils['suburl'],\
                                                      database)
                return 2
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetAllConfiguration{checkForServerAddressInfo}: ",str(e))
        return 0
    
def generateDataToUpdateInfor(deviceInfo,urls):
    existingEthernetSettings = fileObject.readCurrentEthernetSettings().split('-')
    gsmFlag = fileObject.readGSMStatus()
    wifiNetworks = dbObject.getWifiConfigs(database)
    wifisettings = []
    for wifi in wifiNetworks:
        wifisettings.append({"ssid" : wifi[1],\
                             "password" : wifi[2],\
                             "priority" : wifi[3]})
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

osVersion = fileObject.readCurrentVersion()
if __name__ == '__main__':
    if(apiObjectPrimary.checkServerStatus() == 1 or apiObjectSecondary.checkServerStatus() == 1):
        hardwareId = getHardwareId()
        deviceInfoRowNum = dbObject.countDeviceInfoTable(database)
        print("Device Row Count: {}".format(deviceInfoRowNum))
        if deviceInfoRowNum == 0:
            if(apiObjectPrimary.checkServerStatus() == 1):
                ipAddress = getIpAddress()
                receivedData = apiObjectPrimary.createDevice(hardwareId,osVersion)
                print("Received Data From Create Device: {}".format(receivedData))
                if receivedData != '0' and receivedData != "Server Error":
                    dbObject.insertIntoDeviceInfoTable(hardwareId,receivedData['id'],osVersion,ipAddress,database)
                    print("New Device is inserted Successfully")
                else:
                    print("Device Entry Not Successful")
        else:
            while True:
                deviceId = dbObject.getDeviceId(database)
                deviceInfo = dbObject.getAllDeviceInfo(database)
                print("Device Info: {}".format(deviceInfo))
                if (dbObject.checkAddressUpdateRequired(1, database)): # If ant Changes are made then this returns 1
                    if(apiObjectPrimary.checkServerStatus()):
                        requiredDetils = apiObjectPrimary.getAllConfigurationDetails(deviceId)
                        print("Configuration Details From Server: {}".format(requiredDetils))
                        if requiredDetils == '1':
                            dbObject.setUpdatedRequiredStatus(1,database)
                        elif requiredDetils != '0' and requiredDetils != "Server Error":
                            if ((requiredDetils['devicecodeurl'] is not None) and (requiredDetils['devicecodename'] is not None)):
                                checkForFirmwareUpdate(requiredDetils['osversion'],\
                                                       requiredDetils['devicecodeurl'],\
                                                       requiredDetils['devicecodename'])
                                
                            deviceInfoUpdateStatus = checkForChangeinDeviceInfo(requiredDetils, deviceInfo)
                            configInfoUpdateStatus = checkForServerAddressInfo(requiredDetils)
                            networkSettings = requiredDetils['networksettings']
                            ethernetSetings = setEthernetConfiguration(networkSettings['ethernet'])
                            wifiSettings = setWIFINetworkConfiguration(networkSettings['wifi'])
                            print("deviceInfoUpdateStatus: {}, configInfoUpdateStatus: {}, \
                                  ethernetSetings: {}, wifiSettings: {}".format(deviceInfoUpdateStatus,configInfoUpdateStatus,\
                                  ethernetSetings,wifiSettings))
                            if (deviceInfoUpdateStatus == 2 or configInfoUpdateStatus == 2\
                                or ethernetSetings == 2 or wifiSettings == 2):
                                dbObject.resetServerUpdatedStatus(2,database)
                            if (deviceInfoUpdateStatus != 0 and configInfoUpdateStatus != 0\
                                and ethernetSetings != 0 and wifiSettings != 0):
                                dbObject.setUpdatedRequiredStatus(1,database)
               
                elif (dbObject.checkAddressUpdateRequired(2, database)):
                    if(apiObjectSecondary.checkServerStatus()):
                        requiredDetils = apiObjectSecondary.getAllConfigurationDetails(deviceId)
                        print("Configuration Details From Server: {}".format(requiredDetils))
                        if requiredDetils != '0' and requiredDetils != "Server Error":
                            deviceInfoUpdateStatus = checkForChangeinDeviceInfo(requiredDetils, deviceInfo)
        #                    configInfoUpdateStatus = checkForServerAddressInfo(requiredDetils)
                            networkSettings = requiredDetils['networksettings']
                            ethernetSetings = setEthernetConfiguration(networkSettings['ethernet'])
                            wifiSettings = setWIFINetworkConfiguration(networkSettings['wifi'])
                            print("deviceInfoUpdateStatus: {}, ethernetSetings: {}, \
                                  wifiSettings: {}".format(deviceInfoUpdateStatus,\
                                  ethernetSetings,wifiSettings))
                            if (deviceInfoUpdateStatus == 2 \
                                or ethernetSetings == 2 or wifiSettings == 2):#or configInfoUpdateStatus == 2\
                                dbObject.resetServerUpdatedStatus(1,database)
                            if (deviceInfoUpdateStatus != 0 \
                                and ethernetSetings != 0 and wifiSettings != 0):#and configInfoUpdateStatus != 0\
                                dbObject.setUpdatedRequiredStatus(2,database)
                                
                elif (dbObject.checkServerUpdateStatus(1, database)):
                    serverInfo = dbObject.getAllConfigurationDetails(2,database)
                    dataToSend = generateDataToUpdateInfor(deviceInfo,serverInfo)
                    dataSendingFlag = apiObjectPrimary.updateDeviceInfoToServer(dataToSend)
                    print("dataSendingFlag: {}".format(dataSendingFlag))
                    if dataSendingFlag == 1:
                        dbObject.setServerUpdatedStatus(1,database)
                        
                elif (dbObject.checkServerUpdateStatus(2, database)):
                    serverInfo = dbObject.getAllConfigurationDetails(2,database)
                    if serverInfo[0] != '':
                        dataToSend = generateDataToUpdateInfor(deviceInfo,serverInfo)
                        dataSendingFlag = apiObjectPrimary.updateDeviceInfoToServer(dataToSend)
                        print("dataSendingFlag: {}".format(dataSendingFlag))
                        if dataSendingFlag == 1:
                            dbObject.setServerUpdatedStatus(2,database)
                    else:
                        dbObject.setServerUpdatedStatus(2,database)
                else:
                    break