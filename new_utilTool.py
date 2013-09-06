#coding=utf-8
import paramiko
import time
import datetime
import cmd
import sys
import os
import multiprocessing

import util
import hostManager

sgwUser = "lluo"
sgwPassword = "5even!@"
sgwServer = "sgw.seven.com"
sgwPort = 22
#058, DEV, giant
'''
strSSHServer1 = "ap01.telx.7sys.net" 
SSHServer1Path = "/app0/arm084-ap01f/logs/"
strSSHServer2 = "ap02.telx.7sys.net" 
SSHServer2Path = "/app0/arm084-ap02f/logs/"
'''
'''
#053,stable,shark
strSSHServer1 = "ap01.telx.7sys.net" 
SSHServer1Path = "/app1/arm079-ap01a/logs/"
strSSHServer2 = "ap02.telx.7sys.net" 
SSHServer2Path = "/app1/arm079-ap02a/logs/"
'''

#061,tmous
strSSHServer1 = "ap01.telx.7sys.net" 
SSHServer1Path = "/app1/arm087-ap01i/logs/"
strSSHServer2 = "ap02.telx.7sys.net" 
SSHServer2Path = "/app1/arm087-ap02i/logs/"



'''
#062,kddi
strSSHServer1 = "ap01.telx.7sys.net" 
SSHServer1Path = "/app0/arm088-ap01j/logs/"
strSSHServer2 = "ap02.telx.7sys.net" 
SSHServer2Path = "/app0/arm088-ap02j/logs/"
'''


SSHServerUser= "voyeur"

GREP_FILE = "crcs-transaction.log"

def printAllOutput(out,err):
    outList = out.readlines()
    errList = err.readlines()
    if len(outList)>0:
        for line in outList:
            print line,
    if len(errList)>0:
        print errList


class CRCSDownloader(object):
    FOLDER_NAME_PREFIX = "crcs_download_"
    CRCS_NAME_PREFIX = "crcs_"
    def __init__(self, ssh,sshServer,sshServerPath,crcsFolderPath):
        self.ssh = ssh
        self.server = sshServer
        self.serverPath = sshServerPath
        self.crcsFolderPath = crcsFolderPath
        pass

    def grepCRCS(self,strGrepDay):
        strGrepPath = self.serverPath+GREP_FILE+"-"+strGrepDay[:7]+"*"
        print strGrepPath 
        crcsFileName = "%s_%s_%d.crcs" %(CRCSDownloader.CRCS_NAME_PREFIX,strGrepDay,time.time())
        grepCMD = "grep -h \"^%s\" %s" %(strGrepDay,strGrepPath)
        crcsDstPath = "/home/voyeur/"+crcsFileName; 
        loginCmd = "ssh -tt %s@%s" %(SSHServerUser,self.server)
        sshCMD = loginCmd+' ' +grepCMD+' \> '+crcsDstPath+';exit'
        print "Grep result"
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
        
        crcsPath = crcsDstPath
        sshCMD = "scp %s@%s:%s %s/" %(SSHServerUser,self.server,crcsPath,self.crcsFolderPath)
        print "Copy file from server to sgw"
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
        print "finished copy crcs to swg server..."
        
        '''
        crcsPath = "%s/%s" %(self.crcsFolderPath,crcsFileName)
        self.zipFile(crcsPath)
        
        #can't use '~' for home path here
        #remoteFilePath = "/home/lluo/%s/%s.gz" %(crcsFolderName,crcsFileName,)
        remoteFilePath = "%s/%s.gz" %(self.crcsFolderPath,crcsFileName,)
        localPath = "./%s.gz" %(crcsFileName) 
        self.downloadFile(remoteFilePath,localPath)
        '''
        
        print "finish greping file and download it from second server"
    
    
