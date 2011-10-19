'''
Created on May 20, 2011

@author: marc
'''
import unittest
import logging
from comoonics.installation.osrcluster import OSRCluster, OSRClusterNode, OSRClusterNodeNetdev, OSRClusterNodeFilesystem
logging.basicConfig()
log=logging.getLogger("osrcluster")
log.setLevel(logging.DEBUG)

class Test(unittest.TestCase):


    def setUp(self):
        self.defaults = {"cluster":{"config_version":"1", "name":"clurcent5",
                                "cman":{"expected_votes":"1", "two_node":"0"},
                                "clusternodes":
                                         {"clusternode":[
                                                 {"nodeid":"N", "name":"gfs-nodeN", "votes":"1",
                                                  "com_info":{
                                                      "rootvolume":{"name":"/dev/VG_SHAREDROOT/LV_SHAREDROOT"},
#                                                      "eth":[{"ip":"10.0.0.0", "name":"eth0"}]
                                                  },
                                                  "fence":{"method":{"name":"1"}}}]},
                                "fencedevices":{},
                                "rm":{"failoverdomains":{},"resources":{}}}}
        self.clustername="testcluster"
        self.rootvolume="/dev/vg_testcluster_sr/lv_sharedroot"
        self.numnodes=1
        self.netdev="eth0"
        
    def tearDown(self):
        pass
    
    def testClusterRepositoryEXT3(self):
        from comoonics import XmlTools
        result="""<cluster config_version="1" name="testcluster">
    <clusternodes>
        <clusternode name="name0" nodeid="1" votes="1">
            <com_info>
                <eth master="bond0" name="eth0" slave="yes"/>
                <eth master="bond0" name="eth1" slave="yes"/>
                <eth bondingopts="miimon=100,mode=passive" name="bond0"/>
                <eth gateway="10.0.0.2" ip="10.0.0.1" name="bond0.100" netmask="255.255.255.0"/>
                <rootvolume fstype="ext3" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
    </clusternodes>
    <fencedevices/>
    <cman expected_votes="1" two_node="0"/>
    <rm>
        <resources/>
        <failoverdomains/>
    </rm>
</cluster>
"""
        self.numnodes=1
        osrcluster=OSRCluster(self.clustername, self.numnodes)
        for i in range(self.numnodes):
            _node=OSRClusterNode(osrcluster, "name%u" %i, self.rootvolume)
            _node.rootvol=self.rootvolume
            _node.rootfstype="ext3"
            _netdev=OSRClusterNodeNetdev(_node, "eth0")
            _netdev.master="bond0"
            _netdev.slave="yes"
            _node.addNetdev(_netdev)
            _netdev=OSRClusterNodeNetdev(_node, "eth1")
            _netdev.master="bond0"
            _netdev.slave="yes"
            _node.addNetdev(_netdev)
            _netdev=OSRClusterNodeNetdev(_node, "bond0")
            _netdev.bondingopts="miimon=100,mode=passive"
            _node.addNetdev(_netdev)
            _netdev=OSRClusterNodeNetdev(_node, "bond0.100")
            _netdev.ip="10.0.0.1"
            _netdev.netmask="255.255.255.0"
            _netdev.gateway="10.0.0.2"
            _node.addNetdev(_netdev)
            osrcluster.addNode(_node)
        log.debug("Cluster: %s" %osrcluster)
        log.debug("Cluster as hash: %s" %osrcluster.toHash())
        from comoonics.cluster import getClusterRepository
        hash=osrcluster.toHash()
        tmp=getClusterRepository(None,None,hash,self.defaults)
        print XmlTools.toPrettyXML(tmp.getElement())
        tmp=XmlTools.toPrettyXML(tmp.getElement())
        self.assertEquals(result.replace(" ", "").replace("\n", ""), tmp.replace("\t", "").replace(" ", "").replace("\n", ""))

    def testClusterRepositoryGFS(self):
        from comoonics import XmlTools
        self.numnodes=5
        result="""<cluster config_version="1" name="testcluster">
    <clusternodes>
        <clusternode name="name0" nodeid="1" votes="1">
            <com_info>
                <eth ip="dhcp" mac="00:00:00:xx:00" name="eth0"/>
                <rootvolume fstype="gfs" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
                <filesystems>
                    <filesystem dest="/var/run" fstype="bind" mountopts="defaults" source="/.cluster/cdsl/%(param0)s/var/run"/>
                </filesystems>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
        <clusternode name="name1" nodeid="2" votes="1">
            <com_info>
                <eth ip="dhcp" mac="00:00:00:xx:01" name="eth0"/>
                <rootvolume fstype="gfs" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
                <filesystems>
                    <filesystem dest="/var/run" fstype="bind" mountopts="defaults" source="/.cluster/cdsl/%(param0)s/var/run"/>
                </filesystems>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
        <clusternode name="name2" nodeid="3" votes="1">
            <com_info>
                <eth ip="dhcp" mac="00:00:00:xx:02" name="eth0"/>
                <rootvolume fstype="gfs" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
                <filesystems>
                    <filesystem dest="/var/run" fstype="bind" mountopts="defaults" source="/.cluster/cdsl/%(param0)s/var/run"/>
                </filesystems>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
        <clusternode name="name3" nodeid="4" votes="1">
            <com_info>
                <eth ip="dhcp" mac="00:00:00:xx:03" name="eth0"/>
                <rootvolume fstype="gfs" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
                <filesystems>
                    <filesystem dest="/var/run" fstype="bind" mountopts="defaults" source="/.cluster/cdsl/%(param0)s/var/run"/>
                </filesystems>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
        <clusternode name="name4" nodeid="5" votes="1">
            <com_info>
                <eth ip="dhcp" mac="00:00:00:xx:04" name="eth0"/>
                <rootvolume fstype="gfs" name="/dev/vg_testcluster_sr/lv_sharedroot"/>
                <filesystems>
                    <filesystem dest="/var/run" fstype="bind" mountopts="defaults" source="/.cluster/cdsl/%(param0)s/var/run"/>
                </filesystems>
            </com_info>
            <fence>
                <method name="1"/>
            </fence>
        </clusternode>
    </clusternodes>
    <fencedevices/>
    <cman expected_votes="1" two_node="0"/>
    <rm>
        <resources/>
        <failoverdomains/>
    </rm>
</cluster>
"""
        log.debug("Setting up cluster %s" %self.clustername)
        osrcluster=OSRCluster(self.clustername, self.numnodes)
        for i in range(self.numnodes):
            _node=OSRClusterNode(osrcluster, "name%u" %i, self.rootvolume)
            _node.rootvol=self.rootvolume
            _node.rootfstype="gfs"
            _node.addNetdev(OSRClusterNodeNetdev(_node, self.netdev))
            _node.getNetdev(self.netdev).mac="00:00:00:xx:0%u" %i
            _node.getNetdev(self.netdev).ip="dhcp"
            _node.addFilesystem(OSRClusterNodeFilesystem(_node, "bind", "/.cluster/cdsl/%(param0)s/var/run", "/var/run"))
            osrcluster.addNode(_node)
        log.debug("Cluster: %s" %osrcluster)
        log.debug("Cluster as hash: %s" %osrcluster.toHash())
        from comoonics.cluster import getClusterRepository
        tmp=getClusterRepository(None,None,osrcluster.toHash(),self.defaults)
        print XmlTools.toPrettyXML(tmp.getElement())
        tmp=XmlTools.toPrettyXML(tmp.getElement())
        self.assertEquals(result.replace(" ", "").replace("\n", ""), tmp.replace("\t", "").replace(" ", "").replace("\n", ""))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()