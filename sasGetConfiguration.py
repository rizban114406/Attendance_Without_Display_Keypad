import urllib
import tarfile
from shutil import copyfile
import os
import struct
from sasDatabase import sasDatabase
from sasAllAPI import sasAllAPI
from sasFile import sasFile
fileObject = sasFile()
import commands
#import time as t

def myCommands():
    try:
        try:
            os.system('sudo rm /var/lib/mysql/ibdata1')
        except Exception as e:
            fileObject.updateExceptionMessage("sasGetConfiguration{myCommands 1}",str(e))
        try:
            os.system('sudo rm /var/lib/mysql/AttendanceSystem/*')
        except Exception as e:
            fileObject.updateExceptionMessage("sasGetConfiguration{myCommands 2}",str(e))
        try:
            os.system('sudo rm /var/lib/mysql/ib_logfile*')
        except Exception as e:
            fileObject.updateExceptionMessage("sasGetConfiguration{myCommands 3}",str(e))
        os.system('sudo python initializeDatabase.py')
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{myCommands 4}",str(e))
try:
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()
except Exception as e:
    fileObject.updateExceptionMessage("sasGetConfiguration{DB Error}",str(e))
    myCommands()
    dbObject = sasDatabase()
    database = dbObject.connectDataBase()

apiObject = sasAllAPI()

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

def getIpAddress():
    ip =  commands.getoutput('hostname -I')
    return ip

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
            fileObject.updateExceptionMessage("sasGetConfiguration{updateToNewCode 1}",str(e))
        except tarfile.TarError as e:
            fileObject.updateExceptionMessage("sasGetConfiguration{updateToNewCode 2}",str(e))
        os.system('chmod 755 *')
        if os.path.exists("/root/rc.local"):
            copyfile("/root/rc.local", "/etc/rc.local")
        return 1
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{updateToNewCode}",str(e))
        return 0

def restart():
    dbObject.databaseClose(database)
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    process.communicate()[0]

def getNetworkConfiguration(deviceId):
    try:
        configDetails = dbObject.getAllConfigurationDetails(database)
        configDetailsUpdated = apiObject.getConfigDetails(deviceId)
        if configDetailsUpdated != '0' and configDetailsUpdated != "Server Error":
            if str(configDetailsUpdated['base_URL']) != str(configDetails[1]):
                dbObject.updateBaseUrl(str(configDetailsUpdated['base_URL']),database)
            if str(configDetailsUpdated['sub_URL']) != str(configDetails[2]):
                dbObject.updateSubUrl(str(configDetailsUpdated['sub_URL']),database)
            if float(configDetailsUpdated['os_version']) > float(configDetails[0]):
                codeUpdateFlag = updateToNewCode(str(configDetailsUpdated['code_name']),\
                                                 str(configDetailsUpdated['code_URL']))
                if codeUpdateFlag == 1:
                    dbObject.updateOSVersion(float(configDetailsUpdated['os_version']),database)
                    restart()            
            return '1'
        else:
            return configDetailsUpdated
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{getNetworkConfiguration}",str(e))
        return configDetailsUpdated

def getCompanyDetails(deviceId):
    try:
        allCompanies = apiObject.getCompanyDetails(deviceId)
        #print allCompanies
        if allCompanies != '0' and allCompanies != "Server Error":
            dbObject.createTableCompanyListTable(database)
            for company in allCompanies:
                dbObject.insertIntoCompanyListTable(company['companyid'],company['shortname'],database)
            return '1'
        else:
            return '0'
    except Exception as e:
        fileObject.updateExceptionMessage("sasGetConfiguration{getCompanyDetails}",str(e))
        return '0'
    
def sendConfirmationToServer(deviceId,ipAddress):
    osVersion = dbObject.getOSVersion(database)
    updateStatus = apiObject.updateDevice(deviceId,ipAddress,osVersion,'1')
    if updateStatus == '1':
        #print "Updating Flag"
        fileObject.updateConfigUpdateStatus('1')
        return '1'
    else:
        return '0'

def updateHeartBitURL():
    configDetails = dbObject.getAllConfigurationDetails(database)
    url = "http://" + configDetails[1] + configDetails[2] + "server_heartbit"
    fileObject.updateHearBitURL(url)

def checkIPAddress(deviceId,ipAddress):
    desiredDetails = dbObject.getAllDeviceInfo(database)
    if (ipAddress != desiredDetails[6]):
        status = sendConfirmationToServer(deviceId,ipAddress)
        if status == '1':
            dbObject.updateIPAddress(ipAddress,database)

if __name__ == '__main__':
    try:
        deviceId = dbObject.getDeviceId(database)
        print(deviceId)
        hardwareId = getHardwareId()
        osVersion = dbObject.getOSVersion(database)
        print(osVersion)
        ipAddress = getIpAddress()
        if deviceId == 0:
            deviceInfo = apiObject.createDevice(hardwareId,osVersion)
            if (deviceInfo != '0' and deviceInfo != "Server Error"):
                dbObject.insertIntoDeviceInfoTable(deviceInfo,ipAddress,database)
                deviceId = int(deviceInfo['id'])
                print("DeviceId {}".format(deviceId))
            if deviceId != 0:
                networkConfigStatus = getNetworkConfiguration(deviceId)
                companyListStatus = getCompanyDetails(deviceId)
                print("networkConfigStatus: {} companyListStatus {}".format(networkConfigStatus,companyListStatus))
                if networkConfigStatus == '1' and companyListStatus == '1':
                    updateHeartBitURL()
                    sendConfirmationToServer(deviceId,ipAddress)
        else:
            readUpdateStatus = fileObject.readConfigUpdateStatus()
            if readUpdateStatus == '0':
                deviceInfo = apiObject.getDeviceInfo(deviceId)
                print("DeviceId {}".format(deviceId))
                if (deviceInfo != '0' and deviceInfo != "Server Error"):
                    dbObject.updateDeviceInfoTable(deviceInfo,ipAddress,database)
                    networkConfigStatus = getNetworkConfiguration(deviceId)
                    companyListStatus = getCompanyDetails(deviceId)
                    print("networkConfigStatus: {} companyListStatus {}".format(networkConfigStatus,companyListStatus))
                    if networkConfigStatus == '1' and companyListStatus == '1':
                        updateHeartBitURL()
                        sendConfirmationToServer(deviceId,ipAddress)
            else:
                checkIPAddress(deviceId,ipAddress)
        dbObject.databaseClose(database)
    
    except Exception as e:
        dbObject.databaseClose(database)
        fileObject.updateExceptionMessage("sasGetConfiguration{__main__}",str(e))