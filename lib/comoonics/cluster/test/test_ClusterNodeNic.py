from BaseClusterTestClass import baseClusterTestClass

import unittest
from comoonics.cluster import getClusterRepository, getClusterInfo
from comoonics import ComSystem

class test_ClusterNodeNic(baseClusterTestClass):
    """
    Methods from ComoonicsClusterNodeNic
    """
    def init(self):
        import os.path
        ComSystem.setExecMode(ComSystem.SIMULATE)
        super(test_ClusterNodeNic, self).init()
        #create comclusterRepository Object
        self.clusterRepository = getClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = getClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
        self.clusterInfo.helper.setSimOutput()
    
    def testGetname(self):
        self._testNicGetName("name")
            
    def testGetmac(self):
        self._testNicGetName("mac")
            
    def testGetip(self):
        self._testNicGetName("ip", "getIP")
            
    def testGetgateway(self):
        self._testNicGetName("gateway")
            
    def testGetnetmask(self):
        self._testNicGetName("netmask")
            
    def testGetmaster(self):
        self._testNicGetName("master")
                    
    def testGetslave(self):
        self._testNicGetName("slave")

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterNodeNic)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
