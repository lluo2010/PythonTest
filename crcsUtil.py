#coding=utf-8
import os
import shutil
import fileinput
import time
import sys
    

def getUserHexListFromFile(idFilePath, isHexFile):
    userList = []
    for line in fileinput.input(idFilePath):
        decIDString = line.strip("\n")
        strHex = decIDString
        if not isHexFile:
            strHex =hex(int(decIDString))
        strLen = len(strHex)
        strHex = "0-"+strHex[2:strLen-1]+"-0"
        print strHex    
        userList.append(strHex)
        
    return userList

def filterCRCSByHexUserList(hexUserList, srcCRCSPath):
    print hexUserList
    dstCRCSPath = os.path.dirname(srcCRCSPath)+os.sep+"filterCRCS_"+str(time.time())+".csv"
    with open(dstCRCSPath, "w") as resultFile:
        for line in fileinput.input(srcCRCSPath):
            tempLine = line.strip("\n").split(",") 
            if tempLine[1] in hexUserList:
                resultFile.write(line)

#filter CRCS according to  specific user list
def filterCRCS(srcCRCSPath, userFilePath, isHexFile):
    userHexList = getUserHexListFromFile(userFilePath, isHexFile)
    if len(userHexList)>0:
        filterCRCSByHexUserList(userHexList, srcCRCSPath)
    else:
        print "No user"
    pass

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
if __name__=="__main__":
    print "start"
    time.clock()
   
    print "finished"
    print "cost time: %d seconds" %(time.clock())
    pass