class ServerOperator(object):
    def __init__(self,ssh):  
        self.ssh = ssh
        pass
    def __mkdir(self,dirPath):
        print "mkdir path:%s" %(dirPath,)
        sshCMD = "mkdir %s" %(dirPath)
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
    def __mergeAndSortCRCS(self,crcsPath,finalCRCSName):
        print "Merge CRCS and sort in %s" %(crcsPath,)
        tempCRCSPath = "%s/%s" %(crcsPath,finalCRCSName)
        sshCMD = "cat %s/%s* >%s" %(crcsPath,CRCSDownloader.CRCS_NAME_PREFIX,tempCRCSPath)
        print sshCMD
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
        
        print "Sort crcs..."
        finalCRCSPath = "%s_" %(tempCRCSPath)
        sshCMD = "sort %s > %s" %(tempCRCSPath,finalCRCSPath)
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
        return finalCRCSPath
        pass        
    
    def __downloadFile(self,remotePath, localPath):
        print "remote Path:%s, local path:%s" %(remotePath,localPath)
        t = paramiko.Transport((sgwServer, sgwPort))
        print "Try to connect to ftp"
        t.connect(username=sgwUser, password=sgwPassword)
        print "Downloading file %s from ftp" %localPath
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remotePath, localPath)
        t.close()
        print "download finish..."
        
    def __remoteZipFile(self,filePath):
        print "Gzip file:"+filePath
        sshCMD = "gzip -f %s" %(filePath,)
        INInfo, stdout, stderr = self.ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
                   
    def getCRCS(self,strGrepDay):
        crcsFolderName = "%s_%d" %(CRCSDownloader.FOLDER_NAME_PREFIX,time.time())
        crcsDirPath = "/home/%s/%s" %(sgwUser,crcsFolderName)
        self.__mkdir(crcsDirPath)
        #todo:need check if dir is created
        crcsLoader1 = CRCSDownloader(self.ssh,strSSHServer1,SSHServer1Path,crcsDirPath)
        crcsLoader1.grepCRCS(strGrepDay)
        crcsLoader2 = CRCSDownloader(self.ssh,strSSHServer2,SSHServer2Path,crcsDirPath)
        crcsLoader2.grepCRCS(strGrepDay)
        finalCRCSName = "crcs_%s.log" %(strGrepDay,)
        finalCRCSPath = self.__mergeAndSortCRCS(crcsDirPath,finalCRCSName);
        self.__remoteZipFile(finalCRCSPath)
        remoteFilePath = "%s.gz" %(finalCRCSPath,)
        localPath = "./%s.gz" %(finalCRCSName)
        self.__downloadFile(remoteFilePath,localPath)
        #grepAndDownloadFile(ssh,strSSHServer1,SSHServer1Path,strGrepDay)
        #grepAndDownloadFile(ssh,strSSHServer2,SSHServer2Path,strGrepDay)
        print "finish greping file and download it from second server"
    def getCRCSEx(self,strGrepDay,hostInfoList):
        crcsFolderName = "%s_%d" %(CRCSDownloader.FOLDER_NAME_PREFIX,time.time())
        crcsDirPath = "/home/%s/%s" %(sgwUser,crcsFolderName)
        self.__mkdir(crcsDirPath)
        #todo:need check if dir is created
        crcsLoader1 = CRCSDownloader(self.ssh,hostInfoList[0][0],hostInfoList[0][1],crcsDirPath)
        crcsLoader1.grepCRCS(strGrepDay)
        crcsLoader2 = CRCSDownloader(self.ssh,hostInfoList[1][0],hostInfoList[1][1],crcsDirPath)
        crcsLoader2.grepCRCS(strGrepDay)
        finalCRCSName = "crcs_%s.log" %(strGrepDay,)
        finalCRCSPath = self.__mergeAndSortCRCS(crcsDirPath,finalCRCSName);
        self.__remoteZipFile(finalCRCSPath)
        remoteFilePath = "%s.gz" %(finalCRCSPath,)
        localPath = "./%s.gz" %(finalCRCSName)
        self.__downloadFile(remoteFilePath,localPath)
        #grepAndDownloadFile(ssh,strSSHServer1,SSHServer1Path,strGrepDay)
        #grepAndDownloadFile(ssh,strSSHServer2,SSHServer2Path,strGrepDay)
        print "finish greping file and download it from second server"
        

