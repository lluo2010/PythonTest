import os
import shutil
import subprocess
import fileinput
import time

def splitCRCS(crcsPath):
    if not os.path.exists(crcsPath):
        print "there's no crcs.csv, exist"
        return
    
    userList = []
    fileList = []
    strPath = "."+os.sep+"output"
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
    
    
if __name__=="__main__":
    print "start split..."
    time.clock()
    splitCRCS("."+os.sep+"crcs.csv")
    print "finished"
    print "cost time: %d seconds" %(time.clock())
    raw_input("Input any key to exit")