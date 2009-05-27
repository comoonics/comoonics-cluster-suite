"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.17 2009-05-27 18:31:59 marc Exp $
#


__version__ = "$Revision: 1.17 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterRepository.py,v $

from xml import xpath

from comoonics import ComLog
from comoonics.ComDataObject import  DataObject
from comoonics.ComExceptions import ComException
from comoonics.DictTools import searchDict, createDomFromHash
from comoonics.XmlTools import xpathjoin, XPATH_SEP

log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")

class ClusterMacNotFoundException(ComException): pass
class ClusterIdNotFoundException(ComException): pass
class ClusterRepositoryConverterNotFoundException(ComException): pass

class ClusterObject(DataObject):
    non_statics=dict()
    def __init__(self, *params, **kwds):
        super(ClusterObject, self).__init__(*params, **kwds)
        self.non_statics=dict()
    def isstatic(self, _property):
        if self.non_statics.has_key(_property):
            return False
        return True
    def addNonStatic(self, name, rest=None):
        path_end=self.non_statics
        path_end[name]=rest
    def query(self, _property, *params, **keys):
        pass
    def __getattr__(self, value):
        if not self.isstatic(value):
            return self.query(value)
        else:
            return DataObject.__getattribute__(self, value)
                
class ClusterRepository(ClusterObject):
    """
    Provides generall functionality for a clusterrepository instance
    """
    log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")
    CONVERTERS=dict()

    def __new__(cls, *args, **kwds):
        """
        Decides by type of given clustermetainfo which 
        instance of clusterrepository (general, redhat 
        or comoonics) has to be created.
        args = (element,doc,options)
        """
        from xml.dom.ext.reader import Sax2
        if len(args) >= 1 and isinstance(args[0], basestring):
            reader = Sax2.Reader()
            _xml=open(args[0])
            doc = reader.fromStream(_xml)
            _xml.close()
            if len(xpath.Evaluate(ComoonicsClusterRepository.getDefaultComoonicsXPath(), doc.documentElement)) > 0:
                cls = ComoonicsClusterRepository
            elif len(xpath.Evaluate(RedHatClusterRepository.getDefaultClusterNodeXPath(), doc.documentElement)) > 0:
                cls = RedHatClusterRepository
        if len(args) >= 2:
            if (args[0] != None):                
                if xpath.Evaluate(ComoonicsClusterRepository.getDefaultComoonicsXPath(""), args[0]) or len(args[2]) == 0:
                    cls = ComoonicsClusterRepository
                elif xpath.Evaluate(RedHatClusterRepository.getDefaultClusterNodeXPath(), args[0]):
                    cls = RedHatClusterRepository
                    
            elif type(args[2]) == dict:
                from ComClusterInfo.ComoonicsClusterInfo import element_osr, element_clusternode
                if searchDict(args[2],element_osr):
                    cls = ComoonicsClusterRepository
                elif searchDict(args[2],element_clusternode):
                    cls = RedHatClusterRepository
                
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, *params, **kwds):
        #node dictionaries depend on clustertype, setting later!
        self.nodeNameMap = {}
        self.nodeIdMap = {}
        
        super(ClusterRepository, self).__init__(*params, **kwds)
        
    def convert(self, _type="ocfs2"):
        if self.CONVERTERS.has_key(_type):
            return self.CONVERTERS[_type](self)
        else:
            raise ClusterRepositoryConverterNotFoundException("Could not find converter of clusterrepository for type %s" %_type)
            
