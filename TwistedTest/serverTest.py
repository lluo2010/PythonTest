from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet.protocol import Protocol

class QOTD(Protocol):
    NUM = 0
    def __init__(self):
        self.receiveNum = 0;
    def connectionMade(self):
        QOTD.NUM +=1
        #self.transport.write("An apple a day keeps the doctor away:"+str(QOTD.NUM)) 
        #self.transport.loseConnection()
        self.receiveNum = 0;
        print "connection %d time"%(QOTD.NUM)
        
    def dataReceived(self, data):
        print "receive data from client:%s" %data
        self.receiveNum +=1
        if QOTD.NUM==1:
            if self.receiveNum<=2:
                self.transport.write("ack");
                print "ack"
        elif QOTD.NUM==2:
            if self.receiveNum==1:
                self.transport.write("ack");
                print "ack"
        elif QOTD.NUM==3:
            #self.transport.lostConnection()
            reactor.callLater(60*2,reactor.stop)
            print "3 time, stop 60 seconds later"


class QOTDFactory(Factory):
    def buildProtocol(self, addr):
        return QOTD()
    
    
if __name__ =="__main__":
    # 8007 is the port you want to run under. Choose something >1024
    endpoint = TCP4ServerEndpoint(reactor, 9000)
    endpoint.listen(QOTDFactory())
    #reactor.callLater(20,reactor.stop)
    reactor.run()