#coding=utf-8

import os
import subprocess
import datetime
import fileinput


PCD_JAR_PATH = r'D:\Project\Analysis\pcd.jar'


CONNECTION_SUMMARY = 0
BYTE_SUMMARY = 1
def shell_execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    return (p.communicate())


class generatePCDReport(object):
    def __init__(self,strPCDJarPath, strCRCSFilePath,strTcpdumpPath):
        self.strPCDJarPath = strPCDJarPath
        self.strCRCSFilePath = strCRCSFilePath
        self.strTcpdumpPath = strTcpdumpPath
    def generateBasicReport(self):
        output = shell_execute(self.getReportCmd())
        print "----finish generating Basic report,output:"+str(output)
    def getReportCmd(self):
        #Java �jar pcd.jar -c crcs.csv -tsw tcpdump
        cmd = "java -Xmx1048m -jar %s -c %s -tsw %s" %(self.strPCDJarPath,self.strCRCSFilePath,self.strTcpdumpPath)
        return cmd
    
def getCRCSAndTcpdumpPath(strPath):
    pathList = os.listdir(strPath)
    strTcpdumpPath = ""
    strCSVPath = ""
    for file in pathList:
        strFilePath = os.path.join(strPath,file)
        if file.lower()=="tcpdump" and os.path.isdir(strFilePath):
            strTcpdumpPath = strFilePath
        elif file.endswith(".log") and os.path.isfile(strFilePath):
            strCSVPath = strFilePath
    print "crcs path:"+strCSVPath +",tcpdump path:"+strTcpdumpPath
    return (strCSVPath,strTcpdumpPath)
    
    #reportGenerator = generatePCDReport(PCD_JAR_PATH,strCSVPath,strTcpdumpPath)
    #reportGenerator.generateBasicReport()
    
allUserPath = r"D:\tmp\ticket\15543\UserData\AvailableUser"
def generateAllUserBasicReport():
    pathList = os.listdir(allUserPath)
    strUser = ""
    for dirName in pathList:
        #strUser = dirName.split("-")[0]
        strUser = dirName.strip()
        strDirPath = os.path.join(allUserPath,dirName)
        if os.path.isdir(strDirPath):
            pathList = getCRCSAndTcpdumpPath(strDirPath)
            getPath = True
            for p in pathList:
                if len(p)<=0:
                    getPath = False
                    break
            if getPath:
                print "----start generate user %s's basic PCD report..." %(strUser)
                #print pathList[0],pathList[1]
                reportGenerator = generatePCDReport(PCD_JAR_PATH,pathList[0],pathList[1])
                reportGenerator.generateBasicReport()


    
def generateAllUncovereageSummary(summaryType):
    if summaryType not in [BYTE_SUMMARY,CONNECTION_SUMMARY]:
        print "summary type "+ str(summaryType) +"is not supported"
        return
    print "----start generate"
    title = "Byte-Uncoverage_Summary"
    if summaryType==CONNECTION_SUMMARY:
        title = "Connection-Uncoverage_Summary"
    strSummaryPath = getSummaryPath(title)
    with open(strSummaryPath,"w") as summaryFile:
        pathList = os.listdir(allUserPath) 
        strUser = ""
        bPrintHeader = True
        for dirName in pathList:
            strUser = dirName.split("-")[0]
            strDirPath = os.path.join(allUserPath,dirName)
            if os.path.isdir(strDirPath):
                UncoveredAnalysisName = "UncoveredAnalysis.csv"
                analysisFilePath = os.path.join(strDirPath,UncoveredAnalysisName)
                if summaryType==CONNECTION_SUMMARY:
                    fmt = UserConnectUncovereageSummaryFormat(strUser,analysisFilePath)
                elif summaryType==BYTE_SUMMARY:
                    fmt = UserByteUncovereageSummaryFormat(strUser,analysisFilePath) 
                summaryList = fmt.generateUncovereageSummary(bPrintHeader)
                bPrintHeader = False
                for tempList in summaryList:
                    summary = ",".join(tempList)
                    summaryFile.write(summary+"\n")
    
