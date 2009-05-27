from BaseClusterTestClass import baseClusterTestClass
from comoonics.cluster.ComClusterRepository import ClusterMacNotFoundException

import unittest

class test_ClusterRepository(baseClusterTestClass):      
    """
    Methods from RedhatClusterRepository
    """                    
    def setUp(self):
        import os.path
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        super(test_ClusterRepository, self).setUp()
        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

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

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterRepository)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
