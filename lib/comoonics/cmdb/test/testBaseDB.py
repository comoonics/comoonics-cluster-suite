'''
Created on 05.04.2011

@author: marc
'''
import unittest
from comoonics.cmdb.ComBaseDB import BaseDB

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        testlist=[ "a", "b", "c", "d" ]
        self.assertEquals(BaseDB.BinOperatorFromList(testlist, "!="), ['a!=b', 'a!=c', 'a!=d', 'b!=c', 'b!=d', 'c!=d'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()