def getSummaryPath(strTile):
    strFormat = "%Y-%m-%d_%H_%M_%S_%f"
    strFileName = "%s_%s.csv" %(strTile,datetime.datetime.now().strftime(strFormat))
    strSummaryPath = os.path.join(os.getcwd(),strFileName)
    return strSummaryPath
    

def generateAllByteUncovereageSummary():
    generateAllUncovereageSummary(BYTE_SUMMARY) 
def generateAllConnectionUncovereageSummary():
    generateAllUncovereageSummary(CONNECTION_SUMMARY)
    
class UserByteUncovereageSummaryFormat(object):
    def __init__(self, strUser,strUncoverageAnalysisFilePath):
        self.strUncoverageAnalysisFilePath = strUncoverageAnalysisFilePath
        self.strUser = strUser
    def generateUncovereageSummary(self,bPrintHeader):
        headerList = []
        byteCoveragePercentList = []
        uncovereageList = []
        for line in fileinput.input(self.strUncoverageAnalysisFilePath):
            lineNo = fileinput.lineno()
            if lineNo ==1:
                headerList = line.strip("\n").split(",")
                headerList = headerList[:-1]
                print headerList
            elif lineNo in range(4,8):
                byteCoveragePercentList.append(line.strip("\n").split(","))
            elif lineNo in range(17,36):
                tempList = line.strip("\n").split(",")
                #remove 1-4 in list
                tempList[1:5] = []
                if lineNo ==17:
                    tempList[0] = ""
                uncovereageList.append(tempList)
        #print uncovereageList
        for listTemp in uncovereageList:
            headerList.append(listTemp[0])
            for (index,byteCovereagePercent) in enumerate(byteCoveragePercentList):
                byteCovereagePercent.append(listTemp[index+1])
        #print headerList
        #print byteCoveragePercentList
        summaryList = []
        if bPrintHeader:
            headerList.insert(0,"IMEI")
            summaryList.append(headerList)
        for (index,temp) in enumerate(byteCoveragePercentList):
            if index==0:
                temp.insert(0,self.strUser)
            else:
                temp.insert(0,"")
            summaryList.append(temp)
        
        #print summaryList
        return summaryList
    
class UserConnectUncovereageSummaryFormat(object):
    def __init__(self,strUser,strUncoverageAnalysisFilePath):
        self.strUncoverageAnalysisFilePath = strUncoverageAnalysisFilePath
        self.strUser = strUser
    def generateUncovereageSummary(self,bPrintHeader):
        headerList = []
        connectionCoveragePercentList = []
        uncovereageTypeList = []
        for line in fileinput.input(self.strUncoverageAnalysisFilePath):
            lineNo = fileinput.lineno()
            if lineNo ==1:
                headerList = line.strip("\n").split(",")
                headerList = headerList[:-1]
                print headerList
            elif lineNo ==2:
                connectionCoveragePercentList = line.strip("\n").split(",")
                connectionCoveragePercentList = connectionCoveragePercentList[1:-1]
            elif lineNo in range(18,39):
                tempList = line.strip("\n").split(",")
                #remove 1-4 in list
                tempList[2:] = []
                uncovereageTypeList.append(tempList)
        uncovereageTypeList = zip(*uncovereageTypeList)
        #print headerList
        #print byteCoveragePercentList
        summaryList = []
        if bPrintHeader:
            headerList[0] = "IMEI"
            summaryList.append(headerList+list(uncovereageTypeList[0]))
        info = connectionCoveragePercentList+list(uncovereageTypeList[1])
        info.insert(0,self.strUser)
        summaryList.append(info)
        return summaryList
        pass
if __name__ == '__main__':
    print "start generate PCD basic report..."
    #generateAllUserBasicReport()
    #generateAllByteUncovereageSummary()
    #generateAllUserBasicReport()
    generateAllConnectionUncovereageSummary()
    #UserConnectUncovereageSummaryFormat fmt()
    print "finish generate PCD basic report"
    pass