class RedHatClusterRepository(ClusterRepository):
    """
    Represents the clusterconfiguration file of an redhat 
    cluster as an L{DataObject}. Extends generall 
    clusterrepository by special queries for this cluster 
    type.
    """

    # xpathes and attribute names
    element_cluster = "cluster"
    attribute_cluster_name = "name"
    attribute_cluster_configversion = "config_version"

    element_cman = "cman"
    element_cman_expectedvotes_attribute = "expected_votes"
    
    element_clusternodes = "clusternodes"

    element_rm = "rm"
    element_failoverdomains = "failoverdomains"
    element_failoverdomain = "failoverdomain"
    attribute_failoverdomain_name = "name"
    element_failoverdomainnode = "failoverdomainnode"
    attribute_failoverdomainnode_name = "name"
    attribute_failoverdomainnode_priority = "priority"

    element_clusternode = "clusternode"
    attribute_clusternode_name = "name"
    attribute_clusternode_nodeid = "nodeid"
    attribute_clusternode_votes = "votes"
    
    element_clustat="clustat"
    element_clustat_cluster="cluster"
    attribute_clustat_cluster_name="name"
    attribute_clustat_cluster_generation="generation"
    element_clustat_nodes="nodes"
    element_clustat_node="node"
    attribute_clustat_node_name="name"

    element_quorum="quorum"
    attribute_quorum_quorate="quorate"
    attribute_quorum_groupmember="groupmember"
    
    xpath_clustat=xpathjoin(element_cluster, element_clustat)

    def getDefaultClusterConf():
        return "/etc/cluster/cluster.conf"
    getDefaultClusterConf=staticmethod(getDefaultClusterConf)
    
    def getDefaultClusterXPath():
        return xpathjoin(XPATH_SEP, RedHatClusterRepository.element_cluster)
    getDefaultClusterXPath=staticmethod(getDefaultClusterXPath)

    def getDefaultClusterNodeXPath():
        return xpathjoin(RedHatClusterRepository.getDefaultClusterXPath(), RedHatClusterRepository.element_clusternodes, RedHatClusterRepository.element_clusternode)
    getDefaultClusterNodeXPath=staticmethod(getDefaultClusterNodeXPath)
    
    def getDefaultClusterFailoverDomain(domain=""):
        return xpathjoin(RedHatClusterRepository.getDefaultClusterXPath(), RedHatClusterRepository.element_rm, RedHatClusterRepository.element_failoverdomains, RedHatClusterRepository.element_failoverdomain+'[@'+RedHatClusterRepository.attribute_failoverdomain_name+'="'+domain+'"]')
    getDefaultClusterFailoverDomain=staticmethod(getDefaultClusterFailoverDomain)
    
    def getDefaultClustatXPath():
        return xpathjoin(XPATH_SEP, RedHatClusterRepository.element_clustat)
    getDefaultClustatXPath=staticmethod(getDefaultClustatXPath)
    
    def __init__(self, element=None, doc=None, *options):
        from comoonics.cluster.ComClusterNode import ClusterNode
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR options to create a new element")
        elif element == None:
            # if no element is given create a "default" cluster.conf is generated from given hash
            if (len(options) == 2) or (len(options) == 3):
                doc = createDomFromHash(options[0],defaults=options[1])
            else:
                doc = createDomFromHash(options[0])
            element = xpath.Evaluate(RedHatClusterRepository.getDefaultClusterXPath(), doc)[0]

        super(RedHatClusterRepository, self).__init__(element, doc)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = xpath.Evaluate(RedHatClusterRepository.getDefaultClusterNodeXPath(), self.getElement())
        for i in range(len(_nodes)):
            _node = ClusterNode(_nodes[i], doc)
            self.nodeNameMap[_node.getName()] = _node
            self.nodeIdMap[_node.getId()] = _node
            
    def setClusterName(self,name):
        """
        @param: new clustername
        @type: string
        """
        self.log.debug("set name attribute to: " + str(name))
        #no try-except construct because name ist an obligatory object
        return self.setAttribute(RedHatClusterRepository.attribute_cluster_name,name)

    def getClusterName(self):
        """
        @return: clustername
        @rtype: string
        """
        return self.getAttribute(RedHatClusterRepository.attribute_cluster_name)


    def getNodeName(self, mac):
        """
        @param mac: Macaddress of node
        @type mac: L{string}  
        @return: Nodename
        @rtype: string
        @raise ClusterMacNotFoundException: Raises Exception if search for node with given mac failed.
        """
        self.log.debug("get clusternodenic belonging to given mac: " + str(mac))
        for node in self.nodeIdMap.values():
            try:
                node.getNic(mac)
                self.log.debug("get name belonging to searched clusternodenic: " + node.getName())
                return node.getName()
            except KeyError:
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + str(mac))

    def getNodeNameById(self, _id):
        """
        @param id: id of node
        @type int
        @return: Nodename
        @rtype: string
        @raise ClusterIdNotFoundException: Raises Exception if search for node with given mac failed.
        """
        if self.nodeIdMap.has_key(_id):
            return self.nodeIdMap.get(_id).getName()
        
        raise ClusterIdNotFoundException("Cannot find node with id " + str(id))

    def setConfigVersion(self,version):
        """
        @param: new clustername
        @type: string
        """
        self.log.debug("set version attribute to: " + str(version))
        #no try-except construct because name ist an obligatory object
        return self.setAttribute(RedHatClusterRepository.attribute_cluster_configversion,version)

    def getConfigVersion(self):
        """
        @return: clustername
        @rtype: string
        """
        return self.getAttribute(RedHatClusterRepository.attribute_cluster_configversion)
    
    def getNodeId(self, mac):
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
                continue
        raise ClusterMacNotFoundException("Cannot find device with given mac: " + mac)
    
    def createClusterNodesElement(self,myhash,doc=None,element=None,initial=True):
        """
        Creates or manipulates a Nodeelement from given hash to include in a DOM (cluster.conf)
        @param myhash: Hash to create DOM
        @type myhash: L{dict}
        @param doc: if given, expand with content from hash
        @type doc: L{DOM}
        @param element: element in doc to work on
        @param clusternodeelementname: define element which includes clusternodes, default is clusternodes
        @type clusternodelementname: L{string} 
        """
        for key, value in myhash.items():
            # if initial is set, create the clusternode "root"element and use it as initial point
            if initial:
                newelement = doc.createElement(key)
            # if initial is not set use the given element as initial point
            else:
                newelement = element

            # if value is no dict (=> subordinate element) or 
            # list (=> subordinate element with multiple apereance)
            # assume that value must be an attribute of the actuall element            
            if (type(value) != dict) and (type(value) != list):
                newelement.setAttribute(key,str(value))
            # if value is of type dict and initial is not set
            # create and append a subordinate element with name value
            # if initial is true the element has been already created
            elif not initial and (type(value) == dict):
                # nodeelement will be the "working-on" element for the next recursion level
                # if value is of type dict it must be an new element with name key
                nodeelement = doc.createElement(key)                    
                newelement.appendChild(nodeelement)
            else:
                # nodeelement will be the "working-on" element for the next recursion level
                # if type of value is not dict or initial is set use the actual working-on 
                # element as nodeelement
                nodeelement = newelement
                
            _tmp = []
            # if more than one clusternode are defined, build them in rotation
            if (type(value) == list) and initial:
                for i in value:
                    _tmp.append(self.createClusterNodesElement({key:i},doc,element,True))
                return _tmp
            # if an element of the clusternode has multiple apereance, build the elements in rotation
            elif type(value) == list and not initial:
                for i in value:
                    self.createClusterNodesElement({key:i},doc,element,False)
            elif type(value) == dict:
                self.createClusterNodesElement(value,doc,nodeelement,False)
        
        return newelement

