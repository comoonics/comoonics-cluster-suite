from BaseClusterTestClass import baseClusterTestClass
from comoonics.cluster import getClusterRepository, ClusterMacNotFoundException

import unittest

class test_ClusterRepository(baseClusterTestClass):      
    """
    Methods from RedhatClusterRepository
    """                    
    def setUp(self):
        import os.path
        super(test_ClusterRepository, self).setUp()
        #create comclusterRepository Object
        self.clusterRepository = getClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

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
        
    def testStr(self):
        self.assertEquals(str(self.clusterRepository), "ComoonicsClusterRepository(nodes: 3)")
        
    def testClusterInfoClass(self):
        from comoonics.cluster.ComClusterInfo import ComoonicsClusterInfo
        self.assertEquals(self.clusterRepository.getClusterInfoClass(), ComoonicsClusterInfo)

class test_ClusterRepository2(unittest.TestCase):      
    """
    Methods from RedhatClusterRepository
    """                    
    def setUp(self):
        self.clusterRepository = getClusterRepository()
    def testCreateEmpty(self):
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        #create comclusterRepository Object
        self.assertTrue(isinstance(self.clusterRepository, ClusterRepository))
        
    def testStr(self):
        self.assertEquals(str(self.clusterRepository), "ClusterRepository(nodes: 0)")

    def testClusterInfoClass(self):
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        self.assertEquals(self.clusterRepository.getClusterInfoClass(), ClusterInfo)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterRepository)
        test_support.run_unittest(test_ClusterRepository2)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
