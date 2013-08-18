#coding=utf-8
import os
import sys
import shutil
import subprocess
import fileinput
import time
import gzip
import cmd

def __test1():
    '''
    strPath = r"D:\tmp\ticket\TMobile\08-08\log"
    basePath = os.path.dirname(strPath)
    '''
    shutil.move(r"D:\tmp\ticket\TMobile\08-08\a\1.txt", r"D:\tmp\ticket\TMobile\08-08\a\next")
    print os.path.splitext("a.txt")
    
def shell_execute(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
    return (p.communicate())
def getFilelist(strPath,strExtName):
    matchedFileList = []
    fileList = os.listdir(strPath)
    for fileName in fileList:
        filePath = strPath+os.sep+fileName
        if os.path.isfile(filePath):
            splitResult = os.path.splitext(fileName)
            if splitResult[1]==strExtName:
                matchedFileList.append(filePath)
        elif os.path.isdir(filePath):
            tempMatchList = getFilelist(filePath,strExtName)
            matchedFileList.extend(tempMatchList)
    return matchedFileList

def splitCRCS(crcsPath):
    userList = []
    fileList = []
    strPath = os.path.dirname(crcsPath)+os.sep+"splitCRCS"
    if os.path.exists(strPath):
        shutil.rmtree(strPath, ignore_errors=True)
    os.mkdir(strPath)
    print "Split CRCS to %s" %(os.path.abspath(strPath))
    for line in fileinput.input(crcsPath):
        tempLine = line.strip("\n").split(",")
        user = tempLine[1].strip()
        index = -1
        if user in userList:
            index = userList.index(user, 0)
        if index>=0:
            userFile = fileList[index]
            userFile.write(line)
        else:
            userList.append(user)
            strOpenFile = strPath+os.sep+user+".csv"
            userFile = open(strOpenFile,"w")
            fileList.append(userFile)
            userFile.write(line)
    
    for userFile in fileList:
        userFile.close()
            
    pass
def filterFiles(strSourcePath):
    #strSourcePath = r"D:\tmp\ticket\TMobile\08-08\log"
    csvList = getFilelist(strSourcePath, ".csv")
    pcapList = getFilelist(strSourcePath, ".pcap")
    basePath = os.path.dirname(strSourcePath)
    strCSVDstPath = basePath+os.sep+"CSV"
    strPCAPPath = basePath+os.sep+"Tcpdump"
    if not os.path.exists(strCSVDstPath):
        os.mkdir(strCSVDstPath)
    if not os.path.exists(strPCAPPath):
        os.mkdir(strPCAPPath)
    for csv in csvList:
        shutil.move(csv, strCSVDstPath)
    for pcap in pcapList:
        shutil.move(pcap, strPCAPPath)
    print "%d csv files and %d pcap files are moved\n" %(len(csvList),len(pcapList))
    
def extractGzipFile(strGZFile):
    #strGZFile = r"D:\temp\test\crcs_2013-08-05.log.gz"
    splitResult = os.path.splitext(strGZFile)
    inputFilePath =  splitResult[0]
    gzFile = gzip.open(strGZFile, 'rb')
    try:
        with open(inputFilePath,"wb") as resultFile:
            resultFile.write(gzFile.read())
    finally:
        gzFile.close()
    pass
def testCase1():
    strPath = r"D:\tmp\ticket\TMobile\08-08\a"
    #test1()
    findList = getFilelist(strPath,".txt")
    for findFile in findList:
        print findFile
        
def testCase2():
    strPath = r"D:\tmp\ticket\TMobile\08-08\log"
    csvList = getFilelist(strPath, ".csv")
    print "csv list, num %d" %(len(csvList))
    for csv in csvList:
        print csv
def testGZipExtractFile():
    strGZFile = r"D:\temp\test\crcs_2013-08-05.log.gz"
    extractGzipFile(strGZFile) 

def testSplitFile():
    strCRCSPath = "" 
    if len(sys.argv)>1:
        strCRCSPath = sys.argv[1].strip()
    if not strCRCSPath:
        strCRCSPath = os.curdir+os.sep+"crcs.csv"
    if os.path.exists(strCRCSPath):
        splitCRCS(strCRCSPath)
    else:
        print "file %s does not exist" %(strCRCSPath)

def testFilterFiles():
    dirPath = "" 
    if len(sys.argv)>1:
        dirPath = sys.argv[1].strip()
    if not dirPath:
        dirPath = os.curdir+os.sep+"log"
    if os.path.exists(dirPath):
        filterFiles(dirPath)
    else:
        print "Dir %s does not exist" %(dirPath)
        

class UtilCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '''You can execute following command:
    1) filter log, command format:
        filterLog logfolderPath
    2) split crcs, command format:
        splitCRCS crcsFilePath
    10) exist, input quit or exit.
'''
        #self.intro = "Simple command processor example."
    def do_test(self,str):
        print "test, %s" %(str)
        
    def do_filterLog(self,logPath):
        dirPath = "" 
        if logPath and len(logPath)>0:
            dirPath = logPath.strip()
        if not dirPath:
            dirPath = os.curdir+os.sep+"log"
        if os.path.exists(dirPath):
            filterFiles(dirPath)
        else:
            print "Dir %s does not exist" %(dirPath)
            
    def do_splitCRCS(self,crcsPath):
        strCRCSPath = "" 
        if crcsPath and len(crcsPath)>0:
            strCRCSPath = crcsPath.strip()
        if not strCRCSPath:
            strCRCSPath = os.curdir+os.sep+"crcs.csv"
        if os.path.exists(strCRCSPath):
            splitCRCS(strCRCSPath)
        else:
            print "file %s does not exist" %(strCRCSPath)
        #输入认不出命令时
        def default(self,line):
            print "The command you input is not supported"
            
    def do_runPCD(self, pcdPath):
        if not pcdPath:
            '''
            print "please input PCD path"
            return
            '''
            pcdPath = r"D:\Project\Analysis\pcd.jar"
        pcdPath = pcdPath.strip()
        if os.path.exists(pcdPath):
            runPCDCommand = "java -Xmx1048m -jar %s" %(pcdPath,)
            print runPCDCommand
            result = shell_execute(runPCDCommand)
            print result
            pass
        else:
            print "PCD does not exist"
        pass
    #输入quit时退出
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
    
    #test1()
    #testCase1()
    #testFilterFiles()    
    #testGZipExtractFile()   
    #testSplitFile()
    UtilCmd().cmdloop()
    print "finished"
    print "cost time: %d seconds" %(time.clock())
    pass