def getAction(): 
    while(1): 
        print "---Input what you want to do:1 to get CRCS,2 to get user list,3 to get OC version,2 or 3?" 
        action = raw_input().strip()
        if action in ["1","2","3"]: 
            return action
                
    
def grepUserList(ssh,strSSHServer,sshServerPath):
    dtPreDay = datetime.datetime.now()-datetime.timedelta(days= 1)
    strGrepDay = "%d-%02d" %(dtPreDay.date().year,dtPreDay.date().month)
    strGrepPath = sshServerPath+"relay-upc-transaction.log*" 
    
    grepCMD = "grep -h \"%s\" %s" %(strGrepDay,strGrepPath)
    print grepCMD
    loginCmd = "ssh -tt %s@%s" %(SSHServerUser,strSSHServer)
    sshCMD = loginCmd+' ' +grepCMD+"|awk -F, '{print $2,$8}'|sort|uniq"
    print sshCMD
    print "Get 7TP IMEI list:"
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    printAllOutput(stdout,stderr)

def grepOCInfo(ssh,strSSHServer,sshServerPath,strGrepUser,strGrepDay):
    strGrepPath = sshServerPath+"relay-upc-transaction.log*" 
	#grep -h -i "0-13fbf1e38cd03-0" \path\relay-upc-transaction.log |grep "2013-04-05
    grepCMD = "grep -h -i \"%s\" %s|grep %s |awk -F, '{print $1,$2,$8,$22}'  |sort|uniq" %(strGrepUser,strGrepPath,strGrepDay)
    print grepCMD
    loginCmd = "ssh -tt %s@%s" %(SSHServerUser,strSSHServer)
    sshCMD = loginCmd+' ' +grepCMD
    print sshCMD
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    return stdout.readlines()
def getOCVersion(strGrepUser,strGrepDay):
    hostInfoList = [(strSSHServer1,SSHServer1Path),(strSSHServer2,SSHServer2Path)]
    getOCVersionEx(strGrepUser, strGrepDay, hostInfoList)
def getOCVersionEx(strGrepUser,strGrepDay,hostInfoList):
    if not hostInfoList:
        print "no host info,exist"
        return
    ssh = connect2SSH() 
    list1 = grepOCInfo(ssh,hostInfoList[0][0],hostInfoList[0][1],strGrepUser,strGrepDay)
    list2 = grepOCInfo(ssh,hostInfoList[1][0],hostInfoList[1][1],strGrepUser,strGrepDay)
    ssh.close()
    
    list3 = list1+list2
    resultSet = set(list3)
    print "Trying to get %s's version on %s\r\n Time\t7TP\tIMEI\tOCVersion:" %(strGrepUser,strGrepDay)
    versionList = []
    for info in resultSet:
        print "***"+info,
        temp = info.strip().split()
        if len(temp)>0:
            versionList.append(temp[-1])
    if len(versionList)>0:
        print "---User %s's OC version on %s is %s" %(strGrepUser,strGrepDay,",".join(set(versionList)))
    else:
        print "Nothing is found"
def executeCMD(ssh,strSSHServer,sshServerPath,strCMD, strCMDFile):
    strGrepPath = sshServerPath 
    strCMDFile= strCMDFile.strip()
    if strCMDFile and len(strCMDFile)>0:
        strGrepPath = strGrepPath + os.sep+strCMDFile
    
    exeCMD = "%s %s" %(strCMD,strGrepPath)
    print exeCMD
    loginCmd = "ssh -tt %s@%s" %(SSHServerUser,strSSHServer)
    sshCMD = loginCmd+' ' +exeCMD
    print sshCMD
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    outputList = []
    for outputLine in stdout:
        outputList.append(outputLine)
    #printAllOutput(stdout,stderr)
    return outputList

