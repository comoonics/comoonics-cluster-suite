"""
comoonics-cluster-py unittests


This module provides unittests for the package cluster

"""

__version__ = "$Revision: 1.1 $"

import comoonics
from comoonics.cluster.ComClusterInfo import *
from comoonics.cluster.ComClusterNode import *
from comoonics.cluster.ComClusterNodeNic import *
from comoonics.cluster.ComClusterRepository import *

import sys
sys.path.append("./lib")

import unittest

class testClusterTools(unittest.TestCase):
    """
    Unittests for Clustertools
    """
    def setUp(self):
        """
        set up data used in the tests.
        setUp is called before each test function execution.
        """        
        # create Reader object
        reader = Sax2.Reader()

        # parse the document and create clusterrepository object
        # can use only cluster2.conf for test, cluster.conf MUST cause an not 
        # handled exception (because lack of a device name)
        my_file = os.fdopen(os.open("cluster2.conf", os.O_RDONLY))
        doc = reader.fromStream(my_file)
        my_file.close()
        element = xpath.Evaluate('/cluster', doc)[0]

        clusternode_path = "/cluster/clusternodes/clusternode"
        self.nodes = []
        for node in xpath.Evaluate(clusternode_path, doc):
            self.nodes.append(ComoonicsClusterNode(node, doc))

        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository(element, doc)

        #create comclusterinfo object
        self.clusterInfo = ClusterInfo(self.clusterRepository)
        
        #get comclusternode objects
        self._nodes = self.clusterInfo.getNodes()
        
        #create comclusternodenic objects
        self.nics = []        
        for element in xpath.Evaluate("/cluster/clusternodes/clusternode/com_info/eth", doc):
        # create example comnode
            self.nics.append(ComoonicsClusterNodeNic(element, doc))
        
        """
        The following specifications must match these of the used clusterconfiguration
        """
        
        """Preparation of failoverdomains"""
        self.failoverdomainValues = []
        
        self.failoverdomainValues.append({})
        self.failoverdomainValues[0]["name"] = "testdomain1"
        self.failoverdomainValues[0]["members"] = ['member1', 'member2', 'member3', 'member4']
        self.failoverdomainValues[0]["prefnode"] = "member1"
        
        self.failoverdomainValues.append({})
        self.failoverdomainValues[1]["name"] = "testdomain2"
        self.failoverdomainValues[1]["members"] = ['member1a', 'member2a', 'member3a', 'member4a']
        self.failoverdomainValues[1]["prefnode"] = "member4a"
        
        self.failoverdomainValues.append({})
        self.failoverdomainValues[2]["name"] = "testdomain3"
        self.failoverdomainValues[2]["members"] = []
        self.failoverdomainValues[2]["prefnode"] = ""

        """Perparation of nics"""
        self.nicValues = []
        
        self.nicValues.append({})
        self.nicValues[0]["name"] = "eth0"
        self.nicValues[0]["nodename"] = "gfs-node1"
        self.nicValues[0]["nodeid"] = "1"
        self.nicValues[0]["mac"] = ""
        self.nicValues[0]["ip"] = ""
        self.nicValues[0]["gateway"] = ""
        self.nicValues[0]["netmask"] = ""
        self.nicValues[0]["master"] = ""
        self.nicValues[0]["slave"] = ""
        
        self.nicValues.append({})
        self.nicValues[1]["name"] = "eth0"
        self.nicValues[1]["nodename"] = "gfs-node2"
        self.nicValues[1]["nodeid"] = "2"
        self.nicValues[1]["mac"] = "00:0C:29:3C:XX:XX"
        self.nicValues[1]["ip"] = "10.0.0.2"
        self.nicValues[1]["gateway"] = ""
        self.nicValues[1]["netmask"] = "255.255.255.0"
        self.nicValues[1]["master"] = "bond0"
        self.nicValues[1]["slave"] = "yes"
        
        self.nicValues.append({})
        self.nicValues[2]["name"] = "eth1"
        self.nicValues[2]["nodename"] = "gfs-node2"
        self.nicValues[2]["nodeid"] = "2"
        self.nicValues[2]["mac"] = "00:0C:29:3C:XX:XY"
        self.nicValues[2]["ip"] = "10.0.0.3"
        self.nicValues[2]["gateway"] = "1.2.3.4"
        self.nicValues[2]["netmask"] = "255.255.255.0"
        self.nicValues[2]["master"] = ""
        self.nicValues[2]["slave"] = ""
        
        self.nicValues.append({})
        self.nicValues[3]["name"] = "bond0"
        self.nicValues[3]["nodename"] = "gfs-node3"
        self.nicValues[3]["nodeid"] = ""
        self.nicValues[3]["mac"] = "00:17:A4:10:7B:7D"
        self.nicValues[3]["ip"] = "192.168.10.22"
        self.nicValues[3]["gateway"] = "192.168.10.1"
        self.nicValues[3]["netmask"] = "255.255.255.0"
        self.nicValues[3]["master"] = ""
        self.nicValues[3]["slave"] = ""
        
        self.nicValues.append({})
        self.nicValues[4]["name"] = "eth0"
        self.nicValues[4]["nodename"] = "gfs-node3"
        self.nicValues[4]["nodeid"] = ""
        self.nicValues[4]["mac"] = "00:17:A4:10:7B:7E"
        self.nicValues[4]["ip"] = ""
        self.nicValues[4]["gateway"] = ""
        self.nicValues[4]["netmask"] = ""
        self.nicValues[4]["master"] = "bond0"
        self.nicValues[4]["slave"] = "yes"
        
        self.nicValues.append({})
        self.nicValues[5]["name"] = "bond0.45"
        self.nicValues[5]["nodename"] = "gfs-node3"
        self.nicValues[5]["nodeid"] = ""
        self.nicValues[5]["mac"] = "00:17:A4:10:7B:7C"
        self.nicValues[5]["ip"] = "192.168.254.233"
        self.nicValues[5]["gateway"] = ""
        self.nicValues[5]["netmask"] = "255.255.255.255"
        self.nicValues[5]["master"] = ""
        self.nicValues[5]["slave"] = ""
        
        """Preparation of nodes"""
        self.nodeValues = []
        
        self.nodeValues.append({})
        self.nodeValues[0]["name"] = "gfs-node1"
        self.nodeValues[0]["id"] = "1"
        self.nodeValues[0]["votes"] = "1"
        self.nodeValues[0]["rootvolume"] = ""
        self.nodeValues[0]["rootfs"] = "gfs"
        self.nodeValues[0]["mountopts"] = "noatime,nodiratime"
        self.nodeValues[0]["syslog"] = ""
        self.nodeValues[0]["scsifailover"] = "driver"
        
        self.nodeValues.append({})
        self.nodeValues[1]["name"] = "gfs-node2"
        self.nodeValues[1]["id"] = "2"
        self.nodeValues[1]["votes"] = "3"
        self.nodeValues[1]["rootvolume"] = "/dev/VG_SHAREDROOT/LV_SHAREDROOT"
        self.nodeValues[1]["rootfs"] = "meinfs"
        self.nodeValues[1]["mountopts"] = "someopts"
        self.nodeValues[1]["syslog"] = "gfs-node1"
        self.nodeValues[1]["scsifailover"] = "gfs-node1"
        
        self.nodeValues.append({})
        self.nodeValues[2]["name"] = "gfs-node3"
        self.nodeValues[2]["id"] = ""
        self.nodeValues[2]["votes"] = "1"
        self.nodeValues[2]["rootvolume"] = ""
        self.nodeValues[2]["rootfs"] = "gfs"
        self.nodeValues[2]["mountopts"] = "noatime,nodiratime"
        self.nodeValues[2]["syslog"] = ""
        self.nodeValues[2]["scsifailover"] = "driver"
        
    def createNodeList(self, key):
        _list = []
        for i in range(len(self.nodeValues)):
            _list.append(self.nodeValues[i][key])
        return _list
        
