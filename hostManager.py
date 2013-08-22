import os

class HostManager(object):
    def __init__(self):
        #self.strResourcePath = os.path.curdir+os.sep+"resources"
        self.strResourcePath  = r"D:\Project\Analysis\tool\resources"
    def __getHostFileList(self):
        if not os.path.exists(self.strResourcePath):
            print "path %s does not exist" %(self.strResourcePath,)
            return
        fileList = os.listdir(self.strResourcePath)
        hostFilePathList = []
        for tempFile in fileList:
            if tempFile.endswith(".hosts"):
                hostFilePath = self.strResourcePath+os.sep+tempFile
                #print hostFilePath
                hostFilePathList.append(hostFilePath)
            
        return hostFilePathList
    
    def getHostInfoList(self,hostName):
        hostList = self.__getHostFileList()
        if hostList:
            hostInfoList  = self.__getHostInfoList(hostName,hostList)
            print "host info %s" %(str(hostInfoList))
            return hostInfoList
    def __getHostInfoList(self,hostName, hostFilePathList):
        hostInfoList = []
        hostName = hostName.strip().lower()
        for hostFilePath in hostFilePathList:
            hostFileName = os.path.basename(hostFilePath)
            host = os.path.splitext(hostFileName)[0].strip()
            if hostName == host.lower():
                print "find %s" %(host)
                with open(hostFilePath) as hostFile:
                    lineInfo = hostFile.readline().strip()
                    hostInfo1 = self.__parseHostInfo(lineInfo)
                    lineInfo = hostFile.readline().strip()
                    hostInfo2 = self.__parseHostInfo(lineInfo)
                    if hostInfo1:
                        hostInfoList.append(hostInfo1)
                    if hostInfo2:
                        hostInfoList.append(hostInfo2)
                return hostInfoList
        pass
    def __parseHostInfo(self,lineInfo):
        lineInfo = lineInfo.strip()
        if len(lineInfo)>0:
            splitResult = lineInfo.split(",")
            if len(splitResult)>=4:
                host = splitResult[2].strip()
                fileDir = splitResult[3].strip()
                return (host,fileDir)
        
if __name__=="__main__":
    print "start"
    hostManager = HostManager()
    hostManager.getHostInfoList("demo056") 
    info = hostManager.getHostInfoList("demo0574") 
    raw_input("input any key to quit")
    pass