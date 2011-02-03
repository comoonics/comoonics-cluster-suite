from BaseClusterTestClass import baseClusterTestClass

import unittest

class test_ClusterNode(baseClusterTestClass):
    """
    Methods from RedhatClusterNode
    """
    def init(self):
        import os.path
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        super(test_ClusterNode, self).init()
        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = ClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
        self.clusterInfo.helper.setSimOutput()
        self.nics=list()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
            for nic in node.getNics():
                self.nics.append(nic)
      
    def testGetname(self):
        _list = self.createNodeList("name")
        _list.reverse()
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getName(), _list.pop())
            
    def testGetid(self):
        _list = self.createNodeList("id")
        _list.reverse()
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getId(), _list.pop())
            
    def testGetvotes(self):
        _list = self.createNodeList("votes")
        _list.reverse()
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getVotes(), _list.pop())
                    
    """
    Methods from ComoonicsClusterNode
    """
    def testGetnic(self):
        pass
    
    def testRootvolume(self):
        self.assertRaises(IndexError, self.clusterInfo.getNodes()[0].getRootvolume)
        self.assertEqual(self.clusterInfo.getNodes()[1].getRootvolume(), self.nodeValues[1]["rootvolume"])
    
    def testRootfs(self):
        self.assertRaises(IndexError, self.clusterInfo.getNodes()[0].getRootFs)
        i = 0
        for node in self.clusterInfo.getNodes():
            if i>0:
                self.assertEqual(node.getRootFs(), self.nodeValues[i]["rootfs"])
#            else:
#                self.assertRaises(IndexError, node.getRootFs)
            i = i + 1
            
    def testGetmountopts(self):
        self.assertRaises(IndexError, self.clusterInfo.getNodes()[0].getMountopts)
        i = 0
        for node in self.clusterInfo.getNodes():
            if i>0:
                self.assertEqual(node.getMountopts(), self.nodeValues[i]["mountopts"])
#            else:
#                self.assertRaises(IndexError, node.getMountopts())
            i = i + 1
    
    def testGetsyslog(self):
        i = 0
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getSyslog(), self.nodeValues[i]["syslog"])
            i = i + 1
    
    def testGetscsifailover(self):
        i = 0
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getScsifailover(), self.nodeValues[i]["scsifailover"])
            i = i + 1
    
    def testGetnics(self):
        """
        Does test if return value is list, list values are NodeNics and number of list values
        Does not check if NodeNics in list are correct
        """
        
        for node in self.clusterInfo.getNodes():
            _nics = node.getNics()
            
            # prepare predefined ordered list of nicnames to compare
            _nodenames = []
            for i in range(len(self.nicValues)):
                if self.nicValues[i]["nodename"] == node.getName():
                    _nodenames.append(self.nicValues[i]["name"])         
            
            # test if return type of tested function is list
            # test if type of list values is ComoonicsClusterNodeNic
            self.assertEqual(type(_nics), type([]))
            for nic in _nics:
                self.assertEqual(type(nic).__name__, "ComoonicsClusterNodeNic")
                
            # test order of nics in list
            i = 0
            for nic in _nics:
                self.assertEqual(nic.getName(), _nodenames[i])
                i = i + 1

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
