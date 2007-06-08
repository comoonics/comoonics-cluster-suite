"""Comoonics node object module


Represents cluster nodes as an L{DataObject}. 
Node instances can be automatically generated 
by a clusterrepository.

"""

# here is some internal information
# $Id: ComClusterNode.py,v 1.2 2007-06-08 08:24:47 andrea2 Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNode.py,v $

import os

from xml import xpath
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint

from ComClusterNodeNic import *

from comoonics import ComLog
from comoonics.ComDataObject import DataObject

class ClusterNode(DataObject):
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
            xpath.Evaluate("/cluster/clusternodes/clusternode/com_info",args[0])
        except NameError:
            if args[0].getAttribute("name"):
                cls = RedhatClusterNode
            else:
                cls = ClusterNode
        else:
            cls = ComoonicsClusterNode
            
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, element, doc=None):
        super(ClusterNode,self).__init__(element, doc=None)
    
    def getName(self):
        """placeholder for getName method"""
        pass
    
    def getId(self):
        """placeholder for getId method"""
        pass
                

class RedhatClusterNode(ClusterNode):
    """
    Extends the generall ClusterNode class 
    by adding special queries for this cluster 
    type.
    """
    def __init__(self, element, doc=None):
        super(RedhatClusterNode,self).__init__(element, doc=None)

    def getName(self):
        """
        @return: nodename
        @rtype: string
        """
        self.log.debug("get name attribute: " + self.getAttribute("name"))
        #no try-except construct because name ist an obligatory object
        return self.getAttribute("name")

    def getId(self):
        """
        @return: nodeid
        @rtype: int
        """
        try:
            self.log.debug("get nodeid attribute: " + self.getAttribute("nodeid"))
            return self.getAttribute("nodeid")
        except NameError:
            #if attribute id is not set return empty string (because id is an optional attribute)
            return ""

    def getVotes(self):
        """
        @return: votes for quorum
        @rtype: int
        """
        try:
            self.log.debug("get votes attribute: " + self.getAttribute("votes"))
            return self.getAttribute("votes")
        except NameError:
            #if attribute notes does not exist, use default value 1
            return "1"
    

class ComoonicsClusterNode(RedhatClusterNode):
    """
    Extends the redhat ClusterNode class 
    by adding special queries for this cluster 
    type and Hashmaps to combine clusteridentifiers 
    with the corresponding network interfaces.
    """
    
    #define needed pathes from cluster.conf
    cominfo_path = "com_info/"
    rootvolume_path = cominfo_path + "rootvolume/"
    clusternode_path = "/cluster/clusternodes/clusternode"

    #define default values
    defaultRootFs = "gfs"
    defaultMountopts = "noatime,nodiratime"
    defaultScsiFailover = "driver"
    defaultSyslog = ""
    
    def __init__(self, element, doc=None):
        super(ComoonicsClusterNode,self).__init__(element, doc)
        
        # dictionaries device:nicobject and mac:nicobject
        self.nicDev = {}
        self.nicMac = {}

        _nics = xpath.Evaluate(self.cominfo_path + '/eth', self.getElement())
        for i in range(len(_nics)):
            _nic = ComoonicsClusterNodeNic(_nics[i], self.getElement())
            _dev = _nic.getName()
            _mac = _nic.getMac()

            self.nicDev[_dev] = _nic
            self.nicMac[_mac] = _nic
         
    def getNic(self,value):
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

    def getRootvolume(self):
        """
        @return: device belonging to rootvolume
        @rtype: string
        """
        self.log.debug("get rootvolume attribute: " + self.rootvolume_path + "@name")
        return xpath.Evaluate(self.rootvolume_path + "@name",self.getElement())[0].value          

    def getRootFs(self):
        """
        @return: type of root filesystem
        @rtype: string
        """
        try:
            self.log.debug("get rootfs attribute: " + self.rootvolume_path + "@fstype")
            return xpath.Evaluate(self.rootvolume_path + "@fstype",self.getElement())[0].value
        except IndexError:
            return self.defaultRootFs

    def getMountopts(self):
        """
        @return: additional Mountoptions for root filesystem
        @rtype: string
        """
        try:
            self.log.debug("get mountopts attribute: " + self.rootvolume_path + "@mountopts")
            return xpath.Evaluate(self.rootvolume_path + "@mountopts",self.getElement())[0].value
        except IndexError:
            return self.defaultMountopts
        
    def getSyslog(self):
        """
        @return: name of node where syslog is running
        @rtype: string
        """
        try:
            self.log.debug("get syslog attribute: " + self.cominfo_path + "syslog/@name")
            return xpath.Evaluate(self.cominfo_path + "syslog/@name",self.getElement())[0].value
        except IndexError:
            return self.defaultSyslog
    
    def getScsifailover(self):
        """
        @return: behavior in case of scsifailover
        @rtype: string
        """
        try:
            self.log.debug("get scsifailover attribute: " + self.cominfo_path + "scsi/@failover")
            return xpath.Evaluate(self.cominfo_path + "scsi/@failover",self.getElement())[0].value
        except IndexError:
            return self.defaultScsiFailover
        
    def getNics(self):
        """
        @return: instances of corresponding Network interfaces
        @rtype: list
        """
        self.log.debug("get all clusternodenics")
        return self.nicMac.values()
        
def main():
    clusternode_path = "/cluster/clusternodes/clusternode"
    cluster_conf = "test/cluster2.conf"
    
    # create Reader object
    reader = Sax2.Reader()

    # parse the document
    file = os.fdopen(os.open(cluster_conf,os.O_RDONLY))
    doc = reader.fromStream(file)
    file.close()

    Nodes=xpath.Evaluate(clusternode_path, doc)

    for element in Nodes:
        #create example comnode
        obj=ClusterNode(element, doc)

        #test functions
        print "Name: obj.getName(): " + obj.getName() + " - ID: " + obj.getId()
    
        print "\tobj.getVotes(): " + obj.getVotes()
    
        Nics = obj.getNics()
        print "\tobj.getNics(): " + str(Nics)
        
        for Nic in Nics:
            mac = Nic.getMac()
            print "\tobj.getNic('" + mac + "'): " + str(obj.getNic(mac))
            
        try:
            print "\tobj.getRootvolume(): " + obj.getRootvolume()
        except IndexError:
            print "\tobj.getRootvolume(): Exeption raised, OK"
        print "\tobj.getRootFs(): " + obj.getRootFs()
        print "\tobj.getMountopts(): " + obj.getMountopts()
        print "\tobj.getSyslog(): " + obj.getSyslog()
        print "\tobj.SCSIFailover(): " + obj.getScsifailover()
    
        print "\tobj: " + str(obj)
    
    
if __name__ == '__main__':
    main()

# $Log: ComClusterNode.py,v $
# Revision 1.2  2007-06-08 08:24:47  andrea2
# added Debugging
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/03/28 10:59:56  andrea
# inital version
#
