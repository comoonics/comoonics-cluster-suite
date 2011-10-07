import os.path

import sys
sys.path.append("./lib")

import unittest

class baseClusterTestClass(unittest.TestCase):
    """
    Unittests for Clustertools
    """
    def __init__(self, testMethod="runTest"):
        super(baseClusterTestClass, self).__init__(testMethod)
        self.init()
      
    def _testNicGetName(self, name, methodname=None):
        if not methodname:
            methodname="get"+name.capitalize()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
            for nic in node.getNics():
                self.assertEqual(getattr(nic, methodname)(), 
                                 self.nodeValues[node.getId()][nic.getName()][name],
                                 "Nic attribute %s of node %s and nic %s, %s != %s" %(name, node.getId(), nic.getName(), getattr(nic, methodname)(), self.nodeValues[node.getId()][nic.getName()][name]))
    
    def init(self):
        """
        set up data used in the tests.
        setUp is called before each test function execution.
        """        
        testpath=os.path.dirname(sys.argv[0])
        for _module in sys.modules.keys():
            if _module.endswith("BaseClusterTestClass"):
                testpath=os.path.dirname(sys.modules[_module].__file__)

        self._testpath=testpath

        #create comclusternodenic objects
        
        #        The following specifications must match these of the used clusterconfiguration
        
        # Preparation of failoverdomains
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
                
        # Preparation of nodes
        self.nodeValues = {}
        
        self.nodeValues["1"]={}
        self.nodeValues["1"]["name"] = "gfs-node1"
        self.nodeValues["1"]["id"] = "1"
        self.nodeValues["1"]["votes"] = "1"
        self.nodeValues["1"]["rootvolume"] = ""
        self.nodeValues["1"]["rootfs"] = "gfs"
        self.nodeValues["1"]["mountopts"] = ""
        self.nodeValues["1"]["syslog"] = ""
        self.nodeValues["1"]["scsifailover"] = "driver"

        self.nodeValues["1"]["eth1"]={}
        self.nodeValues["1"]["eth1"]["name"] = "eth1"
        self.nodeValues["1"]["eth1"]["nodename"] = "gfs-node1"
        self.nodeValues["1"]["eth1"]["nodeid"] = "1"
        self.nodeValues["1"]["eth1"]["mac"] = ""
        self.nodeValues["1"]["eth1"]["ip"] = "dhcp"
        self.nodeValues["1"]["eth1"]["gateway"] = ""
        self.nodeValues["1"]["eth1"]["netmask"] = ""
        self.nodeValues["1"]["eth1"]["master"] = ""
        self.nodeValues["1"]["eth1"]["slave"] = ""
        
        self.nodeValues["2"]={}
        self.nodeValues["2"]["name"] = "gfs-node2"
        self.nodeValues["2"]["id"] = "2"
        self.nodeValues["2"]["votes"] = "3"
        self.nodeValues["2"]["rootvolume"] = "/dev/VG_SHAREDROOT/LV_SHAREDROOT"
        self.nodeValues["2"]["rootfs"] = "meinfs"
        self.nodeValues["2"]["mountopts"] = "someopts"
        self.nodeValues["2"]["syslog"] = "gfs-node1"
        self.nodeValues["2"]["scsifailover"] = "gfs-node1"

        self.nodeValues["2"]["eth0"]={}
        self.nodeValues["2"]["eth0"]["name"] = "eth0"
        self.nodeValues["2"]["eth0"]["nodename"] = "gfs-node2"
        self.nodeValues["2"]["eth0"]["nodeid"] = "2"
        self.nodeValues["2"]["eth0"]["mac"] = "00:0C:29:3C:XX:XX"
        self.nodeValues["2"]["eth0"]["ip"] = "10.0.0.2"
        self.nodeValues["2"]["eth0"]["gateway"] = ""
        self.nodeValues["2"]["eth0"]["netmask"] = "255.255.255.0"
        self.nodeValues["2"]["eth0"]["master"] = "bond0"
        self.nodeValues["2"]["eth0"]["slave"] = "yes"
        
        self.nodeValues["2"]["eth1"]={}
        self.nodeValues["2"]["eth1"]["name"] = "eth1"
        self.nodeValues["2"]["eth1"]["nodename"] = "gfs-node2"
        self.nodeValues["2"]["eth1"]["nodeid"] = "2"
        self.nodeValues["2"]["eth1"]["mac"] = "00:0C:29:3C:XX:XY"
        self.nodeValues["2"]["eth1"]["ip"] = "10.0.0.3"
        self.nodeValues["2"]["eth1"]["gateway"] = "1.2.3.4"
        self.nodeValues["2"]["eth1"]["netmask"] = "255.255.255.0"
        self.nodeValues["2"]["eth1"]["master"] = ""
        self.nodeValues["2"]["eth1"]["slave"] = ""
        
        self.nodeValues["3"]={}
        self.nodeValues["3"]["name"] = "gfs-node3"
        self.nodeValues["3"]["id"] = "3"
        self.nodeValues["3"]["votes"] = "1"
        self.nodeValues["3"]["rootvolume"] = "/dev/VG_SHAREDROOT/LV_SHAREDROOT"
        self.nodeValues["3"]["rootfs"] = "ocfs2"
        self.nodeValues["3"]["mountopts"] = "noatime"
        self.nodeValues["3"]["syslog"] = ""
        self.nodeValues["3"]["scsifailover"] = "driver"
        self.nodeValues["3"]["bond0"]={}
        self.nodeValues["3"]["bond0"]["name"] = "bond0"
        self.nodeValues["3"]["bond0"]["nodename"] = "gfs-node3"
        self.nodeValues["3"]["bond0"]["nodeid"] = ""
        self.nodeValues["3"]["bond0"]["mac"] = "00:17:A4:10:7B:7D"
        self.nodeValues["3"]["bond0"]["ip"] = "192.168.10.22"
        self.nodeValues["3"]["bond0"]["gateway"] = "192.168.10.1"
        self.nodeValues["3"]["bond0"]["netmask"] = "255.255.255.0"
        self.nodeValues["3"]["bond0"]["master"] = ""
        self.nodeValues["3"]["bond0"]["slave"] = ""
        
        self.nodeValues["3"]["eth0"]={}
        self.nodeValues["3"]["eth0"]["name"] = "eth0"
        self.nodeValues["3"]["eth0"]["nodename"] = "gfs-node3"
        self.nodeValues["3"]["eth0"]["nodeid"] = "3"
        self.nodeValues["3"]["eth0"]["mac"] = "00:17:A4:10:7B:7E"
        self.nodeValues["3"]["eth0"]["ip"] = ""
        self.nodeValues["3"]["eth0"]["gateway"] = ""
        self.nodeValues["3"]["eth0"]["netmask"] = ""
        self.nodeValues["3"]["eth0"]["master"] = "bond0"
        self.nodeValues["3"]["eth0"]["slave"] = "yes"
        
        self.nodeValues["3"]["bond0.45"]={}
        self.nodeValues["3"]["bond0.45"]["name"] = "bond0.45"
        self.nodeValues["3"]["bond0.45"]["nodename"] = "gfs-node3"
        self.nodeValues["3"]["bond0.45"]["nodeid"] = ""
        self.nodeValues["3"]["bond0.45"]["mac"] = "00:17:A4:10:7B:7C"
        self.nodeValues["3"]["bond0.45"]["ip"] = "192.168.254.233"
        self.nodeValues["3"]["bond0.45"]["gateway"] = ""
        self.nodeValues["3"]["bond0.45"]["netmask"] = "255.255.255.255"
        self.nodeValues["3"]["bond0.45"]["master"] = ""
        self.nodeValues["3"]["bond0.45"]["slave"] = ""
