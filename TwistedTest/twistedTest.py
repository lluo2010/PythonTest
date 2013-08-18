from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor

class MyProtocol(Protocol):
    def __init__(self):
        pass
        

    def dataReceived(self, data):
        print "data received %s" %data
        if self.factory:
            print self.factory
       
    #Called when a connection is made.
    def connectionMade(self):
        print "MyProtocol::connection established"
   
    #Called when the connection is shut down.
    def connectionLost(self, reason):
        #self.poemReceived(self.poem)
        print "MyProtocol::connect lost"

class MyClientFactory(ClientFactory):
    '''Factory.buildProtocol() will use "protocol" to create Protocol
     instance and assign this factory to protocol.factory'''
    protocol = MyProtocol

    def __init__(self):
        pass

    def clientConnectionFailed(self, connector, reason):
        print "MyClientFactory::failed to connect"
   
    #Called when an established connection is lost.
    def clientConnectionLost(self, connector, reason):
        print "MyClientFactory::client connection is lost"



def testMain():
    myFactory = MyClientFactory()
    host = "127.0.0.1"
    port = 60000
    reactor.connectTCP(host, port, myFactory)
    reactor.run()

if __name__ == '__main__':
    print "start test"
    testMain()
    print "finish test"
