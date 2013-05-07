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
        print "Input what you want to do:1 to get CRCS,2 to get user list,1 or 2?" 
        action = raw_input().strip()
        if action in ["1","2"]: 
            return action
                
def getCRCS(strGrepDay,ssh):
    grepAndDownloadFile(ssh,strSSHServer1,SSHServer1Path,strGrepDay)
    grepAndDownloadFile(ssh,strSSHServer2,SSHServer2Path,strGrepDay)
    print "finish greping file and download it from second server"
    
def grepUserList(ssh,strSSHServer,sshServerPath):
    dtPreDay = datetime.datetime.now()-datetime.timedelta(days= 1)
    strGrepDay = "%d-%02d" %(dtPreDay.date().year,dtPreDay.date().month)
    strGrepPath = sshServerPath+"upc-baseline.log*" 
    
    grepCMD = "grep -h \"%s\" %s" %(strGrepDay,strGrepPath)
    print grepCMD
    loginCmd = "ssh -tt %s@%s" %(SSHServerUser,strSSHServer)
    sshCMD = loginCmd+' ' +grepCMD+"|awk -F, '{print $2,$8}'|sort|uniq"
    print sshCMD
    print "Get 7TP IMEI list:"
    stdin, stdout, stderr = ssh.exec_command(sshCMD)
    printAllOutput(stdout,stderr)
def connect2SSH(): 
    print "start..."
    print "Try to connect to sgw..."
    ssh = paramiko.SSHClient() 
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.connect(sgwServer, sgwPort, sgwUser, sgwPassword)
    return ssh

if __name__=="__main__": 
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
    print "Finished..."
    raw_input("Input any key to exit")