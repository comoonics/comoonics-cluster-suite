from BaseClusterTestClass import baseClusterTestClass
from comoonics.cluster.ComClusterRepository import ClusterMacNotFoundException
from comoonics import ComLog

import unittest

class test_ClusterInfo(baseClusterTestClass):    
    """
    Unittests for Clustertools
    """   
    def init(self):
        import os.path
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        super(test_ClusterInfo, self).init()
        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = ClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
        import logging
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        ComLog.setLevel(logging.DEBUG)
        self.clusterInfo.helper.setSimOutput()
        self.nics=list()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
            for nic in node.getNics():
                self.nics.append(nic)
      
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
    
    # Methods from RedhatClusterinfo
    def testQueryvalue(self):
        self.assertEqual(self.createNodeList("name"), self.clusterInfo.queryValue("/cluster/clusternodes/clusternode/@name"))
        
    def testQueryxml(self):
        _tmp1 = "name"
        _tmp2 = "gfs-node1"
        _query='/cluster/clusternodes/clusternode[@'+_tmp1+'="'+_tmp2+'"]'
        node=self.clusterInfo.queryXml(_query)[0]
        self.assertEquals(node.getAttribute(_tmp1), _tmp2, "%s==%s->%s != %s->%s" %(_query, node.getAttribute("name"), node.getAttribute("value"), _tmp1, _tmp2))
        
    def testQueryProperties(self):
        from comoonics.ComDataObject import DataObject
        _tmp1 = "name"
        _tmp2 = "gfs-node1"
        _tmp3 = "name"
        _tmp4 = "eth1"
        result=[ "MASTER=yes", "SLAVE=no", "DELAY=0" ]
        result.sort()
        _query='/cluster/clusternodes/clusternode[@'+_tmp1+'="'+_tmp2+'"]/com_info/eth[@'+_tmp3+'="'+_tmp4+'"]'
        properties=DataObject(self.clusterInfo.queryXml(_query)[0]).getProperties().list().split("\n")
        properties.sort()
        self.assertEquals(properties, result, "%s==%s != %s" %(_query, properties, result))
        
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
#        self.assertRaises(NameError,self.clusterInfo.getFailoverdomainPrefNode, self.failoverdomainValues[2]["name"])
            
    def testGetNodeids(self):
        _tmp1 = self.clusterInfo.getNodeIds()
        _tmp2 = self.createNodeList("id")
        _tmp1.sort()
        _tmp2.sort()
        self.assertEqual(_tmp1, _tmp2)
    
    # Methods from ComoonicsClusterinfo
    def testGetNic(self):
        #except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(self.clusterInfo.getNic(_tmp[i]["mac"]), _tmp[i]["name"])

#    def testGetNicFailure(self):
#        self.assertRaises(ClusterMacNotFoundException, self.clusterInfo.getNic,"murks")
        
    # Methods that deal with non static attributes
    def testName(self):
        self.assertEqual("clu_generix", self.clusterInfo.name)
        
    def testGeneration(self):
        self.assertEqual("900", self.clusterInfo.generation)
    def testQuorate(self):
        self.assertEqual("1", self.clusterInfo.quorum_quorate)
    def testQuorumGroupMember(self):
        self.assertEqual("1", self.clusterInfo.quorum_groupmember)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterInfo)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
