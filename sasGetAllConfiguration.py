# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 22:38:17 2019

@author: User
"""
from sasFile import sasFile
fileObject = sasFile()

def setWIFINetworkConfiguration(wifiSettings):
    try: 
        lines = fileObject.readWifiSettings()
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

if __name__ == '__main__':
    
    