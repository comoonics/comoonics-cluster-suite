from BaseClusterTestClass import baseClusterTestClass
from comoonics.cluster.ComClusterRepository import ClusterMacNotFoundException

import unittest

class testClusterRepository(baseClusterTestClass):      
    """
    Methods from RedhatClusterRepository
    """                    
    def testGetnodename(self):
        # except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodename"], str(self.clusterRepository.getNodeName(_tmp[i]["mac"])))
        self.assertRaises(ClusterMacNotFoundException, self.clusterRepository.getNodeName,"murks")
        
    def testGetnodeid(self):
        # except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodeid"], str(self.clusterRepository.getNodeId(_tmp[i]["mac"])))
        self.assertRaises(ClusterMacNotFoundException, self.clusterRepository.getNodeId,"murks")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testClusterRepository))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
