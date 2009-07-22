"""Comoonics clusterinfo object module


This module provides functionality to query instances
of clusterrepositories

"""


# here is some internal information
# $Id: ComClusterInfo.py,v 1.12 2009-07-22 08:37:09 marc Exp $
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


__version__ = "$Revision: 1.12 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterInfo.py,v $


from xml import xpath
from xml.dom.ext import PrettyPrint
from comoonics.XmlTools import xpathjoin, xpathsplit, XPATH_SEP

from comoonics.ComExceptions import ComException

from comoonics import ComLog
from comoonics.cluster.ComClusterRepository import RedHatClusterRepository, ComoonicsClusterRepository, ClusterObject

class ClusterMacNotFoundException(ComException): pass

class ClusterInfo(ClusterObject):
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
        if isinstance(args[0], ComoonicsClusterRepository):
            cls = ComoonicsClusterInfo
        elif isinstance(args[0], RedHatClusterRepository):
            cls = RedHatClusterInfo
        return object.__new__(cls) #, *args, **kwds)
    
    def __init__(self, clusterRepository):
        """
        Set used clusterRepository
        @param clusterRepository: clusterRepository to use
        @type clusterRepository: L{clusterRepository}
        """
        #Clusterrepository holds list of nodes and items like node_prefix etc.
        super(ClusterInfo, self).__init__(clusterRepository.getElement())
        self.clusterRepository = clusterRepository
        
    def getClusterName(self):
        """
        @return: clustername
        @rtype: string
        """
        self.log.debug("get clustername from clusterrepository")
        return self.clusterRepository.getClusterName()
        
    
    def getNodes(self, active=False):
        """
        @param active: only returns actively joined nodes
        @type active: boolean
        @return: list of all node instances
        @rtype: list
        """
        self.log.debug("get clusternodes from clusterrepository(active=%s)" %active)
        _nodes=list()
        for _node in self.clusterRepository.nodeNameMap.values():
            if not active or _node.isActive():
                _nodes.append(_node)
        return _nodes
    
    def getNodeIdentifiers(self, idType="name", active=False):
        """
        @param idType: specifies type of returned identifier (could be name or id)
        @type idType: string
        @param active: only returns actively joined nodes
        @type active: boolean
        @return: list of all node identifiers (e.g. nodenames or nodeids)
        @rtype: list
        """
        _nodes=self.getNodes(active)
        _ids=list()
        if idType == "id":
            self.log.debug("get nodeids from clusterrepositories(active=%s)" %active)
            for _node in _nodes:
                _ids.append(_node.getId())
        elif idType == "name":
            self.log.debug("get nodenames from clusterrepository(active=%s)" %active)
            for _node in _nodes:
                _ids.append(_node.getName())
        return _ids
    
class RedHatClusterInfo(ClusterInfo):
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
        from helper import RedHatClusterHelper
        super(RedHatClusterInfo, self).__init__(clusterRepository)
        self.helper=RedHatClusterHelper()
        self.addNonStatic("name", xpathjoin(RedHatClusterRepository.getDefaultClustatXPath(), RedHatClusterRepository.element_clustat_cluster, "@"+RedHatClusterRepository.attribute_clustat_cluster_name))
