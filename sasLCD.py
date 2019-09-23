import liquidcrystal_i2c as LCD
import time as t

class sasLCD:

    lcd_columns = 20
    lcd_rows    = 4
    
    def __init__(self):
        import subprocess
        import re
        p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,)
        for i in range(0,9):
            line = str(p.stdout.readline())
            for match in re.finditer("[0-9][0-9]:.*[a-zA-Z0-9][a-zA-Z0-9]", line):
                address = match.group()
        if (len(address) > 0):
            addresses = address.split('-- ')
            i2cAddress = addresses[len(addresses)-1]
            self.lcd = LCD.LiquidCrystal_I2C(int(i2cAddress,16),1,numlines=self.lcd_rows)
        
    def printIfNoMatchFound(self):
        self.printClearScreen()
        self.lcd.printline(0 , "   ATTENDANCE MODE  ") 
        self.lcd.printline(2 , "    ACCESS DENIED   ")
        t.sleep(2)

    def printDeviceMaintanace(self):
        self.printClearScreen()
        self.lcd.printline(0 , "    DEVICE UNDER    ") 
        self.lcd.printline(1 , "    MAINTAINANCE    ")
        self.lcd.printline(3 , "  PLEASE TRY LATER  ")
        t.sleep(2)
        
    def printClearScreen(self):
        self.lcd.printline(0 , "                    ")
        self.lcd.printline(1 , "                    ")
        self.lcd.printline(2 , "                    ")
        self.lcd.printline(3 , "                    ")

    def printAfterSuccessfullEventLogg(self,currentTime,employeeDetails):
        self.printClearScreen()
        self.lcd.printline(0 , "ATTENDANCE DONE!!!! ")
##        msg = ""
##        if str(employeeDetails[4]) == '2':
##            if str(employeeDetails[3]) == "":
##                msg = "Ms. "+str(employeeDetails[2])
##            else:
##                msg = "Ms. "+str(employeeDetails[3])
##            
##        else:
##            if str(employeeDetails[3]) == "":
##                msg = "Mr. "+str(employeeDetails[2])
##            else:
##                msg = "Mr. "+str(employeeDetails[3])
                
        message = (str(employeeDetails[2])).upper()
        self.lcd.printline(1 , message)
        message = "ID: " + str(employeeDetails[0])
        self.lcd.printline(2 , message)
        message = "TIME: " + str(currentTime)
        self.lcd.printline(3 , message)
        t.sleep(2)

    def printAfterSuccessfullEventLoggButNoEmployeeID(self):
        self.printClearScreen()
        self.lcd.printline(0 , "   ATTENDANCE MODE  ") 
        self.lcd.printline(2 , "NO EMPLOYEE ID FOUND")
        t.sleep(2)

    def printSyncMessage(self):
        self.printClearScreen()
        self.lcd.printline(0 , "PLEASE WAIT........ ")
        self.lcd.printline(1 , "                    ")
        self.lcd.printline(2 , "  SYNCHRONIZATION   ")
        self.lcd.printline(3 , "    IN PROGRESS     ")
        #t.sleep(1)

    def printInitialMessage(self):
        #self.lcd.blink(False)
        # self.printClearScreen()
        self.lcd.printline(0 , " ATTENDANCE SYSTEM ")
        self.lcd.printline(1 , "SCAN FOR ATTENDANCE ")
        self.lcd.printline(2 , "        OR          ")
        self.lcd.printline(3 , "PRESS '#' TO ENROLL ")
        #t.sleep(1)

    def printPleaseWait(self):
        self.printClearScreen()
        self.lcd.printline(0 , " PLEASE WAIT...")
