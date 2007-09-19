"""Comoonics node object module


Represents cluster nodes as an L{DataObject}. 
Node instances can be automatically generated 
by a clusterrepository.

"""

# here is some internal information
# $Id: ComClusterNode.py,v 1.5 2007-09-19 06:37:37 andrea2 Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNode.py,v $

import os

from xml import xpath
from xml.dom.ext.reader import Sax2
#from xml.dom.ext import PrettyPrint

from comoonics.cluster.ComClusterNodeNic import ComoonicsClusterNodeNic

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
            xpath.Evaluate("/cluster/clusternodes/clusternode/com_info", args[0])
        except NameError:
            if args[0].getAttribute("name"):
                cls = RedhatClusterNode
            else:
                cls = ClusterNode
        else:
            cls = ComoonicsClusterNode
            
        return object.__new__(cls, *args, **kwds)
    
    def __init__(self, element, doc=None):
        super(ClusterNode, self).__init__(element, doc)
    
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
        super(RedhatClusterNode, self).__init__(element, doc)

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
        super(ComoonicsClusterNode, self).__init__(element, doc)
        
        # dictionaries device:nicobject and mac:nicobject
        self.nicMac = {}
        self.nicDev = {}
        self.nicDevList = []

        _nics = xpath.Evaluate(self.cominfo_path + '/eth', self.getElement())
        for i in range(len(_nics)):
            _nic = ComoonicsClusterNodeNic(_nics[i], self.getElement())
            _mac = _nic.getMac()
            _dev = _nic.getName()

            # Hashmaps to provide an easy interface to search a nic 
            # corresponding to a specific mac or devicename
            self.nicDev[_dev] = _nic
            self.nicMac[_mac] = _nic
            
            # List of Devicename/Nicobject Pairs for Operations which 
            # need the informations in order of the cluster configuration
            self.nicDevList.append([_dev, _nic])
         
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

    def getRootvolume(self):
        """
        @return: device belonging to rootvolume
        @rtype: string
        """
        self.log.debug("get rootvolume attribute: " + self.rootvolume_path + "@name")
        return xpath.Evaluate(self.rootvolume_path + "@name", self.getElement())[0].value          

    def getRootFs(self):
        """
        @return: type of root filesystem
        @rtype: string
        """
        try:
            self.log.debug("get rootfs attribute: " + self.rootvolume_path + "@fstype")
            return xpath.Evaluate(self.rootvolume_path + "@fstype", self.getElement())[0].value
        except IndexError:
            return self.defaultRootFs

    def getMountopts(self):
        """
        @return: additional Mountoptions for root filesystem
        @rtype: string
        """
        try:
            self.log.debug("get mountopts attribute: " + self.rootvolume_path + "@mountopts")
            return xpath.Evaluate(self.rootvolume_path + "@mountopts", self.getElement())[0].value
        except IndexError:
            return self.defaultMountopts
        
    def getSyslog(self):
        """
        @return: name of node where syslog is running
        @rtype: string
        """
        try:
            self.log.debug("get syslog attribute: " + self.cominfo_path + "syslog/@name")
            return xpath.Evaluate(self.cominfo_path + "syslog/@name", self.getElement())[0].value
        except IndexError:
            return self.defaultSyslog
    
    def getScsifailover(self):
        """
        @return: behavior in case of scsifailover
        @rtype: string
        """
        try:
            self.log.debug("get scsifailover attribute: " + self.cominfo_path + "scsi/@failover")
            return xpath.Evaluate(self.cominfo_path + "scsi/@failover", self.getElement())[0].value
        except IndexError:
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
        
def main():
    """
    Method to test module. Creates a ClusterNode object and test all defined methods 
    on an cluster.conf example (use a loop to proceed every node).
    """
    clusternode_path = "/cluster/clusternodes/clusternode"
    # can use only cluster2.conf for test, cluster.conf MUST cause an not 
    # handled exception (because lack of a device name)
    cluster_conf = "test/cluster2.conf"
    
    # create Reader object
    reader = Sax2.Reader()

    # parse the document
    my_file = os.fdopen(os.open(cluster_conf, os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()

    nodes = xpath.Evaluate(clusternode_path, doc)

    for element in nodes:
        #create example comnode
        obj = ClusterNode(element, doc)

        #test functions
        print "Name: obj.getName(): " + obj.getName() + " - ID: " + obj.getId()
    
        #print "\tobj.getVotes(): " + obj.getVotes()
    
        nics = obj.getNics()
        print "\tobj.getNics(): " + str(nics)
        
        for nic in nics:
            print nic.getName()
            try:
                mac = nic.getMac()
                print "\tobj.getNic('" + mac + "'): " + str(obj.getNic(mac))
            except KeyError:
                print "Verify if nic " + obj.getName() + " really has got no mac-address."
            
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
# Revision 1.5  2007-09-19 06:37:37  andrea2
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
