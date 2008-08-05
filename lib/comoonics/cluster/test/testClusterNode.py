from BaseClusterTestClass import baseClusterTestClass

import unittest

class testClusterNode(baseClusterTestClass):
    """
    Methods from RedhatClusterNode
    """
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
        i = 0
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getRootFs(), self.nodeValues[i]["rootfs"])
            i = i + 1
            
    def testGetmountopts(self):
        i = 0
        for node in self.clusterInfo.getNodes():
            self.assertEqual(node.getMountopts(), self.nodeValues[i]["mountopts"])
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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testClusterNode))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
