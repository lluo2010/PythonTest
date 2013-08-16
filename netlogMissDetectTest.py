#coding=utf-8
import fileinput
import sys
import datetime
import os

MAX_MISS_INTEVAL = 5 #minutes

POWER_TYPE = 3
CRCS_TYPE_INDEX = 2
CRCS_OPERATOR_INDEX = 13
Time_Format = "%Y-%m-%d %H:%M:%S.%f" 
class  CRCSAnalyze(object):
    def __init__(self, strCRCSPath):
        self.crcsPath = strCRCSPath
        self.deviceOn = 0;
        self.noCRCSRecordList = [] 
        self.noProxyNetlogRecordList = []
        self.strUser = "Unknown"
        self.totalCRCSMissDuration = 0
        self.totalNetlogMissDuration = 0
    def initRestartCheck(self,powerTime,batteryValue): 
        self.hasCRCS = 0
        self.hasProxyNetlog = 0
        self.preBatteryValue = batteryValue
        self.strPrePowerTime = powerTime
                                
    def analyze(self): 
        self.deviceOn = 0 
        self.initRestartCheck("",-1) 
        self.noCRCSRecordList = [] 
        self.noProxyNetlogRecordList = [] 
        for crcsLine in fileinput.input(self.crcsPath): 
            crcsList = self.splitCRCSLine(crcsLine) 
            if fileinput.isfirstline():
                self.strUser = crcsList[1].strip()
            if crcsList: 
                nType = self.getCRCSType(crcsList) 
                if nType == POWER_TYPE: 
                    strPowerType = crcsList[4].strip() 
                    if strPowerType=="battery": 
                        self.handleBatteryCRCS(crcsList) 
                    elif strPowerType=="device_on": 
                        self.deviceOn = 1 
                        self.preBatteryValue = -1
                else:
                    self.hasCRCS = 1 
                    if self.isNetlogStartWithProxy(crcsList)==1:
                        self.hasProxyNetlog = 1
        self.printResult()
        
    def handleBatteryCRCS(self,crcsInfo): 
        powerValue = int(crcsInfo[5].strip()) 
        powerTime = crcsInfo[0].strip() 
        #first battery 
        if self.preBatteryValue<0: 
            self.initRestartCheck(powerTime,powerValue) 
            self.deviceOn = 0 
            return 
        if  self.deviceOn== 0 and abs(powerValue-self.preBatteryValue)>=1 and self.isOutTimeRange(self.strPrePowerTime,powerTime): 
            if self.hasCRCS==0: 
                #print "there's no CRCS from %s to %s" %(strprePowerTime,powerTime) 
                #self.noCRCSRecordList.append((self.strPrePowerTime,powerTime))
                self.addTimeInterval2List(self.noCRCSRecordList,self.strPrePowerTime,powerTime)
            if self.hasProxyNetlog==0: 
                #print "there's no netlog start with proxy_ from %s to %s" %(self.strPrePowerTime,powerTime) 
                #self.noProxyNetlogRecordList.append((self.strPrePowerTime,powerTime))
                self.addTimeInterval2List(self.noProxyNetlogRecordList,self.strPrePowerTime,powerTime) 
            self.initRestartCheck(powerTime,powerValue)
    def addTimeInterval2List(self,list,startTime,endTime):
        listLen = len(list)
        if listLen>0 and list[listLen-1][1] == startTime:
            list[listLen-1][1] = endTime
        else:
            list.append([startTime,endTime])
           
    #printResult(noCRCSRecordList,noProxyNetlogRecordList)
    def printResult(self):
        print "\n----User %s's Analysis as below:" %self.strUser
        noCRCSLen = len(self.noCRCSRecordList)
        if noCRCSLen>0: 
            print "CRCS missing: start time-->end time:"
            self.totalCRCSMissDuration = 0
            for record in self.noCRCSRecordList: 
                duration = self.getSecondsInterval(record[0],record[1])
                print "%s-->%s, duration:%d seconds" %(record[0],record[1],duration)
                self.totalCRCSMissDuration += duration
            print "User %s: total duration for CRCS miss is %d seconds" %(self.strUser,self.totalCRCSMissDuration)
        else:
            print "There's no CRCS missing between 2 power netlogs" 
        noProxyNetlogLen = len(self.noProxyNetlogRecordList)    
        if noProxyNetlogLen>0:
            self.totalNetlogMissDuration = 0
            print "proxy_ netlog missing: start time-->end time:"
            for record in self.noProxyNetlogRecordList:
                duration = self.getSecondsInterval(record[0],record[1])
                print "%s-->%s, duration:%f seconds" %(record[0],record[1],duration)
                self.totalNetlogMissDuration += duration
            print "User %s: total duration for proxy_xx netlog miss is %d seconds" %(self.strUser,self.totalNetlogMissDuration)
        else: 
            print "There's no proxy_ netlog  missing between 2 power netlogs"
    def isOutTimeRange(self,strPreTime,curTime):
        dtPreTime= datetime.datetime.strptime(strPreTime, Time_Format)
        dtCurTime= datetime.datetime.strptime(curTime, Time_Format)
        dtTime = dtPreTime+ datetime.timedelta(minutes=MAX_MISS_INTEVAL)
        return dtCurTime>=dtTime
    def getSecondsInterval(self,strStart, strEnd):
        dtStartTime= datetime.datetime.strptime(strStart, Time_Format) 
        dtEndTime= datetime.datetime.strptime(strEnd, Time_Format)
        d = dtEndTime - dtStartTime
        return d.total_seconds()
    def getCRCSType(self,crcsList):
        strType = crcsList[CRCS_TYPE_INDEX] 
        if strType=="power":
            return POWER_TYPE
        else:
            return 0
    def splitCRCSLine(self,crcsLine):
        crcsList = crcsLine.split(",")
        if len(crcsList)>1:
            return crcsList
    def isNetlogStartWithProxy(self,crcsLine):
        ret = 0;
        if len(crcsLine)>CRCS_OPERATOR_INDEX and crcsLine[2].strip()=="netlog":
            if crcsLine[CRCS_OPERATOR_INDEX].strip().startswith("proxy"):
                ret = 1
        return ret 
            

    