#        self.addNonStatic(RedhatClusterInfo, "id")
        self.addNonStatic("generation",         xpathjoin(RedHatClusterRepository.getDefaultClustatXPath(), RedHatClusterRepository.element_clustat_cluster, "@"+RedHatClusterRepository.attribute_clustat_cluster_generation))
        self.addNonStatic("quorum_quorate",     xpathjoin(RedHatClusterRepository.getDefaultClustatXPath(), RedHatClusterRepository.element_quorum, "@"+RedHatClusterRepository.attribute_quorum_quorate))
        self.addNonStatic("quorum_groupmember", xpathjoin(RedHatClusterRepository.getDefaultClustatXPath(), RedHatClusterRepository.element_quorum, "@"+RedHatClusterRepository.attribute_quorum_groupmember))

    def query(self, param, *params, **keys):
        if keys and keys.has_key("pathroot"):
            _pathroot=keys["pathroot"]
        elif params and len(params)>=1:
            _pathroot=params[0]
        else:
            _pathroot=RedHatClusterRepository.getDefaultClustatXPath()
        if xpathsplit(_pathroot)[0] == RedHatClusterRepository.element_clustat:
            if self.non_statics.get(param, None) != None:
                return self.helper.queryStatusElement(query= xpathjoin(_pathroot, self.non_statics.get(param)))
            else:
                return self.helper.queryStatusElement(query= xpathjoin(_pathroot, "@"+param))
        else:
            return self.queryValue(param)


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
        
    def getNodeFromId(self, _id):
        """
        @param name: _id of clusternode
        @type name: int
        @return: Clusternodeinstance belonging to given nodeid
        @rtype: L{ClusterNode}
        """
        self.log.debug("get node with given id from clusterrepository: %s" %(str(_id)))
        return self.clusterRepository.nodeIdMap[str(_id)]
            
    def getNodeName(self, mac):
        """
        @param mac: mac-address
        @type mac: string
        @return: Clusternodename belonging to given mac-address
        @rtype: string
        """
        self.log.debug("get name of node with given mac from clusterrepository: %s" %(str(mac)))
        return self.clusterRepository.getNodeName(mac)
            
    def getNodeNameById(self, _id):
        """
        @param _id: nodeid
        @type id: int
        @return: Clusternodename belonging to given nodeid
        @rtype: string
        """
        self.log.debug("get name of node with given nodid from clusterrepository: %s" %(str(_id)))
        return self.clusterRepository.getNodeNameById(_id)

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
        _xpath=xpathjoin(RedHatClusterRepository.getDefaultClusterFailoverDomain(failoverdomain), RedHatClusterRepository.element_failoverdomainnode, "@"+RedHatClusterRepository.attribute_failoverdomainnode_name)
        self.log.debug("get failoverdomainnodes from failoverdomain %s: %s" %(failoverdomain,_xpath))
        _tmp1 = self.queryValue(_xpath)
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
            _xpath=xpathjoin(RedHatClusterRepository.getDefaultClusterFailoverDomain(failoverdomain), RedHatClusterRepository.element_failoverdomainnode+"[@"+RedHatClusterRepository.attribute_failoverdomainnode_name+"=\""+_tmp1[i]+"\"]", "@"+RedHatClusterRepository.attribute_failoverdomainnode_priority)
            self.log.debug("query lowest priority of failoverdomainnodes belonging to %s : %s" %(failoverdomain,_xpath))
            _tmp2 = self.queryValue(_xpath)[0]
            if (minprio == "0") or (_tmp2 < minprio):
                minprio = _tmp2
        #get node with lowest priority
        try:
            _xpath=xpathjoin(RedHatClusterRepository.getDefaultClusterFailoverDomain(failoverdomain), RedHatClusterRepository.element_failoverdomainnode+"[@"+RedHatClusterRepository.attribute_failoverdomainnode_priority+"=\""+str(minprio)+"\"]", "@"+RedHatClusterRepository.attribute_failoverdomainnode_name)
            self.log.debug("get failoverprefdomainnode from failoverdomain %s: %s" %(failoverdomain, _xpath))
            return self.queryValue(_xpath)[0]
        except IndexError:
            raise NameError("Cannot find prefered failoverdomainnode for domain %s." %failoverdomain) 
    
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

class ComoonicsClusterInfo(RedHatClusterInfo):
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

# $Log: ComClusterInfo.py,v $
# Revision 1.12  2009-07-22 08:37:09  marc
# Fedora compliant
#
# Revision 1.11  2009/05/27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.10  2008/08/05 13:09:15  marc
# - fixed bugs with constants
# - optimized imports
# - added nonstatic attributes
# - added helper class
#
# Revision 1.9  2008/07/08 07:20:42  andrea2
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
