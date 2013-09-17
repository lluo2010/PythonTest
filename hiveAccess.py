import sys
sys.path.append(r'C:\Python27\Lib\site-packages')
from hive_service import ThriftHive
from hive_service.ttypes import HiveServerException
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def hiveExe(sql):
    print "start"
    try:
        transport = TSocket.TSocket('nn2.telx.7sys.net', 10000) 
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = ThriftHive.Client(protocol)
        print "-before open"
        transport.open()
        print "-after open"

        client.execute(sql)
        print "after execute"

        print "The return value is : " 
        print client.fetchAll()
        print "............"
        transport.close()
    except Thrift.TException, tx:
        print '%s' % (tx.message)
    print "end"

if __name__ == '__main__':
    hiveExe("select imei from user_groups where imei='355880051013502'")