if __name__ =="__main__":
    print "start analyzing..."
    MAX_MISS_MINUTE = 60 #minute
    crcsMissList = []
    netlogMissList = []
    #folderDir = r"D:\tmp\ticket\temp\crcs_details"
    folderDir = ""
    print "the input CRCS folder is incorrect"
    while True:
        print "Please input CRCS folder path:"
        folderDir = raw_input().strip()
        if os.path.exists(folderDir):
            break
    listFile = os.listdir(folderDir);
    for crcsFile in listFile:
        crcsPath = os.path.join(folderDir,crcsFile);
        userAnalyze = CRCSAnalyze(crcsPath)
        userAnalyze.analyze()
        if userAnalyze.totalCRCSMissDuration>=MAX_MISS_MINUTE*60:
            crcsMissList.append(userAnalyze)
        if userAnalyze.totalNetlogMissDuration>=MAX_MISS_MINUTE*60:
            netlogMissList.append(userAnalyze)
    
    print "\n\nFinal report:"
    print "The following user miss CRCS more than %d seconds" %(MAX_MISS_MINUTE*60)
    for userAnalyze in crcsMissList:
        print "User %s, CRCS miss duration %d seconds" %(userAnalyze.strUser,userAnalyze.totalCRCSMissDuration)
        
    print "\nThe following user miss proxy_xx netlog more than %d seconds" %(MAX_MISS_MINUTE*60)
    for userAnalyze in netlogMissList:
        print "User %s, proxy_xx netlog miss duration %d seconds" %(userAnalyze.strUser,userAnalyze.totalNetlogMissDuration)
        
    
    print "analysis finished"
    
