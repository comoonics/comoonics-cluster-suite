'''
Created on Mar 3, 2010

@author: marc
'''
import unittest
from comoonics.scsi.ComSCSIResolver import SCSIWWIDResolver, FCTransportResolver 

class Test(unittest.TestCase):
    def testSCSIWWIDResolver(self):
        res=SCSIWWIDResolver()
        print "SCSIWWIDResolver.key: "+res.getKey()
    
    def testFCTransportResolver(self):
        res=FCTransportResolver()
        print "SCSIWWIDResolver.key: "+res.getKey()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()