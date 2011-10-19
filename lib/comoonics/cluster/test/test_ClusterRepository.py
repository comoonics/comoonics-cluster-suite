from BaseClusterTestClass import baseClusterTestClass
import comoonics.cluster

import unittest

class test_ClusterRepository(baseClusterTestClass):      
    """
    Methods from RedhatClusterRepository
    """                    
    def setUp(self):
        import os.path
        super(test_ClusterRepository, self).setUp()
        #create comclusterRepository Object
        self.clusterRepository = comoonics.cluster.getClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

    def testGetnodename(self):
        # except first nic because it does not have a mac-address
        for node in self.clusterRepository.nodeIdMap.values():
            for nic in node.getNics():
                if not self.nodeValues[node.getId()][nic.getName()].has_key("mac") or self.nodeValues[node.getId()][nic.getName()]["mac"] == "":
                    self.failUnlessRaises(comoonics.cluster.ClusterMacNotFoundException, self.clusterRepository.getNodeName, self.nodeValues[node.getId()][nic.getName()]["mac"])
                else:
                    self.assertEqual(self.clusterRepository.getNodeName(self.nodeValues[node.getId()][nic.getName()]["mac"]), 
                                     self.nodeValues[node.getId()]["name"])
        self.assertRaises(comoonics.cluster.ClusterMacNotFoundException, self.clusterRepository.getNodeId,"murks")
        # except first nic because it does not have an mac-address
        
    def testGetnodeid(self):
        # except first nic because it does not have a mac-address
        for node in self.clusterRepository.nodeIdMap.values():
            for nic in node.getNics():
                if not self.nodeValues[node.getId()][nic.getName()].has_key("mac") or self.nodeValues[node.getId()][nic.getName()]["mac"] == "":
                    self.failUnlessRaises(comoonics.cluster.ClusterMacNotFoundException, self.clusterRepository.getNodeId, self.nodeValues[node.getId()][nic.getName()]["mac"])
                else:
                    self.assertEqual(self.clusterRepository.getNodeId(self.nodeValues[node.getId()][nic.getName()]["mac"]), 
                                     self.nodeValues[node.getId()]["id"])
        self.assertRaises(comoonics.cluster.ClusterMacNotFoundException, self.clusterRepository.getNodeId,"murks")
        
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
        self.clusterRepository = comoonics.cluster.getClusterRepository(maxnodeidnum=5)
    def testCreateEmpty(self):
        from comoonics.cluster.ComClusterRepository import SimpleComoonicsClusterRepository
        #create comclusterRepository Object
        self.assertTrue(isinstance(self.clusterRepository, SimpleComoonicsClusterRepository))
        
    def testStr(self):
        self.assertEquals(str(self.clusterRepository), "SimpleComoonicsClusterRepository(nodes: 5)")

    def testClusterInfoClass(self):
        from comoonics.cluster.ComClusterInfo import SimpleComoonicsClusterInfo
        self.assertEquals(self.clusterRepository.getClusterInfoClass(), SimpleComoonicsClusterInfo)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterRepository)
        test_support.run_unittest(test_ClusterRepository2)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