def executeCMDOnTrial(hostInfoList,strCMD,strCMDFile):
    print "Start execute cmd on remote host..."
    ssh = connect2SSH() 
    list1 = executeCMD(ssh,hostInfoList[0][0],hostInfoList[0][1],strCMD,strCMDFile)
    list2 = executeCMD(ssh,hostInfoList[1][0],hostInfoList[1][1],strCMD,strCMDFile)
    ssh.close()
    list3 = list1+list2
    list3.sort()
    print "execute command %s result:" %(strCMD)
    for result in list3:
        print result,
    
def connect2SSH(): 
    print "start..."
    print "Try to connect to sgw..."
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(sgwServer, sgwPort, sgwUser, sgwPassword)
    return ssh

class CRCSUtilCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '''You can execute following command:
    1) Download CRCS command format:
        downloadCRCS hostName time
        Example: downloadCRCS demo062 2013-08-15 
    2) Get OC version,command format:
        getVersion hostName userID time
        Example: getVersion demo061 14122a6a52078 2013-05-01 or getVersion demo061 13a8 2013-05-01
    3) Filter log, command format:
        filterLog logfolderPath
    4) Split crcs, command format:
        splitCRCS crcsFilePath
    5) Execute command on remote host, command format:
        exeCMD:demo062:grep -ir "netlog,":crcs.log 
    6) Run PCD, command format:
        runPCD pcdPath
    7) Run ddoc, command format:
        runddoc
    8) Open useful directory, command format:
        openDIR
    9) Run some useful operate I want, command format:
        ready
    10) exist, input quit or exit.

'''
    def do_downloadCRCS(self,parammeterLine):
        parammeterLine = parammeterLine.strip()
        hostName,strTime = parammeterLine.split()
        print "host name: %s, search time:%s " %(hostName, strTime)
        hostInfoList = hostManager.HostManager().getHostInfoList(hostName)
        if not hostInfoList:
            print "can't find host %s server information" %(hostName,)
            return
        print hostInfoList
        ssh = connect2SSH()
        serverOpr = ServerOperator(ssh)
        serverOpr.getCRCSEx(strTime,hostInfoList)
        ssh.close() 
    #输入quit时退出
    def do_getVersion(self,line):
        line = line.strip()
        hostName,strUserID,strTime = line.split()
        print "host name:%s,user ID:%s,search time:%s" %(hostName,strUserID,strTime)
        hostInfoList = hostManager.HostManager().getHostInfoList(hostName)
        if not hostInfoList:
            print "can't find host %s server information" %(hostName,)
            return
        print hostInfoList
        getOCVersionEx(strUserID,strTime,hostInfoList)
    def do_exeCMD(self, parammeterLine):
        parammeterLine = parammeterLine.strip()
        #exeCMD:demo062:grep -ir "netlog,":crcs.log 
        splitResult = parammeterLine.split(":")
        print splitResult
        splitLen = len(splitResult)
        if splitLen<3:
            print "Parameter is missed"
            return
        hostName = splitResult[1].strip()
        strCMD = splitResult[2].strip()
        strFile = ""
        if splitLen==4:
            strFile = splitResult[3].strip()
        print "host name %s" %(hostName,)
        hostInfoList = hostManager.HostManager().getHostInfoList(hostName)
        if not hostInfoList:
            print "can't find host %s server information" %(hostName,)
            return
        print hostInfoList   
        executeCMDOnTrial(hostInfoList,strCMD,strFile)
    def do_filterLog(self,logPath):
        dirPath = "" 
        if logPath and len(logPath)>0:
            dirPath = logPath.strip()
        if not dirPath:
            dirPath = os.curdir+os.sep+"log"
        if os.path.exists(dirPath):
            util.filterFiles(dirPath)
        else:
            print "Dir %s does not exist" %(dirPath)
            
    def do_splitCRCS(self,crcsPath):
        strCRCSPath = "" 
        if crcsPath and len(crcsPath)>0:
            strCRCSPath = crcsPath.strip()
        if not strCRCSPath:
            strCRCSPath = os.curdir+os.sep+"crcs.csv"
        if os.path.exists(strCRCSPath):
            util.splitCRCS(strCRCSPath)
        else:
            print "file %s does not exist" %(strCRCSPath)
    def runPCD(self,pcdPath):
        if not pcdPath or len(pcdPath):
            '''
            print "please input PCD path"
            return
            '''
            pcdPath = r"D:\Project\Analysis\pcd.jar"
        pcdPath = pcdPath.strip()
        if os.path.exists(pcdPath):
            util.runPCD(pcdPath)
        else:
            print "PCD does not exist"
    def do_runPCD(self,pcdPath):
        p = multiprocessing.Process(target=self.runPCD,args=(pcdPath,))
        p.start()
        
    def do_openDIR(self, parameter):
        dirs = [r"D:\Project\Analysis\tool",r"D:\tmp\ticket"]
        for strDir in dirs:
            strOpenDirCmd = "explorer %s" %(strDir)
            util.shell_executeInProcessor(strOpenDirCmd)
    def do_runddoc(self,parameter):
        appName = "ddoclog.jar"
        dirPath = r"D:\Project\Analysis\tool"
        disk = dirPath.split(":")[0]
        strCMD = disk.strip()+": & cd "+dirPath+" & "+"java -jar "+dirPath+os.sep+ appName
        print strCMD
        util.shell_executeInProcessor(strCMD)
        print "finish"
        
    def do_ready(self,parameter):
        print "Open useful directory"
        self.do_openDIR(None)
        
        print "Run PCD"
        self.do_runPCD(None)
        
        print "Run cygwin"
        util.shell_executeInProcessor(r"C:\cygwin\bin\mintty.exe -i /Cygwin-Terminal.ico -")
        
        print "Run ddoc tool"
        self.do_runddoc(None)
    #输入认不出命令时
    def default(self,line):
        print "The command you input is not supported"
            
    def do_quit(self, arg):
        print "Quit"
        sys.exit(1)
    #输入exit时退出
    def do_exit(self, arg):
        print "Exit"
        sys.exit(1)
    def do_EOF(self, line):
        return True
    
