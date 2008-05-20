#
# osr.py: customize installation to get a diskless shared root cluster
#
# Andrea Offermann <offermann@atix.de>
#
# Copyright 2008 ATIX Informationstechnologie und Consulting AG
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import logging
log=logging.getLogger("osrcluster")
import re
class KSObject(object):
    IGNORE_ATTRS=[ re.compile("_.*")]
    MAP_ATTRS=dict()
    PARENTS_FOR_ATTRS=dict()
    
    def __init__(self):
        pass
    def writeKS(self, f):
        log.debug(self.__str__())
        f.write(self.__str__()+"\n")
    def __str__(self):
        """
        This method has to be overwritten by children
        """
        return "KSObject"
    def toHash(self):
        _hash=dict()
        for _attr in self.__dict__.keys():
            _ignore=False
            for _ignore_attr in self.IGNORE_ATTRS:
                if isinstance(_ignore_attr, basestring):
                    if _attr == _ignore_attr:
                        _ignore=True
                elif _ignore_attr.match(_attr):
                    _ignore=True
            if not _ignore:
                _attrname=_attr
                if self.MAP_ATTRS.has_key(_attr):
                    _attrname=self.MAP_ATTRS[_attr]
                if self.PARENTS_FOR_ATTRS.has_key(_attr):
                    _parents=self.PARENTS_FOR_ATTRS[_attr]
                    if isinstance(_parents, basestring):
                        _parents=[_parents]
                    _node=_hash
                    for _parent in _parents:
                        if not _node.has_key(_parent):
                            _node[_parent]=dict()
                        _node=_node[_parent]
                                
                    _node[_attrname]=getattr(self, _attr)
                else:
                    _hash[_attrname]=getattr(self, _attr)
        return _hash

#        _hash = {"cluster":{"name":anaconda.id.osrcluster.clustername,
#                                    "clusternodes":
#                                     {"clusternode":[
#                                       {"nodeid":"1", "name":str(nodename),
#                                          "com_info":{
#                                            "rootvolume":{"name":str(self._dsrc_root)},
#                                            "eth":[{"ip":str(ipAddress),
#                                                    "name":str(self._netdevice),
#                                                    "mac":anaconda.id.network.available()[self._netdevice].get('hwaddr')}]}}]}}}
class OSRCluster(KSObject):
    def __init__ (self, _clustername="unknown", _usehostname=False, _journals=5):
        KSObject.__init__(self)
        #self.netdev = []
        #self.nodename = []
        #self.nodenumber = ""
        #self.rootvol = ""
        self.IGNORE_ATTRS.append("nodes")
        self.IGNORE_ATTRS.append("nodeslist")
# FIXME: has to be changed to votes or some better thing        
        self.IGNORE_ATTRS.append("journals")
        self.IGNORE_ATTRS.append("lockproto")
        self.IGNORE_ATTRS.append("useHostname")
        self.MAP_ATTRS["clustername"]="name"
        self.clustername = _clustername
        self.useHostname = _usehostname
        self.journals=_journals
        self.lockproto="lock_dlm"
        self.nodes=dict()
        self.nodeslist=list()
        #or _node in _nodes:
        #   self.nodes.append(SharedrootNode(_node))

    def __str__(self):
        """
        Will look as follows:
            osrcluster [--usehostname] [--journals=journals] clustername
        """
        tmp = "osrcluster "
        #tmp = tmp + "--journalnumber=%s " % str(self.nodenumber)
        if self.useHostname:
            tmp = tmp + "--usehostname "
        tmp = tmp+"--journals=%s " %self.journals
        #tmp = tmp + "--firstnodename='%s' " % self.nodename[0]
        #tmp = tmp + "--firstnodenetdevice='%s'\n" % self.netdev
        tmp=tmp + " " + self.clustername
        for _node in self.nodeslist:
            tmp+="\n%s" %_node 
        return tmp
    
    def toHash(self):
        _hash={"cluster": super(OSRCluster, self).toHash()}
        _nodes=list()
        for _node in self.nodeslist:
            _nodes.append(_node.toHash())
        _hash["cluster"]["clusternodes"]=dict()
        _hash["cluster"]["clusternodes"]["clusternode"]=_nodes       
        return _hash
    
    def addNode(self, _clusternode):
        """
        Adds a clusternode<<OSRClusterNode>> to the cluster
        """
        self.nodes[_clusternode.nodename]=_clusternode
        self.nodeslist.append(_clusternode)
        
    def addNetdev(self, _clusternodenetdev):
        """
        Adds a clusternodenetdev<<OSRClusterNodeNetdev>> to the cluster and the referenced node
        """
        self.nodes[_clusternodenetdev.nodename].addNetDev(_clusternodenetdev)
    def getNode(self, nameornumber):
        if isinstance(nameornumber, basestring):
            return self.nodes[nameornumber]
        else:
            return self.nodeslist[nameornumber]
    
    def hasNode(self, nameornumber):
        if isinstance(nameornumber, basestring):
            return self.nodes.has_key(nameornumber)
        else:
            return len(self.nodeslist)<nameornumber
        
    def getNextNodeId(self):
        return len(self.nodeslist)
    
