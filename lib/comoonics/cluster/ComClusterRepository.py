"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.5 2007-09-04 07:52:25 andrea2 Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterRepository.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from ComClusterNode import *

from comoonics.ComDataObject import DataObject
from comoonics import ComLog
from comoonics.ComExceptions import *

class ClusterMacNotFoundException(ComException): pass

class ClusterRepository(DataObject):
    """
    Provides generall functionality for a clusterrepository instance
    """

    log = ComLog.getLogger("comoonics.cluster.ComClusterRepository")

    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clustermetainfo which 
        instance of clusterrepository (general, redhat 
        or comoonics) has to be created.
        """
        if xpath.Evaluate("/cluster/clusternodes/clusternode/com_info",args[0]):
            cls = ComoonicsClusterRepository
        elif xpath.Evaluate("/cluster/clusternodes/clusternode",args[0]):
            cls = RedhatClusterRepository
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self,element,doc=None):
        #node dictionaries depend on clustertype, setting later!
        self.nodeNameMap = {}
        self.nodeIdMap = {}
        
        super(ClusterRepository,self).__init__(element,doc)
    
class RedhatClusterRepository(ClusterRepository):
    """
    Represents the clusterconfiguration file of an redhat 
    cluster as an L{DataObject}. Extends generall 
    clusterrepository by special queries for this cluster 
    type.
    """
    
    defaultcluster_path = "/cluster"
    """@type: string"""
    defaultclusternode_path = defaultcluster_path + "/clusternodes/clusternode"
    """@type: string"""
    
    def __init__(self,element,doc=None):    
        super(RedhatClusterRepository,self).__init__(element,doc)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = xpath.Evaluate(self.defaultclusternode_path, self.getElement())
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
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.nodeIdMap.values():
            try:
                self.log.debug("get clusternodenic belonging to given mac: " + mac)
                node.getNic(mac)
                self.log.debug("get name belonging to searched clusternodenic: " + node.getName())
                return node.getName()
            except KeyError:
                pass
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)
    
    def getNodeId(self,mac):
        """
        @return: Nodeid
        @rtype: int
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.nodeIdMap.values():
            #if node does not match given mac, test next node
            try:
                self.log.debug("get clusternodenic belonging to given mac: " + mac)
                node.getNic(mac)
                self.log.debug("get id belonging to searched clusternodenic: " + node.getName())
                return node.getId()
            except KeyError:
                pass
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)

class ComoonicsClusterRepository(RedhatClusterRepository):
    """
    Represents the clusterconfiguration file of an 
    comoonics cluster as an L{DataObject}.
    """
    def __init__(self,element,doc=None):
        super(ComoonicsClusterRepository,self).__init__(element,doc)
            
def main():
    """
    Method to test module. Creates a ClusterRepository object, prints defined hashmaps 
    and test getting of nodename and nodeid of nodes defined in a example cluster.conf.
    """
    # create Reader object
    reader = Sax2.Reader()

    #parse the document and create clusterrepository object
    file = os.fdopen(os.open("test/cluster2.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    file.close()
    element = xpath.Evaluate("/cluster", doc)[0]

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element,doc)
    
    print "Dictionary Nodeid:Nodeobject"
    print clusterRepository.nodeIdMap
    print "\nDictionary Nodename:Nodeobject"
    print clusterRepository.nodeNameMap
    
    print "\nclusterRepository\n" + str(clusterRepository)
    print "Repositorytype Comoonics?: " + str(isinstance(clusterRepository, ComoonicsClusterRepository))
    
    for node in clusterRepository.nodeNameMap.values():
        print "Node " + str(node.getName())
        for Nic in node.getNics():
            print "\tNic " + Nic.getName() + ", mac " + Nic.getMac()
            mac = Nic.getMac()
            print "\tgetNodeName(mac): " + clusterRepository.getNodeName(mac)
            print "\tgetNodeId(mac): " + clusterRepository.getNodeId(mac) + "\n"

if __name__ == '__main__':
    main()

# $Log: ComClusterRepository.py,v $
# Revision 1.5  2007-09-04 07:52:25  andrea2
# Removed unused variable
#
# Revision 1.4  2007/08/06 12:09:27  andrea2
# Added more Docu, removed ClusterMetainfo
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/02 13:30:56  andrea
# inital version
#
