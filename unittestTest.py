'''
Created on May 12, 2013

@author: lluo
'''
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        print "setup"
    def tearDown(self):
        print "tearDown"
    def fun(self):
        self.assertTrue(1==1, "fun test")
    def testName(self):
        self.failIf(1!=1,"test name") 
    def test2(self):
        self.assertEqual(1, 2, "test2")

'''
class Test2(unittest.TestCase):
    def runTest(self):
        self.assertTrue(1!=1, "test2")
'''

def getTestSuite():
    suite= unittest.TestSuite()
    suite.addTest(Test("testName"))
    suite.addTest(Test("test2"))
    return suite
def getTestSuite2():
    tests = ["testName","test2"]
    suite = unittest.TestSuite(map(Test,tests))
    return suite
def getTestSuite3():
    suite1 = unittest.TestSuite()
    suite1.addTest(Test("testName"))
    suite2 = unittest.TestSuite()
    suite2.addTest(Test("test2"))
    suite = unittest.TestSuite([suite1,suite2])
    return suite
def getTestSuite4():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    return suite
def testxxx():
    a = 1
    b = 2
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    runner = unittest.TextTestRunner() 
    #runner.run(getTestSuite())
    #runner.run(getTestSuite3())
    runner.run(getTestSuite2())
    #runner.run(getTestSuite4())