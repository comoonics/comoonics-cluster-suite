'''
Created on 20.04.2011

@author: marc
'''
import unittest
from comoonics.analysis.StraceAnalyser import StraceEntry

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRepr(self):
        entry=StraceEntry(timespend='0.000004', pid='9351', timebetween='0.000272', call='brk', result='0x1afed000', params='0')
        print repr(entry)
    def testStr(self):
        entry=StraceEntry(timespend='0.000004', pid='9351', timebetween='0.000272', call='brk', result='0x1afed000', params='0')
        print str(entry)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRepr']
    unittest.main()