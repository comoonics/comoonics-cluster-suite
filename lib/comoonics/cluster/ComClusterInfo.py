"""Comoonics clusterinfo object module


This module provides functionality to query instances
of clusterrepositories

"""


# here is some internal information
# $Id: ComClusterInfo.py,v 1.9 2008-07-08 07:20:42 andrea2 Exp $
#


__version__ = "$Revision: 1.9 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterInfo.py,v $

import os

from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint

import comoonics.cluster

from comoonics.DictTools import createDomFromHash
from comoonics.ComExceptions import ComException

from comoonics import ComLog

class ClusterMacNotFoundException(ComException): pass

class ClusterInfo(object):
    """
    Provides a set of queries to use with a L{ClusterRepository} to get 
    information about the used clusterconfiguration.
    """
    
    log = ComLog.getLogger("comoonics.cluster.ComClusterInfo")
    
    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clusterrepository which instance of 
        clusterinfo (general, redhat or comoonics) has to be created.
        """
        from comoonics.cluster.ComClusterRepository import ClusterRepository, RedhatClusterRepository, ComoonicsClusterRepository
        
        if isinstance(args[0], ComoonicsClusterRepository):
            cls = ComoonicsClusterInfo
        elif isinstance(args[0], RedhatClusterRepository):
            cls = RedhatClusterInfo
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, clusterRepository):
        """
        Set used clusterRepository
        @param clusterRepository: clusterRepository to use
        @type clusterRepository: L{clusterRepository}
        """
        #Clusterrepository holds list of nodes and items like node_prefix etc.
        self.clusterRepository = clusterRepository
        
    def getClusterName(self):
        """
        @return: clustername
        @rtype: string
        """
        self.log.debug("get clustername from clusterrepository")
        return self.clusterRepository.getClusterName()
        
    
    def getNodes(self):
        """
        @return: list of all node instances
        @rtype: list
        """
        self.log.debug("get clusternodes from clusterrepository")
        return self.clusterRepository.nodeNameMap.values()
    
    def getNodeIdentifiers(self, idType="name"):
        """
        @param type: specifies type of returned identifier (could be name or id)
        @type type: string
        @return: list of all node identifiers (e.g. nodenames or nodeids)
        @rtype: list
        """
        if idType == "id":
            self.log.debug("get nodeids from clusterrepositories")
            return self.clusterRepository.nodeIdMap.keys()
        elif idType == "name":
            self.log.debug("get nodenames from clusterrepository")
            return self.clusterRepository.nodeNameMap.keys()
    
class RedhatClusterInfo(ClusterInfo):
    """
    Extends L{ClusterInfo} to provides a set of special queries 
    to use with a L{RedhatClusterRepository} to get information 
    about the used redhat clusterconfiguration.
    """
    
    def __init__(self, clusterRepository):
        """
        Set used clusterRepository
        @param clusterRepository: clusterRepository to use
        @type clusterRepository: L{RedhatClusterRepository}
        """
        super(RedhatClusterInfo, self).__init__(clusterRepository)

    def queryValue(self, query):
        """
        Provides the possibility to get specific values by 
        execute queries which are not yet implemented as a 
        direct function.
        
        @param query: xpath to query clusterinfo instance
        @type query: string
        @return: answer of proceeded query as list of strings
        @rtype: list
        """
        self.log.debug("queryValue: %s" %(query))
        _tmp1 = xpath.Evaluate(query, self.clusterRepository.getElement())
        _tmp2 = []
        for i in range(len(_tmp1)):
            _tmp2.append(_tmp1[i].value)
        return _tmp2
    
    def queryXml(self, query):
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
        self.log.debug("queryXml: %s" %(query))
        _tmp1 = xpath.Evaluate(query, self.clusterRepository.getElement())
        _tmp2 = StringIO.StringIO()
        PrettyPrint(_tmp1[0], stream=_tmp2)
        return _tmp2.getvalue()
        
    def getNode(self, name):
        """
        @param name: name of clusternode
        @type name: string
        @return: Clusternodeinstance belonging to given clusternodename
        @rtype: L{ClusterNode}
        """
        self.log.debug("get node with given name from clusterrepository: %s" %(name))
        return self.clusterRepository.nodeNameMap[name]
        
    def getNodeFromId(self, id):
        """
        @param name: id of clusternode
        @type name: int
        @return: Clusternodeinstance belonging to given nodeid
        @rtype: L{ClusterNode}
        """
        self.log.debug("get node with given id from clusterrepository: %s" %(str(id)))
        return self.clusterRepository.nodeIdMap[str(id)]
            
    def getNodeName(self, mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Clusternodename belonging to given mac-address
        @rtype: string
        """
        self.log.debug("get name of node with given mac from clusterrepository: %s" %(str(mac)))
        return self.clusterRepository.getNodeName(mac)
            
    def getNodeNameById(self, id):
        """
        @param id: nodeid
        @type id: int
        @return: Clusternodename belonging to given nodeid
        @rtype: string
        """
        self.log.debug("get name of node with given nodid from clusterrepository: %s" %(str(id)))
        return self.clusterRepository.getNodeNameById(id)

    def getNodeId(self, mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Clusternodeid belonging to given mac-address
        @rtype: string
        """
        self.log.debug("get id of node with given mac from clusterrepository: %s" %(str(mac)))
        return self.clusterRepository.getNodeId(mac)
    
    def getFailoverdomainNodes(self, failoverdomain):
        """
        @param failoverdomain: failoverdomain
        @type failoverdomain: string
        @return: Names of nodes which belong to the given failoverdomain
        @rtype: string
        """
        #no defaultvalue specified because every dailoverdomain needs to have one or more failoverdomainnodes
        self.log.debug("get failoverdomainnodes from failoverdomain %s: %s [@name='%s']/%s/@name" %(failoverdomain,comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomain_name))
        _tmp1 = self.queryValue("%s[@name='%s']/%s/@name" %(comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name))
        return _tmp1
    
    def getFailoverdomainPrefNode(self, failoverdomain):
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
            self.log.debug("query lowest priority of failoverdomainnodes belonging to %s : %s[@name='%s']/%s[@name='%s']/@priority" %(failoverdomain,comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name,_tmp1[i]))
            _tmp2 = self.queryValue("%s[@name='%s']/%s[@name='%s']/@priority" %(comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name,_tmp1[i]))[0]
            if (minprio == "0") or (_tmp2 < minprio):
                minprio = _tmp2
        #get node with lowest priority
        try:
            self.log.debug("get failoverprefdomainnode from failoverdomain %s: %s[@name='%s']/%s[@priority='%s']/@name" %(failoverdomain,comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name,str(minprio)))
            return self.queryValue("%s[@name='%s']/%s[@priority='%s']/@name" %(comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name,str(minprio)))[0]
        except IndexError:
            raise NameError("Cannot find prefered failoverdomainnode at xpath %s[@name='%s']/%s[@priority='%s']/@name" %(comoonics.cluster.failoverdomain_path,failoverdomain,comoonics.cluster.failoverdomainnode_name,str(minprio)))
    
    def getNodeIds(self):
        """
        @return: List of clusternodeids
        @rtype: list
        """
        self.log.debug("get list of nodeids from clusterrepository")
        return self.clusterRepository.nodeIdMap.keys()
    
    def getNextNodeID(self):
        """
        @return: next not used nodeid
        @rtype: int
        """
        idlist = self.getNodeIds()
        idlist.sort()
        return int(idlist[-1])+1

class ComoonicsClusterInfo(RedhatClusterInfo):
    """
    Extends L{RedhatClusterInfo} to provides a set of special queries 
    to use with a L{ComoonicsClusterRepository} to get information 
    about the used comoonics clusterconfiguration.
    """
    def __init__(self, clusterRepository):
        """
        Set used clusterRepository
        @param clusterRepository: clusterRepository to use
        @type clusterRepository: L{ComoonicsClusterRepository}
        """
        super(ComoonicsClusterInfo, self).__init__(clusterRepository)
    
    def getNic(self, mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Instance of Network interface with given mac-address
        @rtype: L{ComoonicsClusterNodeNic}
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        for node in self.getNodes():
            try:
                self.log.debug("get clusternodenic with given mac: %s" %(str(mac)))
                return node.getNic(mac).getName()
            except KeyError:
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: %s" %(str(mac)))
    
def main():
    """
    Method to test module. Creates a ClusterInfo object and test all defined methods 
    on an cluster.conf example (use a loop to proceed every node).
    """
    from comoonics.cluster.ComClusterRepository import ClusterRepository
    
    # create Reader object
    reader = Sax2.Reader()

    # parse the document and create clusterrepository object
    # can use only cluster2.conf for test, cluster.conf MUST cause an not 
    # handled exception (because lack of a device name)
    my_file = os.fdopen(os.open("test/cluster2.conf", os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()
    element = xpath.Evaluate(comoonics.cluster.cluster_path, doc)[0]

    #create clusterRepository Object
    clusterRepository = ClusterRepository(element, doc)

    #create comclusterinfo object
    clusterInfo = ClusterInfo(clusterRepository)
    
    #test functions
    print "clusterInfo.getNodeIdentifiers('name'): " + str(clusterInfo.getNodeIdentifiers("name"))
    print "clusterInfo.getNodeIds(): " + str(clusterInfo.getNodeIds())
    
    print "Next free ID: " + str(clusterInfo.getNextNodeID())
    
    my_file = os.fdopen(os.open("test/cluster2.conf", os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()
    element = xpath.Evaluate(comoonics.cluster.cluster_path, doc)[0]
    #create clusterRepository Object
    clusterRepository = ClusterRepository(element, doc)
    print "Typ ClusterRepository: " + str(type(clusterRepository))
    #create comclusterinfo object
    clusterInfo = ClusterInfo(clusterRepository)
    print "Typ ClusterInfo: " + str(type(clusterInfo))
    _tmpnode = clusterInfo.getNodeFromId(clusterInfo.getNextNodeID()-1)
    _defaults = {"clusternode":{"nodeid":str(clusterInfo.getNextNodeID()),"votes":"1","com_info":{"rootvolume":{"name":_tmpnode.getRootvolume()},"eth":{"name":"eth0"}}}}
    _mydom = createDomFromHash(_defaults)
    #default = xpath.Evaluate("/cluster/clusternodes/clusternode",doc)[-1]
    _tmp = xpath.Evaluate(comoonics.cluster.clusternode_path, doc)
    _node = doc.importNode(_mydom.documentElement,True)  
    #_tmp[0].insertBefore(_node,default)
    _tmp[0].appendChild(_node)
    PrettyPrint(_tmp[0])
    #return

    _nodes = clusterInfo.getNodes()
    print "clusterInfo.getNodes(): %s" %(str(_nodes))
    print "clusterInfo.queryValue('%s/@name'): " %(comoonics.cluster.clusternode_name) + str(clusterInfo.queryValue("%s/@name" %(comoonics.cluster.clusternode_path)))
    print "clusterInfo.queryXml('%s/@name'): " %(comoonics.cluster.clusternode_name) + str(clusterInfo.queryXml("%s/@name" %(comoonics.cluster.clusternode_path)))
    
    for node in _nodes:
        print "\nName: %s  - ID: %s" %(node.getName(),node.getId())
        _name = node.getName()
        _nics = node.getNics()
        for _nic in _nics:
            _mac = _nic.getMac()
            try:
                print "clusterInfo.getNic(%s): %s" %(_mac,clusterInfo.getNic(_mac))
                print "\tclusterInfo.getNodeId(%s): %s: " %(_mac,clusterInfo.getNodeId(_mac))
                print "\tclusterInfo.getNodeName(%s): %s: " %(_mac,clusterInfo.getNodeName(_mac))
            except ClusterMacNotFoundException:
                print "Verify that nic %s does not have an mac-address" %(_nic.getName())
        print "clusterInfo.getNode(" + _name + "): " + str(clusterInfo.getNode(_name))
        
    print "\nclusterInfo.getFailoverdomainNodes(testdomain1): %s" %(str(clusterInfo.getFailoverdomainNodes("testdomain1")))
    print "clusterInfo.getFailoverdomainPrefNode(testdomain1): %s" %(str(clusterInfo.getFailoverdomainPrefNode("testdomain1")))
    print "\nclusterInfo.getFailoverdomainNodes(testdomain2): %s" %(str(clusterInfo.getFailoverdomainNodes("testdomain2")))
    print "clusterInfo.getFailoverdomainPrefNode(testdomain2): %s" %(str(clusterInfo.getFailoverdomainPrefNode("testdomain2")))
    
    print "\nclusterInfo: %s" %(str(clusterInfo))
        
if __name__ == '__main__':
    main()

# $Log: ComClusterInfo.py,v $
# Revision 1.9  2008-07-08 07:20:42  andrea2
# Use constants from __init__ for xpathes (except attributes)
#
# Revision 1.8  2008/06/17 16:22:55  mark
# added support for query nodenamebyid. This is needed for passing the nodeid as boot parameter.
#
# Revision 1.7  2008/02/27 09:16:40  mark
# added getClusterName support
#
# Revision 1.6  2007/09/19 06:40:53  andrea2
# adapted source code in dependence on Python Style Guide, removed not used imports and statements, adapted some debug messages, added NameError-Exception for Method getFailoverdomainPrefNode
#
# Revision 1.5  2007/08/14 08:37:01  andrea2
# extended docu and test
#
# Revision 1.4  2007/08/06 12:09:27  andrea2
# Added more Docu, removed ClusterMetainfo
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
