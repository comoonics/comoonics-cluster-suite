"""Comoonics clusterinfo object module


This module provides functionality to query instances
of clusterrepositories

"""


# here is some internal information
# $Id: ComClusterInfo.py,v 1.3 2007-06-08 08:24:47 andrea2 Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterInfo.py,v $

from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint

from ComClusterNode import *
from ComClusterRepository import *

from comoonics import ComLog
from comoonics.ComExceptions import *

class ClusterMacNotFoundException(ComException):pass

class ClusterInfo(object):
    """
    Provides a set of queries to use with a L{ClusterRepository} 
    to get information about the used clusterconfiguration.
    """
    
    log = ComLog.getLogger("comoonics.cluster.ComClusterInfo")
    
    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clusterrepository 
        which instance of clusterinfo (general, redhat 
        or comoonics) has to be created.
        """
        if isinstance(args[0], ComoonicsClusterRepository):
            cls = ComoonicsClusterInfo
        elif isinstance(args[0], RedhatClusterRepository):
            cls = RedhatClusterInfo
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, clusterRepository):
        #Clusterrepository holds list of nodes and items like node_prefix etc.
        self.clusterRepository = clusterRepository
    
    def getNodes(self):
        """
        @return: list of all node instances
        @rtype: list
        """
        self.log.debug("get clusternodes from clusterrepository")
        return self.clusterRepository.nodeNameMap.values()
    
    def getNodeIdentifiers(self,type="name"):
        """
        @param type: specifies type of returned identifier (could be name or id)
        @type type: string
        @return: list of all node identifiers (e.g. nodenames or nodeids)
        @rtype: list
        """
        identifiers = []
        if type == "id":
            self.log.debug("get nodeids from clusterrepositories")
            return self.clusterRepository.nodeIdMap.keys()
        elif type == "name":
            self.log.debug("get nodenames from clusterrepository")
            return self.clusterRepository.nodeNameMap.keys()
        return identifiers
    
class RedhatClusterInfo(ClusterInfo):
    """
    Extends L{ClusterInfo} to provides a set of special queries 
    to use with a L{RedhatClusterRepository} to get information 
    about the used redhat clusterconfiguration.
    """

    cluster_path = "/cluster"
    failoverdomain_path = "/cluster/rm/failoverdomains/failoverdomain"
    failoverdomainnode_attribute = "/failoverdomainnode"
    
    def __init__(self, clusterRepository):
        super(RedhatClusterInfo,self).__init__(clusterRepository)

    def queryValue(self,query):
        """
        Provides the possibility to get specific values by 
        execute queries which are not yet implemented as a 
        direct function.
        
        @param query: xpath to query clusterinfo instance
        @type query: string
        @return: answer of proceeded query as list of strings
        @rtype: list
        """
        self.log.debug("queryValue: " + query)
        _tmp1 = xpath.Evaluate(query,self.clusterRepository.getElement())
        _tmp2 = []
        for i in range(len(_tmp1)):
            _tmp2.append(_tmp1[i].value)
        return _tmp2
    
    def queryXml(self,query):
        """
        Provides the possibility to execute queries 
        which are not yet implemented as a direct function 
        to get a part of the xml.
        
        @param query: xpath to query clusterinfo instance
        @type query: string
        @return: answer of proceeded query as xml
        @rtype: string
        """
        import StringIO
        self.log.debug("queryXml: " + query)
        _tmp1 = xpath.Evaluate(query,self.clusterRepository.getElement())
        _tmp2 = StringIO.StringIO()
        PrettyPrint(_tmp1[0],stream=_tmp2)
        return _tmp2.getvalue()
        
    def getNode(self,name):
        """
        @param name: name of clusternode
        @type name: string
        @return: Clusternodeinstance belonging to given clusternodename
        @rtype: L{ClusterNode}
        """
        self.log.debug("get node with given name from clusterrepository: " + name)
        return self.clusterRepository.nodeNameMap[name]
            
    def getNodeName(self,mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Clusternodename belonging to given mac-address
        @rtype: string
        """
        self.log.debug("get name of node with given mac from clusterrepository: " + mac)
        return self.clusterRepository.getNodeName(mac)
            
    def getNodeId(self,mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Clusternodeid belonging to given mac-address
        @rtype: string
        """
        self.log.debug("get id of node with given mac from clusterrepository: " + mac)
        return self.clusterRepository.getNodeId(mac)
    
    def getFailoverdomainNodes(self,failoverdomain):
        """
        @param failoverdomain: failoverdomain
        @type failoverdomain: string
        @return: Names of nodes which belong to the given failoverdomain
        @rtype: string
        """
        #no defaultvalue specified because every dailoverdomain needs to have one or more failoverdomainnodes
        try:
            self.log.debug("get failoverdomainnodes from failoverdomain " + failoverdomain + ": " + self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "/@name")
            _tmp1 = self.queryValue(self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "/@name")
        except NameError:
            return ""
        return _tmp1
    
    def getFailoverdomainPrefNode(self,failoverdomain):
        """
        @param failoverdomain: failoverdomain
        @type failoverdomain: string
        @return: Name of node which is prefered in failovercase of given failoverdomain
        @rtype: string
        """
        #no defaultvalue specified because every dailoverdomain needs to have one or more failoverdomainnodes and priority is a needed attribute
        _tmp1 = self.getFailoverdomainNodes(failoverdomain)
        
        #search for lowest priority
        minprio = "0"
        for i in range(len(_tmp1)):
            self.log.debug("query lowest priority of failoverdomainnodes belonging to " + failoverdomain + ": " + self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "[@name='" + _tmp1[i] + "']/@priority")
            _tmp2 = self.queryValue(self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "[@name='" + _tmp1[i] + "']/@priority")[0]
            if (minprio == "0") or (_tmp2 < minprio):
                minprio = _tmp2
        #get node with lowest priority
        try:
            self.log.debug("get failoverprefdomainnode from failoverdomain " + failoverdomain + ": " + self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "[@priority='" + str(minprio) + "']/@name")
            return self.queryValue(self.failoverdomain_path + "[@name='" + failoverdomain + "']" + self.failoverdomainnode_attribute + "[@priority='" + str(minprio) + "']/@name")[0]
        except NameError:
            return ""
    
    def getNodeIds(self):
        """
        @return: List of clusternodeids
        @rtype: list
        """
        self.log.debug("get list of nodeids from clusterrepository")
        return self.clusterRepository.nodeIdMap.keys()

class ComoonicsClusterInfo(RedhatClusterInfo):
    """
    Extends L{RedhatClusterInfo} to provides a set of special queries 
    to use with a L{ComoonicsClusterRepository} to get information 
    about the used comoonics clusterconfiguration.
    """
    def __init__(self, clusterRepository):
        super(ComoonicsClusterInfo,self).__init__(clusterRepository)
    
    def getNic(self,mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Instance of Network interface with given mac-address
        @rtype: L{ComoonicsClusterNodeNic}
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.getNodes():
            try:
                self.log.debug("get clusternodenic with given mac: " + mac)
                return node.getNic(mac).getName()
            except KeyError:
                pass
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)
    
def main():    
    # create Reader object
    reader = Sax2.Reader()

    #parse the document and create clusterrepository object
    file = os.fdopen(os.open("test/cluster2.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    file.close()
    element = xpath.Evaluate('/cluster', doc)[0]

    #create clusterMetainfo Object
    clusterMetainfo = ClusterMetainfo("node_","True")

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element,doc,clusterMetainfo)

    #create comclusterinfo object
    clusterInfo = ClusterInfo(clusterRepository)
    
    #test functions
    print "clusterInfo.getNodeIdentifiers('name'): " + str(clusterInfo.getNodeIdentifiers("name"))
    print "clusterInfo.getNodeIds(): " + str(clusterInfo.getNodeIds())
    _nodes = clusterInfo.getNodes()
    print "clusterInfo.getNodes(): " + str(_nodes)
    print "clusterInfo.queryValue(): " + str(clusterInfo.queryValue("/cluster/clusternodes/clusternode/@name"))
    print "clusterInfo.queryXml(): " + str(clusterInfo.queryXml("/cluster/clusternodes/clusternode/@name"))
    
    for node in _nodes:
        print "\nName: " + node.getName() + " - ID: " + node.getId()
        _name = node.getName()
        _nics = node.getNics()
        for _nic in _nics:
            _mac = _nic.getMac()
            print "clusterInfo.getNic(" + _mac + "): " + clusterInfo.getNic(_mac)
            print "\tclusterInfo.getNodeId(" + _mac + "): " + clusterInfo.getNodeId(_mac)
            print "\tclusterInfo.getNodeName(" + _mac + "): " + clusterInfo.getNodeName(_mac)
        print "clusterInfo.getNode(" + _name + "): " + str(clusterInfo.getNode(_name))
        
    print "\nclusterInfo.getFailoverdomainNodes(testdomain1): " + str(clusterInfo.getFailoverdomainNodes("testdomain1"))
    print "clusterInfo.getFailoverdomainPrefNode(testdomain1): " + str(clusterInfo.getFailoverdomainPrefNode("testdomain1"))
    print "\nclusterInfo: " + str(clusterInfo)
        

if __name__ == '__main__':
    main()

# $Log: ComClusterInfo.py,v $
# Revision 1.3  2007-06-08 08:24:47  andrea2
# added Debugging
#
# Revision 1.2  2007/06/05 13:32:57  andrea2
# *** empty log message ***
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/03/29 10:59:56  andrea
# inital version
#
