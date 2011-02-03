"""Comoonics node object module


Represents cluster nodes as an L{DataObject}. 
Node instances can be automatically generated 
by a clusterrepository.

"""

# here is some internal information
# $Id: ComClusterNode.py,v 1.14 2011-02-03 14:41:36 marc Exp $
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


__version__ = "$Revision: 1.14 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNode.py,v $

import os

from ComClusterRepository import RedHatClusterRepository, ComoonicsClusterRepository, ClusterObject
from ComClusterNodeNic import ComoonicsClusterNodeNic

from comoonics import ComLog
from comoonics.XmlTools import xpathjoin

class ClusterNode(ClusterObject):
    """
    Provides generall functionality for a clusternode instance
    """
    
    log = ComLog.getLogger("comoonics.cluster.ComClusterNode")
    
    def __new__(cls, *args, **kwds):
        """
        Decides by content of given element which 
        instance of clusternode (general, redhat 
        or comoonics) has to be created.
        """
        try:
            import comoonics.XmlTools
            comoonics.XmlTools.evaluateXPath(ComoonicsClusterRepository.getDefaultComoonicsXPath(""), args[0])
        except NameError:
            if args[0].getAttribute("name"):
                cls = RedHatClusterNode
            else:
                cls = ClusterNode
        else:
            cls = ComoonicsClusterNode
            
        return object.__new__(cls) #, *args, **kwds)
    
    def __init__(self, element, doc=None):
        super(ClusterNode, self).__init__(element, doc)
    
    def getName(self):
        """placeholder for getName method"""
        pass
    
    def getId(self):
        """placeholder for getId method"""
        pass
    def isActive(self):
        """placeholder for isActvie method. Should return True if node is actively joined to the given cluster"""
        return True                

class RedHatClusterNode(ClusterNode):
    """
    Extends the generall ClusterNode class 
    by adding special queries for this cluster 
    type.
    """

    clustat_pathroot=xpathjoin(RedHatClusterRepository.getDefaultClustatXPath(), RedHatClusterRepository.element_clustat_nodes, RedHatClusterRepository.element_clustat_node+'[@'+RedHatClusterRepository.attribute_clustat_node_name+'="%s"]')
    
    def __init__(self, element, doc=None):
        super(RedHatClusterNode, self).__init__(element, doc)
        from helper import RedHatClusterHelper, HelperNotSupportedError
        try:
            self.helper=RedHatClusterHelper()
        except HelperNotSupportedError:
            self.helper=None
        self.addNonStatic("state")
        self.addNonStatic("local")
        self.addNonStatic("estranged")
        self.addNonStatic("rgmanager")
        self.addNonStatic("rgmanager_master")
        self.addNonStatic("qdisk")

    def query(self, param, *params, **keys):
        if self.non_statics.get(param, None) != None and self.helper:
            return self.helper.queryStatusElement(query=xpathjoin(self.xpath_clustat, self.element_nodes, self.element_node+'['+self.attribute_node_name+'="'+self.getName()+'"]', self.non_statics.get(param)))
        elif self.helper:
            return self.helper.queryStatusElement(query=os.path.join(self.clustat_pathroot %self.getName(), "@"+param))
        else:
            return None

    def getName(self):
        """
        @return: nodename
        @rtype: string
        """
        return self.getAttribute(RedHatClusterRepository.attribute_clusternode_name)

    def getId(self):
        """
        @return: nodeid
        @rtype: int
        """
        return self.getAttribute(RedHatClusterRepository.attribute_clusternode_nodeid, "")

    def getVotes(self):
        """
        @return: votes for quorum
        @rtype: int
        """
        return self.getAttribute(RedHatClusterRepository.attribute_clusternode_votes, "1")
    
    def isActive(self):
        """
        @return: True if clusternode is active
        """
        return self.state==None or self.state=='1'

