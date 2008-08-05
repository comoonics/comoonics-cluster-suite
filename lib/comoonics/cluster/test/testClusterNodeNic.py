from testClusterNode import testClusterNode

import unittest

class testClusterNodeNic(testClusterNode):
    """
    Methods from ComoonicsClusterNodeNic
    """
    def testGetname(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getName(), self.nicValues[i]["name"])
            i = i + 1
            
    def testGetmac(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMac(), self.nicValues[i]["mac"])
            i = i + 1
            
    def testGetip(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getIP(), self.nicValues[i]["ip"])
            i = i + 1
            
    def testGetgateway(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getGateway(), self.nicValues[i]["gateway"])
            i = i + 1
            
    def testGetnetmask(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getNetmask(), self.nicValues[i]["netmask"])
            i = i + 1
            
    def testGetmaster(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMaster(), self.nicValues[i]["master"])
            i = i + 1
            
    def testGetslave(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getSlave(), self.nicValues[i]["slave"])
            i = i + 1

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testClusterNodeNic))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
