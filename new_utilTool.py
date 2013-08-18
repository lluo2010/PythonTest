#coding=utf-8
import paramiko
import time
import datetime
import util


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
#056,tmous
strSSHServer1 = "ap01.telx.7sys.net" 
SSHServer1Path = "/app0/arm082-ap01d/logs/"
strSSHServer2 = "ap02.telx.7sys.net" 
SSHServer2Path = "/app0/arm082-ap02d/logs/"
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
        INInfo, stdout, stderr = ssh.exec_command(sshCMD)
        printAllOutput(stdout,stderr)
        
        crcsPath = crcsDstPath
        sshCMD = "scp %s@%s:%s %s/" %(SSHServerUser,self.server,crcsPath,self.crcsFolderPath)
        print "Copy file from server to sgw"
        INInfo, stdout, stderr = ssh.exec_command(sshCMD)
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
    ssh = connect2SSH() 
    list1 = grepOCInfo(ssh,strSSHServer1,SSHServer1Path,strGrepUser,strGrepDay)
    list2 = grepOCInfo(ssh,strSSHServer2,SSHServer2Path,strGrepUser,strGrepDay)
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

def connect2SSH(): 
    print "start..."
    print "Try to connect to sgw..."
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(sgwServer, sgwPort, sgwUser, sgwPassword)
    return ssh

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