class testClusterInfo(testClusterTools):
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
        self.assertRaises(comoonics.cluster.ComClusterInfo.ClusterMacNotFoundException, self.clusterInfo.getNic,"murks")
        
class testClusterNode(testClusterTools):
    """
    Methods from RedhatClusterNode
    """
    def testGetname(self):
        _list = self.createNodeList("name")
        _list.reverse()
        for node in self.nodes:
            self.assertEqual(node.getName(), _list.pop())
            
    def testGetid(self):
        _list = self.createNodeList("id")
        _list.reverse()
        for node in self.nodes:
            self.assertEqual(node.getId(), _list.pop())
            
    def testGetvotes(self):
        _list = self.createNodeList("votes")
        _list.reverse()
        for node in self.nodes:
            self.assertEqual(node.getVotes(), _list.pop())
                    
    """
    Methods from ComoonicsClusterNode
    """
    def testGetnic(self):
        pass
    
    def testRootvolume(self):
        self.assertRaises(IndexError, self.nodes[0].getRootvolume)
        self.assertEqual(self.nodes[1].getRootvolume(), self.nodeValues[1]["rootvolume"])
    
    def testRootfs(self):
        i = 0
        for node in self.nodes:
            self.assertEqual(node.getRootFs(), self.nodeValues[i]["rootfs"])
            i = i + 1
            
    def testGetmountopts(self):
        i = 0
        for node in self.nodes:
            self.assertEqual(node.getMountopts(), self.nodeValues[i]["mountopts"])
            i = i + 1
    
    def testGetsyslog(self):
        i = 0
        for node in self.nodes:
            self.assertEqual(node.getSyslog(), self.nodeValues[i]["syslog"])
            i = i + 1
    
    def testGetscsifailover(self):
        i = 0
        for node in self.nodes:
            self.assertEqual(node.getScsifailover(), self.nodeValues[i]["scsifailover"])
            i = i + 1
    
    def testGetnics(self):
        """
        Does test if return value is list, list values are NodeNics and number of list values
        Does not check if NodeNics in list are correct
        """
        
        for node in self.nodes:
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
            
