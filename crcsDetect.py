#coding=utf-8
import fileinput
import sys
import datetime
import os

MAX_MISS_INTEVAL = 120 #minutes

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
        self.crcsMissEndTime = ""
        self.deviceOnTime = ""
    def initRestartCheck(self,powerTime,batteryValue): 
        self.hasCRCS = 0
        self.hasProxyNetlog = 0
        self.preBatteryValue = batteryValue
        self.strPrePowerTime = powerTime
                                
    def analyze(self): 
        self.crcsMissEndTime = ""
        self.deviceOnTime = ""
        self.deviceOn = 0 
        self.initRestartCheck("",-1) 
        self.noCRCSRecordList = [] 
        self.noProxyNetlogRecordList = [] 
        for crcsLine in fileinput.input(self.crcsPath): 
            crcsList = self.splitCRCSLine(crcsLine) 
            if fileinput.isfirstline():
                self.strUser = crcsList[1].strip()
            if crcsList: 
                curTime = crcsList[0].strip() 
                if len(self.strPrePowerTime)>0 and len(curTime)>0 and self.isOutTimeRange(self.strPrePowerTime,curTime,MAX_MISS_INTEVAL):
                    self.addTimeInterval2List(self.noCRCSRecordList,self.strPrePowerTime,curTime)
                    self.crcsMissEndTime = curTime
                    #print "---add" +  self.strPrePowerTime+"--"+ curTime
                if len(crcsList)>4 and crcsList[4].strip()=="device_on":
                    self.deviceOnTime = curTime
                    
                deviceon_interval = 5 #5 minute
                if self.deviceOnTime!="" and self.crcsMissEndTime!="":
                    if self.isInTimeRange(self.deviceOnTime,self.crcsMissEndTime,deviceon_interval):
                        self.noCRCSRecordList.pop()
                        self.crcsMissEndTime = ""
                        #print "----delete "
                    
                self.strPrePowerTime = curTime
                
        self.printResult()
        
    def addTimeInterval2List(self,list,startTime,endTime):
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
        
    def isOutTimeRange(self,strPreTime,curTime,interval):
        dtPreTime= datetime.datetime.strptime(strPreTime, Time_Format)
        dtCurTime= datetime.datetime.strptime(curTime, Time_Format)
        dtTime = dtPreTime+ datetime.timedelta(minutes=interval)
        return dtCurTime>=dtTime
    def isInTimeRange(self,strPreTime,curTime,interval):
        dtPreTime= datetime.datetime.strptime(strPreTime, Time_Format)
        dtCurTime= datetime.datetime.strptime(curTime, Time_Format)
        
        if dtPreTime>dtCurTime:
            d = dtPreTime- dtCurTime
            return   d.total_seconds()< interval*60
        else:
            d = dtCurTime-dtPreTime
            return   d.total_seconds()< interval*60
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
    print "start analyzing..."
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
        
    print "\r\nanalysis finished"
    
    raw_input("Input any key to exit")