class OSRClusterNode(KSObject):
    def __init__(self, _osrcluster, _nodename="unknownnodename", _rootvol=None, _nodeid=None):
        KSObject.__init__(self)
        self.IGNORE_ATTRS.append("cluster")
        self.IGNORE_ATTRS.append("netdevs")
        self.IGNORE_ATTRS.append("netdevslist")
        self.MAP_ATTRS["nodename"]="name"
        self.MAP_ATTRS["rootvol"]="rootvolume"
        self.PARENTS_FOR_ATTRS["rootvol"]=["com_info", "name" ]
        self.cluster=_osrcluster
        self.nodename=_nodename
        self.rootvol=_rootvol
        if _nodeid==None:
            self.nodeid=self.cluster.getNextNodeId()
        else:
            self.nodeid=_nodeid
        self.netdevs=dict()
        self.netdevslist=list()
    
    def toHash(self):
        _hash=super(OSRClusterNode, self).toHash()
        _netdevs=list()
        for _netdev in self.netdevslist:
            _netdevs.append(_netdev.toHash())
        if not _hash.has_key("com_info"):
            _hash["com_info"]=dict()
            
        _hash["com_info"]["eth"]=_netdevs
        return _hash
    
    def addNetdev(self, _clusternodenetdev):
        self.netdevs[_clusternodenetdev.devname]=_clusternodenetdev
        self.netdevslist.append(_clusternodenetdev)        
    
    def hasNetdev(self, nameornumber):
        if isinstance(nameornumber, basestring):
            return self.netdevs.has_key(nameornumber)
        else:
            return len(self.netdevslist)<nameornumber
    
    def getNetdev(self, nameornumber):
        if isinstance(nameornumber, basestring):
            return self.netdevs[nameornumber]
        else:
            return self.netdevslist[nameornumber]

    def __str__(self):
        """
        Will look as follows:
            osrclusternode --rootvol=ROOTVOL nodename
        """
        tmp="osrclusternode "
        if self.rootvol != None:
            tmp=tmp+"--rootvol=%s " %self.rootvol
        tmp=tmp+" "+self.nodename
        for _netdev in self.netdevslist:
            tmp+="\n%s" %_netdev
        return tmp

class OSRClusterNodeNetdev(KSObject):
    def __init__(self, _node, _netdev="eth0"):
        KSObject.__init__(self)
        self.MAP_ATTRS["devname"]="name"
        self.IGNORE_ATTRS.append("node")
        self.devname=_netdev
        self.node=_node
        
    def __str__(self):
        """
        Will look as follows:
           osrclusternodenetdev nodename devname
        """
        return "osrclusternodenetdev %s %s" %(self.node.nodename, self.devname)

def test(clustername="testcluster", numnodes=5, usehostnames=False, rootvolume="/dev/vg_testcluster_sr/lv_sharedroot", netdev="eth0"):
    logging.basicConfig()
    from xml.dom.ext import PrettyPrint
    defaults = {"cluster":{"config_version":"1", "name":"clurcent5",
                                "cman":{"expected_votes":"1", "two_node":"0"},
                                "clusternodes":
                                         {"clusternode":[
                                                 {"nodeid":"N", "name":"gfs-nodeN", "votes":"1",
                                                  "com_info":{
                                                      "rootvolume":{"name":"/dev/VG_SHAREDROOT/LV_SHAREDROOT"},
                                                      "eth":[{"ip":"10.0.0.0", "name":"eth0"}],
                                                      "fenceackserver":{"passwd":"XXX", "user":"root"}},
                                                  "fence":{"method":{"name":"1"}}}]},
                                "fencedevices":{},
                                "rm":{"failoverdomains":{},"resources":{}}}}
    log.setLevel(logging.DEBUG)
    log.debug("Setting up cluster %s" %clustername)
    osrcluster=OSRCluster(clustername, usehostnames, numnodes)
    for i in range(1, 6):
        _node=OSRClusterNode(osrcluster, "name%u" %i, rootvolume, str(i))
        _node.addNetdev(OSRClusterNodeNetdev(_node, netdev))
        _node.getNetdev(netdev).mac="00:00:00:xx:0%u" %i
        _node.getNetdev(netdev).ip="dhcp"
        osrcluster.addNode(_node)
    log.debug("Cluster: %s" %osrcluster)
    log.debug("Cluster as hash: %s" %osrcluster.toHash())
    from comoonics.cluster.ComClusterRepository import ClusterRepository
    _tmp=ClusterRepository(None,None,osrcluster.toHash(),defaults)
    
    log.debug("To cluster.conf: ")
    PrettyPrint(_tmp.getDocument())

if __name__ == "__main__":
    test()
####################################
# $Log: osrcluster.py,v $
# Revision 1.1  2008-05-20 15:55:36  marc
# first official release
#