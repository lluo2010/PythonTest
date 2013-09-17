import os
import shutil
import subprocess
import fileinput
import time
import sys
import util
#from commands import *

def test1():
    output = subprocess.check_output(
    'echo to stdout; echo to stderr 1>&2; exit 1',
    shell=True,
    stderr=subprocess.STDOUT,
    )
    print 'Have %d bytes in output' % len(output)
    print output
    
def test2():
    idFilePath = r"D:\tmp\ticket\TMobile\Tmous-user.txt"
    for line in fileinput.input(idFilePath):
        decIDString = line.strip("\n")
        
        strHex =hex(int(decIDString))
        strLen = len(strHex)
        strHex = "0-"+strHex[2:strLen-1]+"-0"
        print strHex

def getUserHexList():
    userList = []
    idFilePath = r"D:\tmp\ticket\TMobile\Tmous-user.txt"
    for line in fileinput.input(idFilePath):
        decIDString = line.strip("\n")
        
        strHex =hex(int(decIDString))
        strLen = len(strHex)
        strHex = "0-"+strHex[2:strLen-1]+"-0"
        print strHex    
        userList.append(strHex)
    return userList
    pass

def test3():
    userList = getUserHexList()
    '''
    userList = ["0-143c1339748b0-0","0-143c1339747f9-0","0-143c133974775-0",
                "0-143c133974556-0","0-143c1339745b9-0","0-143c1339745e3-0",
                "0-143c13397437f-0","0-143c133974467-0","0-143c133974236-0"]
    '''
    print userList
    crcsPath = r"D:\tmp\ticket\TMobile\crcs.log"
    filteredCRCSPath = r"D:\tmp\ticket\TMobile\filter-crcs.log"
    with open(filteredCRCSPath, "w") as resultFile:
        for line in fileinput.input(crcsPath):
            tempLine = line.strip("\n").split(",") 
            if tempLine[1] in userList:
                resultFile.write(line)

def splitCRCS(crcsPath):
    userList = []
    fileList = []
    strPath = os.path.dirname(crcsPath)+os.sep+"splitCRCS"
    if os.path.exists(strPath):
        shutil.rmtree(strPath, ignore_errors=True)
    os.mkdir(strPath)
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

def testGetFirst():
    strPath = r"D:\tmp\ticket\TMobile\08-11\upc.log"
    userList = []
    upcList = []
    for tempLine in fileinput.input(strPath):
        struser = tempLine.split(",")[1]
        if not struser in userList:
            userList.append(struser)
            upcList.append(tempLine)
            print struser
    print len(userList)
    print userList
    print "upc list:"
    for upc in upcList:
        print upc,
def test4():
    str ="abc"
    splitList = str.split(":")
    print len(splitList) 
    print "%s" %(",".join(splitList))
    
    pass
def test5():
    import fileinput
    userList = []
    userTimeList = []
    filePath = r"D:\tmp\ticket\temp\a"
    for line in fileinput.input(filePath):
        dt,user = line.split(",")
        user = user.strip("\n")
        if not user in userList:
            userList.append(user)
            userTimeList.append((user,dt))
    for userInfo in userTimeList:
        print "%s:%s" %(userInfo[0],userInfo[1])
        
def test6():
    
    for i in range(10):
        strPath = r"D:\tmp\ticket\17946\temp"+os.sep+str(1)+"-"+str(i)+".log"
        with open(strPath,"w") as tempFile:
            pass

import multiprocessing
def newProcessor():       
    print "new processor"
    pcdPath = r"D:\Project\Analysis\pcd.jar"
    pcdPath = pcdPath.strip()
    if os.path.exists(pcdPath):
        runPCDCommand = "java -Xmx1048m -jar %s" %(pcdPath,)
        print runPCDCommand
        result = util.shell_execute(runPCDCommand)
        print result
    print "end new processor"
    pass
def test7():
    p = multiprocessing.Process(target=newProcessor)
    p.start()
    print "end test7"


class A(object):
    def runProcess(self):
        p = multiprocessing.Process(target=self.worker,args=("hello",))
        p.start()
        pass
    def worker(self,str):
        print str
if __name__=="__main__":
    print "start"
    time.clock()
    #test7()
    #a = A()
    #a.runProcess()
    #test4()
    #testSplitFile()
    #testGetFirst()
    print "finished"
    print "cost time: %d seconds" %(time.clock())
    pass