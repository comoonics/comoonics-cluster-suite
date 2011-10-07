"""Comoonics clusterRepository object module


Represents a given clusterconfiguration as an 
L{DataObject} and Maps of L{ClusterNode}. Also 
includes some methods for simple queries and 
provides generall query functionality by been 
inherited from L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterRepository.py,v 1.19 2010-11-21 21:45:28 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = "$Revision: 1.19 $"

from comoonics import ComLog
from comoonics.DictTools import createDomFromHash
import comoonics.XmlTools
from comoonics.cluster import ClusterObject, ClusterIdNotFoundException, ClusterMacNotFoundException, ClusterRepositoryConverterNotFoundException
from comoonics.cluster.ComClusterInfo import ClusterInfo, RedHatClusterInfo, ComoonicsClusterInfo, SimpleComoonicsClusterInfo
log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")

                
class ClusterRepository(ClusterObject):
    """
    Provides generall functionality for a clusterrepository instance
    """
    log = ComLog.getLogger("comoonics.cdsl.ComClusterRepository")
    CONVERTERS=dict()

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
        
    def __str__(self):
        return "%s(nodes: %u)" %(self.__class__.__name__, len(self.nodeIdMap))
    
    def getClusterInfoClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        return ClusterInfo

    def getClusterNodeClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        from comoonics.cluster.ComClusterNode import ClusterNode
        return ClusterNode

class SimpleComoonicsClusterRepository(ClusterRepository):
    """
    Class that implements a simple cluster repository that does not consist of any configuration file but is
    defined from the constructor parameters.
    """
    def __init__(self, maxnodeidnum=1, nodeids=None, nodenames=None, clusterconf=None):
        """
        Constructor that creates a new cluster repository from outside information.
        @param nodeids: an optional list of nodeids (list of numbers)
        @type  nodeids: L{list} of L{int}
        @param maxnodeid: if no nodeids list is given maxnodeid will implicitly create a list of ids from 1 to maxnodeid.
        @type  maxnodeid: L{int} default is 1
        @param nodenames: an optional list of nodenames (list of strings).
        @type  nodenames: L{list} of L{string} which represent the list of nodenames.   
        """
        super(SimpleComoonicsClusterRepository, self).__init__()
        num_nodeids=maxnodeidnum
        if nodeids and not maxnodeidnum:
            num_nodeids=len(nodeids)
            
        for index in range(num_nodeids):
            nodeid=index
            if nodeids:
                nodeid=nodeids.get(index, index)
            nodename=None
            if nodenames:
                nodename=nodename=nodenames.get(index, None)
            node=self.getClusterNodeClass()(nodeid=nodeid, nodename=nodename)
            self.nodeIdMap[nodeid]=node
            if nodename:
                self.nodeNameMap[nodename]=node
    
    def getClusterInfoClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        return SimpleComoonicsClusterInfo

    def getClusterNodeClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        from comoonics.cluster.ComClusterNode import SimpleComoonicsClusterNode
        return SimpleComoonicsClusterNode
            
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
    
    xpath_clustat=comoonics.XmlTools.xpathjoin(element_cluster, element_clustat)

    def getDefaultClusterConf():
        return "/etc/cluster/cluster.conf"
    getDefaultClusterConf=staticmethod(getDefaultClusterConf)
    
    def getDefaultClusterXPath():
        return comoonics.XmlTools.xpathjoin(comoonics.XmlTools.XPATH_SEP, RedHatClusterRepository.element_cluster)
    getDefaultClusterXPath=staticmethod(getDefaultClusterXPath)

    def getDefaultClusterNodeXPath():
        return comoonics.XmlTools.xpathjoin(RedHatClusterRepository.getDefaultClusterXPath(), RedHatClusterRepository.element_clusternodes, RedHatClusterRepository.element_clusternode)
    getDefaultClusterNodeXPath=staticmethod(getDefaultClusterNodeXPath)
    
    def getDefaultClusterFailoverDomain(domain=""):
        return comoonics.XmlTools.xpathjoin(RedHatClusterRepository.getDefaultClusterXPath(), RedHatClusterRepository.element_rm, RedHatClusterRepository.element_failoverdomains, RedHatClusterRepository.element_failoverdomain+'[@'+RedHatClusterRepository.attribute_failoverdomain_name+'="'+domain+'"]')
    getDefaultClusterFailoverDomain=staticmethod(getDefaultClusterFailoverDomain)
    
    def getDefaultClustatXPath():
        return comoonics.XmlTools.xpathjoin(comoonics.XmlTools.XPATH_SEP, RedHatClusterRepository.element_clustat)
    getDefaultClustatXPath=staticmethod(getDefaultClustatXPath)
    
    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR options to create a new element")
        elif element == None:
            # if no element is given create a "default" cluster.conf is generated from given hash
            if (len(options) == 2) or (len(options) == 3):
                doc = createDomFromHash(options[0],defaults=options[1])
            else:
                doc = createDomFromHash(options[0])
            element = comoonics.XmlTools.evaluateXPath(RedHatClusterRepository.getDefaultClusterXPath(), doc)[0]

        super(RedHatClusterRepository, self).__init__(element, doc)
        
        #fill dictionaries with nodename:nodeobject, nodeid:nodeobject and nodeident:nodeobject
        _nodes = comoonics.XmlTools.evaluateXPath(RedHatClusterRepository.getDefaultClusterNodeXPath(), self.getElement())
        for i in range(len(_nodes)):
            _node = self.getClusterNodeClass()(_nodes[i], doc)
            self.nodeNameMap[_node.getName()] = _node
            self.nodeIdMap[_node.getId()] = _node
    
    def getClusterInfoClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        return RedHatClusterInfo

    def getClusterNodeClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        from comoonics.cluster.ComClusterNode import RedHatClusterNode
        return RedHatClusterNode
            
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
            return comoonics.XmlTools.xpathjoin(RedHatClusterRepository.getDefaultClusterNodeXPath(), ComoonicsClusterRepository.element_comoonics)
        else:
            return comoonics.XmlTools.xpathjoin(RedHatClusterRepository.getDefaultClusterNodeXPath()+"["+RedHatClusterRepository.attribute_clusternode_name+"=\""+_nodename+"\"]", ComoonicsClusterRepository.element_comoonics)
    getDefaultComoonicsXPath=staticmethod(getDefaultComoonicsXPath)

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

    def __init__(self, element=None, doc=None, *options):
        if ((element == None) and (len(options) == 0)) or ((element != None) and (len(options) != 0)):
            raise AttributeError("You have to specify element OR filename attribute")
        else:
            super(ComoonicsClusterRepository, self).__init__(element, doc, *options)
    
    def getClusterInfoClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        return ComoonicsClusterInfo

    def getClusterNodeClass(self):
        """
        Returns the class for the cluster information relevant to this ClusterRepository
        @returns L{comoonics.cluster.ComClusterInformation.ClusterInformation}
        """
        from comoonics.cluster.ComClusterNode import ComoonicsClusterNode
        return ComoonicsClusterNode

ClusterRepository.CONVERTERS["ocfs2"]=ComoonicsClusterRepository.createOCFS2ClusterConf
