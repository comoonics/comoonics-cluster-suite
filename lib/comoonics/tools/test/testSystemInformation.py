'''
Created on 24.03.2011

@author: marc
'''
import unittest
from comoonics.tools.ComSystemInformation import getSystemInformation

class Test(unittest.TestCase):


    def setUp(self):
        self.systeminformation=getSystemInformation()


    def tearDown(self):
        pass


    def testgetFeatures(self):
        self.failUnless("linux" in self.systeminformation.getFeatures(), "Systeminformation does not return linux as feature.")
        
    def testArchitecture(self):
        self.failUnless(self.systeminformation.getArchitecture(), "Could not determine the architecture of this system.")
            
    def testName(self):
        self.failUnless(self.systeminformation.getName(), "Could not determine the name of this system.")
            
    def testUptime(self):
        self.failUnless(self.systeminformation.getUptime(), "Could not determine the uptime of this system.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()