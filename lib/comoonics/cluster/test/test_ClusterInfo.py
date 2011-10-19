from BaseClusterTestClass import baseClusterTestClass
from comoonics import ComLog
from comoonics.cluster import getClusterRepository, getClusterInfo

import unittest

class test_ClusterInfo(baseClusterTestClass):    
    """
    Unittests for Clustertools
    """   
    def init(self):
        import os.path
        import logging
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        super(test_ClusterInfo, self).init()
        #create comclusterRepository Object
        self.clusterRepository = getClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = getClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
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
        self.assertEqual(self.clusterInfo.getNodeIdentifiers('id'), self.nodeValues.keys())
        _tmp1 = self.clusterInfo.getNodeIdentifiers('name')
        _tmp2 = map(lambda node: node["name"], self.nodeValues.values())
        _tmp1.sort()
        _tmp2.sort()
        self.assertEqual(_tmp1, _tmp2)
    
    # Methods from RedhatClusterinfo
    def testQueryvalue1(self):
        list1=map(lambda node: node["name"], self.nodeValues.values())
        list2=self.clusterInfo.queryValue("/cluster/clusternodes/clusternode/@name")
        list1.sort()
        list2.sort()
        self.assertEqual(list1, list2)
        
    def testQueryvalue2(self):
        self.assertEqual(len(map(lambda node: node["name"], self.nodeValues.values())), self.clusterInfo.queryValue("count(/cluster/clusternodes/clusternode/@name)")[0])
        
    def testQueryxml(self):
        _tmp1 = "name"
        _tmp2 = "gfs-node1"
        _query='/cluster/clusternodes/clusternode[@'+_tmp1+'="'+_tmp2+'"]'
        node=self.clusterInfo.queryXml(_query)[0]
        self.assertEquals(node.getAttribute(_tmp1), _tmp2, "%s==%s->%s != %s->%s" %(_query, node.getAttribute("name"), node.getAttribute("value"), _tmp1, _tmp2))
        
    def testQueryxml2(self):
        _query='/cluster/doesnotexist'
        result=self.clusterInfo.queryXml(_query)
        self.assertEquals(result, [], "Query %s should return false as result but does not. %s" %(_query, result))
        
    def testQueryProperties(self):
        from comoonics.ComDataObject import DataObject
        _tmp1 = "name"
        _tmp2 = "gfs-node1"
        _tmp3 = "name"
        _tmp4 = "eth1"
        result=[ "MASTER=yes", "SLAVE=no", "DELAY=0" ]
        result.sort()
        _query='/cluster/clusternodes/clusternode[@'+_tmp1+'="'+_tmp2+'"]/com_info/eth[@'+_tmp3+'="'+_tmp4+'"]'
        propertieselement=self.clusterInfo.queryXml(_query)[0]
        properties=DataObject(propertieselement).getProperties().list().split("\n")
        properties.sort()
        self.assertEquals(properties, result, "%s==%s != %s" %(_query, properties, result))
        
    def testGetnode(self):
        """
        Requires proper function of method getName() 
        """
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getName(), self.nodeValues[node.getId()]["name"])
        
    def testGetname(self):
        for node in self.clusterInfo.getNodes():
            for nic in node.getNics():
                if self.nodeValues[node.getId()][nic.getName()].has_key("mac") and self.nodeValues[node.getId()][nic.getName()]["mac"]!= "":
                    self.assertEquals(self.clusterInfo.getNodeName(self.nodeValues[node.getId()][nic.getName()]["mac"]),
                                                                node.getName())
        
    def testGetid(self):
        for node in self.clusterInfo.getNodes():
            for nic in node.getNics():
                if self.nodeValues[node.getId()][nic.getName()].has_key("mac") and self.nodeValues[node.getId()][nic.getName()]["mac"]!= "":
                    self.assertEquals(self.clusterInfo.getNodeId(self.nodeValues[node.getId()][nic.getName()]["mac"]),
                                                              node.getId())
            
    def testGetFailoverdomainnodes(self):
        for i in range(len(self.failoverdomainValues)):
            self.assertEqual(self.clusterInfo.getFailoverdomainNodes(self.failoverdomainValues[i]["name"]), self.failoverdomainValues[i]["members"])
            
    def testGetFailoverdomainprefnode(self):
        for i in range(len(self.failoverdomainValues)-1):
            self.assertEqual(self.clusterInfo.getFailoverdomainPrefNode(self.failoverdomainValues[i]["name"]), self.failoverdomainValues[i]["prefnode"])
#        self.assertRaises(NameError,self.clusterInfo.getFailoverdomainPrefNode, self.failoverdomainValues[2]["name"])
            
    def testGetNodeids(self):
        _tmp1 = self.clusterInfo.getNodeIds()
        _tmp2 = self.nodeValues.keys()
        _tmp1.sort()
        _tmp2.sort()
        self.assertEqual(_tmp1, _tmp2)
    
    # Methods from ComoonicsClusterinfo
    def testGetNic(self):
        for node in self.clusterInfo.getNodes():
            for nic in node.getNics():
                if self.nodeValues[node.getId()][nic.getName()].has_key("mac") and self.nodeValues[node.getId()][nic.getName()]["mac"] != "":
                    self.assertEquals(self.clusterInfo.getNic(self.nodeValues[node.getId()][nic.getName()]["mac"]),
                                                              nic.getName())
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
