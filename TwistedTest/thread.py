from twisted.internet import reactor,threads
import threading

def aSillyBlockingMethod(x):
    import time
    time.sleep(2)
    print "----"+threading.current_thread().getName()
    print "--********"+x
    

print "main thread:"+threading.current_thread().getName()
threads.deferToThread(aSillyBlockingMethod,"1")
threads.deferToThread(aSillyBlockingMethod,"2")
threads.deferToThread(aSillyBlockingMethod,"3")

reactor.suggestThreadPoolSize(1)
reactor.run()