class testClusterNodeNic(testClusterTools):
    """
    Methods from ComoonicsClusterNodeNic
    """
    def testGetname(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getName(), self.nicValues[i]["name"])
            i = i + 1
            
    def testGetmac(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMac(), self.nicValues[i]["mac"])
            i = i + 1
            
    def testGetip(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getIP(), self.nicValues[i]["ip"])
            i = i + 1
            
    def testGetgateway(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getGateway(), self.nicValues[i]["gateway"])
            i = i + 1
            
    def testGetnetmask(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getNetmask(), self.nicValues[i]["netmask"])
            i = i + 1
            
    def testGetmaster(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMaster(), self.nicValues[i]["master"])
            i = i + 1
            
    def testGetslave(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getSlave(), self.nicValues[i]["slave"])
            i = i + 1

class testClusterRepository(testClusterTools):      
    """
    Methods from RedhatClusterRepository
    """                    
    def testGetnodename(self):
        # except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodename"], str(self.clusterRepository.getNodeName(_tmp[i]["mac"])))
        self.assertRaises(comoonics.cluster.ComClusterRepository.ClusterMacNotFoundException, self.clusterRepository.getNodeName,"murks")
        
    def testGetnodeid(self):
        # except first nic because it does not have an mac-address
        _tmp = self.nicValues[1:]
        for i in range(len(_tmp)):
            self.assertEqual(_tmp[i]["nodeid"], str(self.clusterRepository.getNodeId(_tmp[i]["mac"])))
        self.assertRaises(comoonics.cluster.ComClusterRepository.ClusterMacNotFoundException, self.clusterRepository.getNodeId,"murks")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testClusterInfo))
    suite.addTest(makeSuite(testClusterNode))
    suite.addTest(makeSuite(testClusterNodeNic))
    suite.addTest(makeSuite(testClusterRepository))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
    #unittest.main()