class ComoonicsClusterNode(RedHatClusterNode):
    """
    Extends the redhat ClusterNode class 
    by adding special queries for this cluster 
    type and Hashmaps to combine clusteridentifiers 
    with the corresponding network interfaces.
    """
    #define default values
    defaultRootFs = "gfs"
    defaultMountopts = ""
    defaultScsiFailover = "driver"
    defaultSyslog = ""
    
    def __init__(self, element, doc=None):
        super(ComoonicsClusterNode, self).__init__(element, doc)
        
        # dictionaries device:nicobject and mac:nicobject
        self.nicMac = {}
        self.nicDev = {}
        self.nicDevList = []

        #_path=comoonics.cluster.netdev_path %("[@name='%s']" %self.getName())
        #_nics = xpath.Evaluate(_path, self.getElement())
        self._elt_com_info=self.getElement().getElementsByTagName(ComoonicsClusterRepository.element_comoonics)[0]
        for _elt_nic in self._elt_com_info.getElementsByTagName(ComoonicsClusterRepository.element_netdev):
            _nic = ComoonicsClusterNodeNic(_elt_nic, doc)
            _mac = _nic.getMac()
            _dev = _nic.getName()

            # Hashmaps to provide an easy interface to search a nic 
            # corresponding to a specific mac or devicename
            self.nicDev[_dev] = _nic
            self.nicMac[_mac] = _nic
            
            # List of Devicename/Nicobject Pairs for Operations which 
            # need the informations in order of the cluster configuration
            self.nicDevList.append([_dev, _nic])
    
    def getIPForNic(self, value):
        """
        Returns the ip for the nic given
        @param value: Mac-Address (e.g. 00:11:22:33:44) or Devicename (e.g. eth0)
        @type value: string
        @return: ip which belongs to the given nic if dhcp the nodename is tried to be resolved and that ip is taken
        @rtype: L{ComoonicsClusterNodeNic}
        """
        _nic=self.getNic(value)
        _ip=""
        if _nic.isDHCP():
            import socket
            _ip=socket.gethostbyname(self.getName())
        elif _nic.hasAttribute("ip"):
            _ip=_nic.getIP()
        return _ip
        
    def getNic(self, value):
        """
        @param value: Mac-Address (e.g. 00:11:22:33:44) or Devicename (e.g. eth0)
        @type value: string
        @return:  instances of network interfaces which belongs to given mac
        @rtype: L{ComoonicsClusterNodeNic}
        """
        import re
        pattern = r"\b([0-9A-F][0-9A-F])\:([0-9A-F][0-9A-F])\:([0-9A-F][0-9A-F])\:([0-9A-F][0-9A-F])\:([0-9A-Z][0-9A-Z])\:([0-9A-Z][0-9A-Z])\b"
        if re.match(pattern, value):
            self.log.debug("get clusternodenic corresponding to given mac: " + value)
            return self.nicMac[value]
        else:
            self.log.debug("get clusternodenic corresponding to given devicename: " + value)
            return self.nicDev[value]

    def _getRootvolumeElement(self):
        _rootvolumeelement=self._elt_com_info.getElementsByTagName(ComoonicsClusterRepository.element_rootvolume)
        return _rootvolumeelement[0]            
    
    def getRootvolume(self):
        """
        @return: device belonging to rootvolume
        @rtype: string
        """
        _element=self._getRootvolumeElement()
        if _element and _element.hasAttribute(ComoonicsClusterRepository.attribute_rootvolume_name):
            return self._getRootvolumeElement().getAttribute(ComoonicsClusterRepository.attribute_rootvolume_name)
        else:
            return ""

    def getRootFs(self):
        """
        @return: type of root filesystem
        @rtype: string
        """
        _element=self._getRootvolumeElement()
        if _element and _element.hasAttribute(ComoonicsClusterRepository.attribute_rootvolume_fstype):
            return _element.getAttribute(ComoonicsClusterRepository.attribute_rootvolume_fstype)
        else:
            return self.defaultRootFs

    def getMountopts(self):
        """
        @return: additional Mountoptions for root filesystem
        @rtype: string
        """
        _element=self._getRootvolumeElement()
        if _element and _element.hasAttribute(ComoonicsClusterRepository.attribute_rootvolume_mountopts):
            return _element.getAttribute(ComoonicsClusterRepository.attribute_rootvolume_mountopts)
        else:
            return self.defaultMountopts
        
    def getSyslog(self):
        """
        @return: name of node where syslog is running
        @rtype: string
        """
        _elements=self._elt_com_info.getElementsByTagName(ComoonicsClusterRepository.element_syslog)
        if _elements and len(_elements)>0 and _elements[0].hasAttribute(ComoonicsClusterRepository.attribute_syslog_name):
            return _elements[0].getAttribute(ComoonicsClusterRepository.attribute_syslog_name)
        else:
            return self.defaultSyslog
    
    def getScsifailover(self):
        """
        @return: behavior in case of scsifailover
        @rtype: string
        """
        _elements=self._elt_com_info.getElementsByTagName(ComoonicsClusterRepository.element_scsi)
        if _elements and len(_elements)>0 and _elements[0].hasAttribute(ComoonicsClusterRepository.attribute_scsi_failover):
            return _elements[0].getAttribute(ComoonicsClusterRepository.attribute_scsi_failover)
        else:
            return self.defaultScsiFailover
        
    def getNics(self):
        """
        @return: instances of corresponding Network interfaces
        @rtype: list
        """
        self.log.debug("get all clusternodenics")
        #return self.nicDev.values()
    
        _tmp = []
        for i in range(len(self.nicDevList)):
            _tmp.append(self.nicDevList[i][1])
        return _tmp
    
    def getIPs(self):
        """
        @return: all resolved ips of the corresponding network interfaces
        @rtype: list of strings which represent ips
        """
        _tmp=[]
        for nic in self.getNics():
            try:
                _ip=self.getIPForNic(nic.getName())
                if _ip and _ip!="":
                    _tmp.append(_ip)
            except:
                pass
        return _tmp

# $Log: ComClusterNode.py,v $
# Revision 1.14  2011-02-03 14:41:36  marc
# - also work with no helper class
#
# Revision 1.13  2010/11/21 21:45:28  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.12  2009/07/22 08:37:09  marc
# Fedora compliant
#
# Revision 1.11  2009/05/27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.10  2008/08/05 18:28:18  marc
# more bugfixes
#
# Revision 1.9  2008/08/05 13:09:23  marc
# - fixed bugs with constants
# - optimized imports
# - added nonstatic attributes
# - added helper class
#
# Revision 1.8  2008/07/08 07:22:31  andrea2
# Use constants from __init__ (xpathes, filenames)
#
# Revision 1.7  2008/06/20 14:58:04  mark
# set default mountopts to "" as this has to be set within the fs-lib.sh
#
# Revision 1.6  2008/06/10 10:14:52  marc
# - added getIPForNic
#
# Revision 1.5  2007/09/19 06:37:37  andrea2
# Fixed Bug BZ #79, adapted source code in dependence on Python Style Guide
#
# Revision 1.4  2007/08/08 08:38:44  andrea2
# Changed getNics() to get also more than one nic without mac-address
#
# Revision 1.3  2007/08/06 12:09:27  andrea2
# Added more Docu, removed ClusterMetainfo
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/03/28 10:59:56  andrea
# inital version
#
