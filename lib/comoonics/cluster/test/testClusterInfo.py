from BaseClusterTestClass import baseClusterTestClass
from comoonics.cluster.ComClusterRepository import ClusterMacNotFoundException

import unittest

class testClusterInfo(baseClusterTestClass):    
    """
    Unittests for Clustertools
    """   
    def testGetnodes(self):
        """
        Tests only correct type of list and content as well as length of list.
        Does not check if the nodes in the list are correct.
        """
        _tmp = self.clusterInfo.getNodes()
        self.assertEqual(type(_tmp), type([]))
        self.assertEqual(len(_tmp), len(self.nodeValues))
        for node in _tmp:
            self.assertEqual(str(type(node)), "<class 'comoonics.cluster.ComClusterNode.ComoonicsClusterNode'>")
            
    def testGetnodeidentifiers(self):
        self.assertEqual(self.clusterInfo.getNodeIdentifiers('name'), self.createNodeList("name"))
        _tmp1 = self.clusterInfo.getNodeIdentifiers('id')
        _tmp2 = self.createNodeList("id")
        _tmp1.sort()
        _tmp2.sort()
        self.assertEqual(_tmp1, _tmp2)
    
    """
    Methods from RedhatClusterinfo
    """
    def testQueryvalue(self):
        self.assertEqual(self.createNodeList("name"), self.clusterInfo.queryValue("/cluster/clusternodes/clusternode/@name"))
        
    def testQueryxml(self):
        _tmp = " name='gfs-node1'\n"
        self.assertEqual(_tmp, str(self.clusterInfo.queryXml('/cluster/clusternodes/clusternode/@name')))
        
    def testGetnode(self):
        """
        Requires proper function of method getName() 
        """
        for nodename in self.createNodeList("name"):
            self.assertEqual(self.clusterInfo.getNode(nodename).getName(), nodename)
        
    def testGetname(self):
        #except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodename"], str(self.clusterInfo.getNodeName(_tmp[i]["mac"])))
        
    def testGetid(self):
        #except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodeid"], str(self.clusterInfo.getNodeId(_tmp[i]["mac"])))
            
    def testGetFailoverdomainnodes(self):
        for i in range(len(self.failoverdomainValues)):
            self.assertEqual(self.clusterInfo.getFailoverdomainNodes(self.failoverdomainValues[i]["name"]), self.failoverdomainValues[i]["members"])
            
    def testGetFailoverdomainprefnode(self):
        for i in range(len(self.failoverdomainValues)-1):
            self.assertEqual(self.clusterInfo.getFailoverdomainPrefNode(self.failoverdomainValues[i]["name"]), self.failoverdomainValues[i]["prefnode"])
        self.assertRaises(NameError,self.clusterInfo.getFailoverdomainPrefNode, self.failoverdomainValues[2]["name"])
            
    def testGetNodeids(self):
        _tmp1 = self.clusterInfo.getNodeIds()
        _tmp2 = self.createNodeList("id")
        _tmp1.sort()
        _tmp2.sort()
        self.assertEqual(_tmp1, _tmp2)
    
    """
    Methods from ComoonicsClusterinfo
    """
    def testGetNic(self):
        #except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(self.clusterInfo.getNic(_tmp[i]["mac"]), _tmp[i]["name"])
        self.assertRaises(ClusterMacNotFoundException, self.clusterInfo.getNic,"murks")
        
    """
    Methods that deal with non static attributes
    """
    def testName(self):
        self.assertEqual("clu_generix", self.clusterInfo.name)
        
    def testGeneration(self):
        self.assertEqual("900", self.clusterInfo.generation)
    def testQuorate(self):
        self.assertEqual("1", self.clusterInfo.quorum_quorate)
    def testQuorumGroupMember(self):
        self.assertEqual("1", self.clusterInfo.quorum_groupmember)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testClusterInfo))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