if __name__=="__main__":
    print "start"
    time.clock()
    CRCSUtilCmd().cmdloop()
    print "finished"
    print "cost time: %d seconds" %(time.clock())
  
'''  
if __name__=="__main__": 
    strGZFile = r"D:\temp\test\crcs_2013-08-05.log.gz"
    util.extractGzipFile(strGZFile) 
    while 1: 
        action = getAction() 
        if action=="1": 
            print "Please input the Date(UTC) you want to grep, format:2013-05-01" 
            strGrepDay= raw_input().strip() 
            print "grep Data:%s" %(strGrepDay,) 
            ssh = connect2SSH() 
            serverOpr = ServerOperator(ssh)
            serverOpr.getCRCS(strGrepDay)
            ssh.close() 
        elif action=="2": 
            ssh = connect2SSH() 
            grepUserList(ssh,strSSHServer1,SSHServer1Path) 
            ssh.close() 
        elif action=="3": 
            while 1: 
                print 'Input the the user and date,split by ":", format:14122a6a52078:2013-05-01 or 13a8:2013-05-01'
                input= raw_input().strip() 
                if len(input)>0 and input.find(':')>0: 
                    strGrepUser,strGrepDay = input.split(":") 
                    getOCVersion(strGrepUser,strGrepDay) 
                    break 
    
        print "Finished...\n"
'''