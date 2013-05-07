#coding=utf-8
import paramiko
import time
import datetime

sgwUser = "lluo"
sgwPassword = "5even!@"
sgwServer = "sgw.seven.com"
sgwPort = 22
strSSHServer1 = "ap27c.corp.seven.com" 
SSHServer1Path = "/usr/local/seven/eng008-ap27c/logs/"
strSSHServer2 = "ap28c.corp.seven.com" 
SSHServer2Path = "/usr/local/seven/eng008-ap28c/logs/"
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
    
def downloadFile(remotePath, localPath):
    print "remote Path:%s, local path:%s" %(remotePath,localPath)
    t = paramiko.Transport((sgwServer, sgwPort))
    print "Try to connect to ftp"
    t.connect(username=sgwUser, password=sgwPassword)
    print "Downloading file %s from ftp" %localPath
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remotePath, localPath)
    t.close()

def grepAndDownloadFile(ssh,strSSHServer,sshServerPath,strGrepDay):
    strGrepPath = sshServerPath+GREP_FILE+"-"+strGrepDay[:7]+"*"
    print strGrepPath 
    grepCMD = "grep -h \"^%s\" %s" %(strGrepDay,strGrepPath)
    crcsFileName = "crcs_%s_%d.crcs" %(strGrepDay,time.time())
    crcsDstPath = "/home/voyeur/"+crcsFileName; 
    loginCmd = "ssh -tt %s@%s" %(SSHServerUser,strSSHServer)
    sshCMD = loginCmd+' ' +grepCMD+' \> '+crcsDstPath+';exit'
    print "Grep result"
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    printAllOutput(stdout,stderr)
    
    crcsPath = crcsDstPath
    sshCMD = "scp %s@%s:%s ~/" %(SSHServerUser,strSSHServer,crcsPath)
    print "Copy file from server to sgw"
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    printAllOutput(stdout,stderr)
    print "finished copy crcs to swg server..."
    
    print "Gzip file:"+crcsFileName
    sshCMD = "gzip -f ~/%s" %(crcsFileName,)
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    printAllOutput(stdout,stderr)
    
    #can't use '~' for home path here
    remoteFilePath = "/home/lluo/%s.gz" %(crcsFileName,)
    localPath = "./%s.gz" %(crcsFileName) 
    downloadFile(remoteFilePath,localPath)
    
    print "finish greping file and download it from second server"

def getAction(): 
    while(1): 
        print "Input what you want to do:2 to get user list,3 to get OC version,2 or 3?" 
        action = raw_input().strip()
        if action in ["2","3"]: 
            return action
                
def getCRCS(strGrepDay,ssh):
    grepAndDownloadFile(ssh,strSSHServer1,SSHServer1Path,strGrepDay)
    grepAndDownloadFile(ssh,strSSHServer2,SSHServer2Path,strGrepDay)
    print "finish greping file and download it from second server"
    
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
        print info,
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
    while 1: 
        action = getAction() 
        if action=="1": 
            print "Please input the Date(UTC) you want to grep, format:2013-05-01" 
            strGrepDay= raw_input().strip() 
            print "grep Data:%s" %(strGrepDay,) 
            ssh = connect2SSH() 
            getCRCS(strGrepDay,ssh) 
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