class ComoonicsClusterRepository(RedHatClusterRepository):
    """
    Represents the clusterconfiguration file of an 
    comoonics cluster as an L{DataObject}.
    """
    
    element_comoonics = "com_info"
    element_rootvolume = "rootvolume"
    attribute_rootvolume_name = "name"
    attribute_rootvolume_fstype = "fstype"
    attribute_rootvolume_mountopts = "mountopts"
    element_netdev = "eth"
    attribute_netdev_name="name"
    attribute_netdev_mac="mac"
    attribute_netdev_ip="ip"
    attribute_netdev_gateway="gateway"
    attribute_netdev_netmask="mask"
    attribute_netdev_master="master"
    attribute_netdev_slave="slave"
    element_syslog = "syslog"
    attribute_syslog_name = "name"
    element_scsi = "scsi"
    attribute_scsi_failover = "failover"

    def getDefaultComoonicsXPath(_nodename=None):
        if not _nodename:
            return xpathjoin(RedHatClusterRepository.getDefaultClusterNodeXPath(), ComoonicsClusterRepository.element_comoonics)
        else:
            return xpathjoin(RedHatClusterRepository.getDefaultClusterNodeXPath()+"["+RedHatClusterRepository.attribute_clusternode_name+"=\""+_nodename+"\"]", ComoonicsClusterRepository.element_comoonics)
    getDefaultComoonicsXPath=staticmethod(getDefaultComoonicsXPath)

    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR filename attribute")
        else:
            super(ComoonicsClusterRepository, self).__init__(element, doc, *options)

    def createOCFS2ClusterConf(clusterRepository):
        """
        returns a string containing a valid OCFS2 cluster configuration
        """
        __NODE_TMPL__="""
node:
        ip_port = %(tcp_port)u
        ip_address = %(ip_address)s
        number = %(nodeid)s
        name = %(name)s
        cluster = %(clustername)s
"""
        __CL_TMPL__="""
cluster:
        node_count = %(nodecount)u
        name = %(clustername)s
"""
        import StringIO

        output = StringIO.StringIO()

        _nodehash=dict()
        for _node in clusterRepository.nodeIdMap.values():
            _nodehash.clear()
            _nodehash["tcp_port"]=int(_node.getAttribute("tcp_port", "7777"))
            _nodehash["clustername"]=clusterRepository.getClusterName()
            _nodehash["nodeid"]=_node.getId()
            _nodehash["name"]=_node.getName()
            _nodehash["ip_address"]=_node.getIPs()[0]
            #for _nic in _node.getNics():
            #    _ip=_nic.getIP()
            #    if _ip != "":
            #        _nodehash["ip_address"]=_ip
            output.write(__NODE_TMPL__ %_nodehash)
        _clusterhash=dict()
        _clusterhash["nodecount"]=len(clusterRepository.nodeIdMap.keys())
        _clusterhash["clustername"]=clusterRepository.getClusterName()
        output.write(__CL_TMPL__ %_clusterhash)
        
        return output.getvalue()
    
    createOCFS2ClusterConf=staticmethod(createOCFS2ClusterConf)

