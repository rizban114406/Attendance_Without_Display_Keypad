# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 21:54:47 2019

@author: Rizban Hussain
"""

from sasDatabase import sasDatabase
dbObject = sasDatabase()
database = dbObject.connectDataBase()

from sasAllAPI import sasAllAPI
apiObjectPrimary = sasAllAPI(1)

dbObject.resetUpdatedRequiredStatus(1, database)
deviceId = dbObject.getDeviceId(database)
apiObjectPrimary.confirmUpdateRequest(deviceId)