#        t.sleep(.2)

    def enrollmentMode(self):
        self.printClearScreen()
        self.lcd.printline(0 , "  ENROLLMENT MODE  ")

    def printEnrollemntGivePassword(self):
        self.enrollmentMode()
        self.lcd.printline(1 , "ENTER PIN=")
        self.lcd.printline(2 , "A=ENTER C=CANCEL")
        self.lcd.printline(3 , "B=BACKSPACE")
        self.lcd.setCursor(10,1)

    def printEnrollemntGiveEmployeeId(self):
        self.enrollmentMode()
        self.lcd.printline(1 , "EMPLOYEE ID=")
        self.lcd.printline(2 , "A=ENTER C=CANCEL")
        self.lcd.printline(3 , "B=BACKSPACE")
        self.lcd.setCursor(12,1)

    def printCompanyNames(self,companyList,printedCompany):
        self.printClearScreen()
        #self.enrollmentMode()
        self.lcd.printline(0 , "SELECT YOUR COMPANY ")
        line2 = 0
        line3 = 0
        messageLine2=""
        messageLine3=""
        companyNo = 1
        for company in companyList:
            if (20-line2) >= (len(company)+3):
                messageLine2 = messageLine2 + str(companyNo) + "." + company + " "
                line2 = line2 + (len(company)+3)
                companyNo = companyNo + 1
                printedCompany = printedCompany + 1
            elif (20-line3) >= (len(company)+2):
                messageLine3 = messageLine3 + str(companyNo) + "." + company + " "
                line3 = line3 + (len(company)+2)
                companyNo = companyNo + 1
                printedCompany = printedCompany + 1
            else:
                break
        self.lcd.printline(1 , messageLine2)
        self.lcd.printline(2 , messageLine3)
        self.lcd.printline(3 , "<<<'*' PRESS 'D'>>>")
        return printedCompany
                
    def printEmployeeId(self,idNumber):
        self.lcd.printstr(str(idNumber))

    def printPassword(self,pin):
        self.lcd.printstr(str(pin))

    def setLCDCursorForBackSpace(self,x,y):
        self.lcd.setCursor(x,y)
        self.lcd.printstr(" ")
        self.lcd.setCursor(x,y)

    def printValidEmployeeNotSuccess(self,flag,employeeId,x):
        self.enrollmentMode()
        if flag == "Invalid":
            msg = "  ID "+str(employeeId)+" NOT VALID"
            self.lcd.printline(2 , msg)
        elif flag == "Registered":
            msg = "  ID "+str(employeeId)+" REGISTERED"
            self.lcd.printline(2 , msg)        
        elif flag == "Server Down":
            self.lcd.printline(1 , "  LOST CONNECTION  ")
            self.lcd.printline(2 , "    WITH SERVER    ")
            self.lcd.printline(3 , "  TRY AGAIN LATER  ")
        elif x == '1':
            self.lcd.printline(2 , " REQUEST TIMED OUT ")
        t.sleep(2)

    def printPasswordResponse(self,flag,x):
        self.enrollmentMode()
        if flag == "Not Matched":
            msg = "    ACCESS DENIED   "
            self.lcd.printline(2 , msg)    
        elif flag == "Server Down":
            self.lcd.printline(1 , "  LOST CONNECTION  ")
            self.lcd.printline(2 , "    WITH SERVER    ")
            self.lcd.printline(3 , "  TRY AGAIN LATER  ")
        elif x == '1':
            self.lcd.printline(2 , " REQUEST TIMED OUT ")
        t.sleep(2)

    def printPutAnyFinger(self):
        self.enrollmentMode()
        self.lcd.printline(2 , "  PUT ANY FINGER  ")
        self.lcd.printline(3 , " WITHIN 2 MINUTES ")
        t.sleep(1)

    def printFingerAlreadyExists(self):
        self.enrollmentMode()
        self.lcd.printline(2 , "   FINGER ALREADY   ")
        self.lcd.printline(3 , "       EXISTS       ")
        t.sleep(2)

    def printRemoveAndPutSameFinger(self):
        self.enrollmentMode()
        self.lcd.printline(2 , "   REMOVE FINGER  ")
        t.sleep(2)
        self.enrollmentMode()
        self.lcd.printline(2 , "  PUT SAME FINGER ")
        self.lcd.printline(3 , " WITHIN 2 MINUTES ")
        t.sleep(1)
        
    def printWaitAfterGivingBothFingers(self):
        self.enrollmentMode()
        self.lcd.printline(2 , "  PLEASE WAIT...  ")
        t.sleep(1)

    def printTwoFingersDidNotMatched(self):
        self.enrollmentMode()
        self.lcd.printline(2 , " FINGER NOT MATCHED")
        self.lcd.printline(3 , "   PROCESS FAILED")
        t.sleep(2)

    def printSuccessEnrollmentMessage(self):
        self.enrollmentMode()
        self.lcd.printline(2 , "  FINGER ENROLLED  ")
        self.lcd.printline(3 , "   SUCCESSFULLY    ")
        t.sleep(2)

    def printUnsuccessEnrollmentMessage(self,receivedData):
        self.enrollmentMode()
        if receivedData == "Server Error":
            self.lcd.printline(1 , "  LOST CONNECTION  ")
            self.lcd.printline(2 , "    WITH SERVER    ")
            self.lcd.printline(3 , "  TRY AGAIN LATER  ")
        else:
            self.lcd.printline(2 , " ERROR HAS OCCURED ")
            self.lcd.printline(3 , "    TRY AGAIN      ")
        t.sleep(2)

    def timeOutMessage(self):
        self.enrollmentMode()
        self.lcd.printline(2 , " REQUEST TIMED OUT ")
        t.sleep(2)

    def printCompanyNotSelected(self,ch,x):
        self.enrollmentMode()
        if ch == 'C':
            self.lcd.printline(2 , "ENROLLMENT CANCELED")
        elif x == '1':
            self.lcd.printline(2 , " REQUEST TIMED OUT ")
        t.sleep(2)
        
    def printIDNotGivenOrTimeOutOrCanceled(self,ch,employeeId,x):
        self.enrollmentMode()
        if ch == 'C':
            self.lcd.printline(2 , "ENROLLMENT CANCELED")
        elif x == '1':
            self.lcd.printline(2 , " REQUEST TIMED OUT ")
        elif employeeId == "":
            self.lcd.printline(2 , "   ID NOT GIVEN    ")
        t.sleep(2)
        
    def printPasswordNotGivenOrTimeOutOrCanceled(self,ch,employeeId,x):
        self.enrollmentMode()
        if ch == 'C':
            self.lcd.printline(2 , "ENROLLMENT CANCELED")
        elif x == '1':
            self.lcd.printline(2 , " REQUEST TIMED OUT ")
        elif employeeId == "":
            self.lcd.printline(2 , "PASSWORD NOT GIVEN ")
        t.sleep(2)

    def printExceptionMessage(self,message):
        self.printClearScreen()
        self.lcd.printline(1 , message.upper())
        t.sleep(1)