ClusterRepository.CONVERTERS["ocfs2"]=ComoonicsClusterRepository.createOCFS2ClusterConf

# $Log: ComClusterRepository.py,v $
# Revision 1.17  2009-05-27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.16  2008/08/06 11:18:28  marc
# - fixed more bugs with xpath
#
# Revision 1.15  2008/08/05 18:28:18  marc
# more bugfixes
#
# Revision 1.14  2008/08/05 13:09:40  marc
# - fixed bugs with constants
# - optimized imports
# - added nonstatic attributes
# - added helper class
#
# Revision 1.13  2008/07/08 07:34:30  andrea2
# Improved imports (no imports with *), sourced out dict-tools, sourced out validate_xml to xmltools, use constants (xpath, filenames) from __init__
#
# Revision 1.12  2008/06/17 16:22:55  mark
# added support for query nodenamebyid. This is needed for passing the nodeid as boot parameter.
#
# Revision 1.11  2008/06/10 10:16:15  marc
# - added ClusterConf conversion
#
# Revision 1.10  2008/06/04 10:28:28  marc
# - added ocfs2config creation
#
# Revision 1.9  2008/05/20 11:14:39  marc
# - Error better readable
#
# Revision 1.8  2008/04/07 09:45:22  andrea2
# added searchDict, applyDefaults(apply defaultvalues to a hash), setConfigVersion, createDomFromHash, adds posibility to hand over a hash over to ClusterRepository
#
# Revision 1.7  2008/02/27 09:16:40  mark
# added getClusterName support
#
# Revision 1.6  2007/09/19 06:42:28  andrea2
# adapted source code in dependence on Python Style Guide, removed not used imports and statements
#
# Revision 1.5  2007/09/04 07:52:25  andrea2
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
