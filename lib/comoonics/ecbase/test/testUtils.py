'''
Created on 15.02.2011

@author: marc
'''
import unittest
from comoonics.ecbase.ComUtils import *

class Test(unittest.TestCase):


    def testGrepInLines(self):
        lines=["eine eins", "eine zwei", "keine drei"]
        self.assertEquals(["eins", "zwei" ], grepInLines(lines, "^eine (.*)"))

    def testIsInt1(self):
        one="1"
        self.assertTrue(isInt(one))
    def testIsInt2(self):
        self.assertFalse(isInt("sds"))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testUtils']
    unittest.main()