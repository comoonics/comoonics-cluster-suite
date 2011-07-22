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
        keys=self.__dict__.keys()
        keys.sort()
        for _attr in keys:
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
                    
                    if getattr(self, _attr):           
                        _node[_attrname]=getattr(self, _attr)
                elif getattr(self, _attr):
                    _hash[_attrname]=getattr(self, _attr)
        return _hash
    
class OSRCluster(KSObject):
    def __init__ (self, _clustername="unknown", _journals=5):
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
        self.MAP_ATTRS["clustername"]="name"
        self.clustername = _clustername
        self.journals=_journals
        self.lockproto="lock_dlm"
        self.nodes=dict()
        self.nodeslist=list()
        #or _node in _nodes:
        #   self.nodes.append(SharedrootNode(_node))

    def __str__(self):
        """
        Will look as follows:
            osrcluster [--journals=journals] clustername
        """
        tmp = "osrcluster "
        #tmp = tmp + "--journalnumber=%s " % str(self.nodenumber)
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
    
    def extendKSOptionParser(op):
        """
        Default is do nothing.s
        """
        op.add_option("--journals", dest="journals", type="int", action="store", default=1)
        return op
    extendKSOptionParser=staticmethod(extendKSOptionParser)

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
        return len(self.nodeslist)+1
    
class OSRClusterNode(KSObject):
    def __init__(self, _osrcluster, _nodename="unknownnodename", _rootvol=None, _rootfstype=None, _nodeid=None):
        KSObject.__init__(self)
        self.IGNORE_ATTRS.append("cluster")
        self.IGNORE_ATTRS.append("netdevs")
        self.IGNORE_ATTRS.append("netdevslist")
        self.IGNORE_ATTRS.append("filesystemlist")
        self.MAP_ATTRS["scsifailover"]="failover"
        self.MAP_ATTRS["nodename"]="name"
        self.MAP_ATTRS["rootvol"]="name"
        self.MAP_ATTRS["rootfstype"]="fstype"
        self.PARENTS_FOR_ATTRS["rootvol"]=["com_info", "rootvolume" ]
        self.PARENTS_FOR_ATTRS["rootfstype"]=["com_info", "rootvolume" ]
        self.PARENTS_FOR_ATTRS["scsifailover"]=["com_info", "scsi" ]
        self.cluster=_osrcluster
        self.nodename=_nodename
        self.rootvol=_rootvol
        self.rootfstype=_rootfstype
        if _nodeid==None:
            self.nodeid=str(self.cluster.getNextNodeId())
        else:
            self.nodeid=_nodeid
        self.netdevs=dict()
        self.netdevslist=list()
        self.filesystemlist=list()
    
    def toHash(self):
        _hash=super(OSRClusterNode, self).toHash()
        _netdevs=list()
        for _netdev in self.netdevslist:
            _netdevs.append(_netdev.toHash())
        if not _hash.has_key("com_info"):
            _hash["com_info"]=dict()
            
        _hash["com_info"]["eth"]=_netdevs
        if len(self.filesystemlist)>0:
            _hash["com_info"]["filesystems"]=dict()
        for filesystem in self.filesystemlist:
            _hash["com_info"]["filesystems"]["filesystem"]=filesystem.toHash()
        return _hash
    
    def extendKSOptionParser(op):
        """
        Default is do nothing.s
        """
        op.add_option("--rootvol", dest="rootvol", default=None)
        op.add_option("--rootfstype", dest="rootfstype", default=None)
        op.add_option("--scsifailover", dest="scsifailover", default=None)
        return op
    extendKSOptionParser=staticmethod(extendKSOptionParser)
    
    def addFilesystem(self, filesystem):
        self.filesystemlist.append(filesystem)
    
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
        if self.rootfstype != None:
            tmp=tmp+"--rootfstype=%s " %self.rootfstype
        if hasattr(self, "scsifailover") and self.scsifailover != None:
            tmp=tmp+"--scsifailover=%s" %self.scsifailover
        tmp=tmp+" "+self.nodename
        for _netdev in self.netdevslist:
            tmp+="\n%s" %_netdev
        for filesystem in self.filesystemlist:
            tmp+="\n%s" %filesystem
        return tmp

class OSRClusterNodeNetdev(KSObject):
    valid_attrs=[ "master", "slave", "bondingopts", "ip", "netmask", "gateway" ]
    def __init__(self, _node, _netdev="eth0", **kwds):
        KSObject.__init__(self)
        self.MAP_ATTRS["devname"]="name"
        self.IGNORE_ATTRS.append("node")
        self.IGNORE_ATTRS.append("valid_attrs")
        self.devname=_netdev
        self.node=_node
        if kwds:
            for attr in OSRClusterNodeNetdev.valid_attrs:
                if kwds.has_attr(attr):
                    setattr(self, attr, kwds[attr])
                    
    def __str__(self):
        """
        Will look as follows:
           osrclusternodenetdev nodename devname
        """
        output="osrclusternodenetdev "
        for attr in OSRClusterNodeNetdev.valid_attrs:
            if hasattr(self, attr):
                output+=" --%s=%s" %(attr, getattr(self, attr)) 
        return output+" %s %s" %(self.node.nodename, self.devname)
    
    def extendKSOptionParser(op):
        """
        Default is do nothing.s
        """
        for attr in OSRClusterNodeNetdev.valid_attrs:
            op.add_option("--%s" %attr, dest=attr, default=None)
        return op
    extendKSOptionParser=staticmethod(extendKSOptionParser)

class OSRClusterNodeFilesystem(KSObject):
    def __init__(self, node, fstype, source, dest, mountopts="defaults"):
        KSObject.__init__(self)
        self.IGNORE_ATTRS.append("node")
        self.source=source
        self.dest=dest
        self.fstype=fstype
        self.mountopts=mountopts
        self.node=node
        
    def __str__(self):
        """
        Will look as follows in the kickstartfile:
        osrclusternodefilesystem nodename fstype source dest [mountopts]
        """
        return "osrclusternodefilesystem %s %s %s %s %s" %(self.node.nodename, self.fstype, self.source, self.dest, self.mountopts)
    
    def extendKSOptionParser(op):
        """
        Default is do nothing.s
        """
        return op
    extendKSOptionParser=staticmethod(extendKSOptionParser)

####################################
# $Log: osrcluster.py,v $
# Revision 1.3  2008-06-04 10:28:56  marc
# -bugfixes
#
# Revision 1.2  2008/05/20 16:05:03  marc
# nodeid must be str not int
#
# Revision 1.1  2008/05/20 15:55:36  marc
# first official release
#