"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.1 2007-06-05 13:11:21 andrea2 Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterRepository.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from ComClusterMetainfo import *
from ComClusterNode import *

from comoonics.ComLog import *
from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import *

class ClusterMacNotFoundException(ComException):
    """
    Defines Exeption which is raised if a querie
    cannot find an element with given mac-address.
    """
    pass

class ClusterRepository(DataObject):
    """
    Provides generall functionality for a clusterrepository instance
    """

    log = ComLog.getLogger("ComCdslRepository")

    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clustermetainfo which 
        instance of clusterrepository (general, redhat 
        or comoonics) has to be created.
        """
        if isinstance(args[2], ComoonicsClusterMetainfo):
            cls = ComoonicsClusterRepository
        elif isinstance(args[2], RedhatClusterMetainfo):
            cls = RedhatClusterRepository
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self,element,doc=None,clusterMetainfo=None):
        #node dictionaries depend on clustertype, setting later!
        self.nodeNameMap = {}
        self.nodeIdMap = {}
        self.nodeIdentMap = {}
        
        if clusterMetainfo==None:
            clusterMetainfo = ClusterMetainfo()
        else:
            self.metainfo = clusterMetainfo
        
        super(ClusterRepository,self).__init__(element,doc)
        
    def getMetainfo(self):
        """
        @return: returns metainfo object
        @rtype: L{ClusterMetainfo}
        """
        return self.metainfo
    
class RedhatClusterRepository(ClusterRepository):
    """
    Represents the clusterconfiguration file of an redhat 
    cluster as an L{DataObject}. Extends generall 
    clusterrepository by special queries for this cluster 
    type.
    """
    
    cluster_path = "/cluster"
    """@type: string"""
    clusternode_path = cluster_path + "/clusternodes/clusternode"
    """@type: string"""
    
    def __init__(self,element,doc=None,clusterMetainfo=None):
        if clusterMetainfo==None:
            clusterMetainfo = ClusterMetainfo()
            
        super(RedhatClusterRepository,self).__init__(element,doc,clusterMetainfo)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = xpath.Evaluate(self.clusternode_path, self.getElement())
        for i in range(len(_nodes)):
            _node = ClusterNode(_nodes[i], self.getElement())
            _name = _node.getName()
            _id = _node.getId()
            self.nodeNameMap[_name] = _node
            self.nodeIdMap[_id] = _node

    def getNodeName(self,mac):
        """
        @return: Nodename
        @rtype: string
        """
        for node in self.nodeIdMap.values():
            try:
                node.getNic(mac)
                return node.getName()
            except KeyError:
                pass
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)
    
    def getNodeId(self,mac):
        """
        @return: Nodeid
        @rtype: int
        """
        for node in self.nodeIdMap.values():
            #if node does not match given mac, test next node
            try:
                node.getNic(mac)
                return node.getId()
            except KeyError:
                pass
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)

class ComoonicsClusterRepository(RedhatClusterRepository):
    """
    Represents the clusterconfiguration file of an 
    comoonics cluster as an L{DataObject}. Extends 
    the redhat clusterrepository by adding an 
    extra comoonics specific Hashmap.
    """
    def __init__(self,element,doc=None,clusterMetainfo=None):
        if clusterMetainfo==None:
            clusterMetainfo = ClusterMetainfo()
        
        super(ComoonicsClusterRepository,self).__init__(element,doc,clusterMetainfo)
        
        #get nodeidentifier using parameters fro clustermetainfo
        node_prefix = clusterMetainfo.getAttribute("node_prefix")
        use_nodeids = clusterMetainfo.getAttribute("use_nodeids")
        maxnodeidnum = clusterMetainfo.getAttribute("maxnodeidnum")
        
        #fill dictionaries with nodename:nodeobject and nodeid:nodeobject
        _nodes = xpath.Evaluate(self.clusternode_path, self.getElement())
        for i in range(len(_nodes)):
            _node = ClusterNode(_nodes[i], self.getElement())          
            if ((use_nodeids == "True") and (maxnodeidnum == "0")): #maxnodidnum is not set but use_nodeid is set
                _ident = _node.getId()
            elif (maxnodeidnum == "0"): #maxnodidnum is set but use_nodeid is not set
                _ident = _node.getName()
                
            else: #use_nodeids and maxnodeidnum are set
                _ident = i
            
            #value of node_prefix matters if use_nodeids is set
            #if node_prefix in clustermetainfo object is "", then getAttr gets "True" instead
            if ((node_prefix != True) and (use_nodeids == "True")):
                _ident = str(node_prefix) + str(_ident)
            elif (node_prefix != True) and not (use_nodeids == "True"):
                self.log.info("Prefix could only be used together with use_nodeids")
            
            self.nodeIdentMap[_ident] = _node
            
def main():
    # create Reader object
    reader = Sax2.Reader()

    #parse the document and create clusterrepository object
    file = os.fdopen(os.open("test/cluster2.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    file.close()
    element = xpath.Evaluate("/cluster", doc)[0]

    #create clusterMetainfo Object
    clusterMetainfo = ClusterMetainfo("node_","True")

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element,doc,clusterMetainfo)
    
    print "Dictionary Nodeid:Nodeobject"
    print clusterRepository.nodeIdMap
    print "\nDictionary Nodename:Nodeobject"
    print clusterRepository.nodeNameMap
    print "\nDictionary Nodeident:Nodeobject"
    print clusterRepository.nodeIdentMap
    
    print "\nclusterRepository\n" + str(clusterRepository)
    
    for node in clusterRepository.nodeNameMap.values():
        print "Node " + str(node.getName())
        for Nic in node.getNics():
            print "\tNic " + Nic.getName() + ", mac " + Nic.getMac()
            mac = Nic.getMac()
            print "\tgetNodeName(mac): " + clusterRepository.getNodeName(mac)
            print "\tgetNodeId(mac): " + clusterRepository.getNodeId(mac) + "\n"

    print "\tgetMetainfo(): " + str(clusterRepository.getMetainfo())
    
if __name__ == '__main__':
    main()

# $Log: ComClusterRepository.py,v $
# Revision 1.1  2007-06-05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/02 13:30:56  andrea
# inital version
#