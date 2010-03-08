'''
Created on Mar 3, 2010

@author: marc
'''
import unittest
from comoonics.scsi import ComSCSI

class Test(unittest.TestCase):
    def testSCSIHosts(self):
        ComSCSI.getSCSIHosts()
        
    def testFCHosts(self):
        ComSCSI.getFCHosts()

    def testFCRescan(self):
        for host in ComSCSI.getFCHosts():
            ComSCSI.rescan(host)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()