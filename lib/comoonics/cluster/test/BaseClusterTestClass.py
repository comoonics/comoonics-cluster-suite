from comoonics import ComLog
from comoonics.cluster.ComClusterInfo import ClusterInfo
from comoonics.cluster.ComClusterNode import ComoonicsClusterNode
from comoonics.cluster.ComClusterNodeNic import ComoonicsClusterNodeNic
from comoonics.cluster.ComClusterRepository import ClusterRepository

from xml.dom.ext.reader import Sax2

import os
import os.path
from xml import xpath

import sys
sys.path.append("./lib")

import unittest

class baseClusterTestClass(unittest.TestCase):
    """
    Unittests for Clustertools
    """
    def setUp(self):
        """
        set up data used in the tests.
        setUp is called before each test function execution.
        """        
        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository("cluster2.conf")

        #create comclusterinfo object
        self.clusterInfo = ClusterInfo(self.clusterRepository)
        
        #create comclusternodenic objects
        
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
        
        # setup the cashes for clustat for redhat cluster
        import logging
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        ComLog.setLevel(logging.DEBUG)
        self.clusterInfo.helper.__setSimOutput()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
        
    def createNodeList(self, key):
        _list = []
        for i in range(len(self.nodeValues)):
            _list.append(self.nodeValues[i][key])
        return _list
