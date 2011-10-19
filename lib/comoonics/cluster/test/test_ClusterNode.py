from BaseClusterTestClass import baseClusterTestClass

import unittest
from comoonics.cluster import getClusterRepository, getClusterInfo
from comoonics import ComSystem

class test_ClusterNode(baseClusterTestClass):
    """
    Methods from RedhatClusterNode
    """
    def init(self):
        import os.path
        ComSystem.setExecMode(ComSystem.SIMULATE)
        super(test_ClusterNode, self).init()
        #create comclusterRepository Object
        self.clusterRepository = getClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = getClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
        self.clusterInfo.helper.setSimOutput()
        self.nics=list()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
            for nic in node.getNics():
                self.nics.append(nic)
      
    def testGetname(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getName(), self.nodeValues[node.getId()]["name"])
            
    def testGetid(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getId(), self.nodeValues[node.getId()]["id"])
            
    def testGetvotes(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getVotes(), self.nodeValues[node.getId()]["votes"])
                    
    """
    Methods from ComoonicsClusterNode
    """
    def testGetnic(self):
        pass
    
    def testRootvolume(self):
        self.assertEqual(self.clusterRepository.nodeIdMap["1"].getRootvolume(), self.nodeValues["1"]["rootvolume"])
    
    def testRootfs(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getRootFs(), self.nodeValues[node.getId()]["rootfs"])
            
    def testGetmountopts(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getMountopts(), self.nodeValues[node.getId()]["mountopts"])
    
    def testGetsyslog(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getSyslog(), self.nodeValues[node.getId()]["syslog"])
    
    def testGetscsifailover(self):
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getScsifailover(), self.nodeValues[node.getId()]["scsifailover"])
    
    def testGetnics(self):
        """
        Does test if return value is list, list values are NodeNics and number of list values
        Does not check if NodeNics in list are correct
        """
        
        for node in self.clusterInfo.getNodes():
            _nics = node.getNics()
            
            # test if return type of tested function is list
            # test if type of list values is ComoonicsClusterNodeNic
            self.assertEqual(type(_nics), type([]))
            for nic in _nics:
                self.assertEqual(type(nic).__name__, "ComoonicsClusterNodeNic")
                self.assertEqual(nic.getName(), self.nodeValues[node.getId()][nic.getName()]["name"])

    def testGetnonstatics(self):
        for node in self.clusterInfo.getNodes():
            for attr in node.non_statics.keys():
                self.assert_(getattr(node, attr) in ["1", "0" ], "testGetnonstatics(node=%s, attr=%s)%s!=%s" %(node.getName(), attr, getattr(node, attr), ["1", "0"]))

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterNode)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
