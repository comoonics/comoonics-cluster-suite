"""Comoonics clusterNodeNic object module


Represents network interfaces (e.g. of comoonics 
clusternode instances) as an L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterNodeNic.py,v 1.7 2008-07-08 07:25:31 andrea2 Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNodeNic.py,v $

import os

from xml import xpath
from xml.dom.ext.reader import Sax2

from comoonics.ComDataObject import DataObject
from comoonics import ComLog

class ComoonicsClusterNodeNic(DataObject):
    """
    Represents network interfaces (e.g. of comoonics 
    clusternode instances) as an L{DataObject}.
    """
    
    log = ComLog.getLogger("comoonics.cluster.ComClusterNodeNic")
    
    def __init__(self, element, doc=None):
        super(ComoonicsClusterNodeNic, self).__init__(element, doc)
              
    def getName(self):
        """
        @return: Returns name of interface
        @rtype: string
        """
        self.log.debug("get devicename attribute: " + self.getAttribute("name"))
        return self.getAttribute("name")
    
    def getMac(self):
        """
        @return: Returns mac-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get mac attribute: " + self.getAttribute("mac"))
            return self.getAttribute("mac")
        except NameError:
            return ""
        
    def getIP(self):
        """
        @return: Returns ip-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get ip attribute: " + self.getAttribute("ip"))
            # special case for dhcp we'll return the given ipaddress
            if self.isDHCP():
                from comoonics import ComSystem
                import re
                try:
                    output=ComSystem.execLocalOutput("PATH=/sbin:/usr/sbin ip addr show %s" %self.getName(), True)
                    _mac=re.search("link/ether (?P<mac>\S+)", output).group("mac")
                    _ip=re.search(".*inet (?P<ip>[0-9.]+)", output).group("ip")
                    if _mac.upper() == self.getMac().upper():
                        return _ip
                    else:
                        return self.getAttribute("ip")
                except:
                    ComLog.debugTraceLog(self.log)
                    return self.getAttribute("ip")
            else:
                return self.getAttribute("ip")
        except NameError:
            return ""
    
    def isDHCP(self):
        """
        @return: True when NIC is configured via DHCP else False
        """
        return self.getAttribute("ip")=="dhcp"
    
    def getGateway(self):
        """
        @return: Returns gateway of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get gateway attribute: " + str(self.getAttribute("gateway")))
            return self.getAttribute("gateway")
        except NameError:
            return ""
    
    def getNetmask(self):
        """
        @return: Returns netmask of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get mask attribute: " + self.getAttribute("mask"))
            return self.getAttribute("mask")
        except NameError:
            return ""
    
    def getMaster(self):
        """Returns master"""
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get master attribute: " + self.getAttribute("master"))
            return self.getAttribute("master")
        except NameError:
            return ""
    
    def getSlave(self):
        """Returns slave"""
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get slave attribute: " + self.getAttribute("slave"))
            return self.getAttribute("slave")
        except NameError:
            return ""

def main():
    """
    Method to test module. Creates a ClusterNodeNic object and test all defined 
    methods on an cluster.conf example (use a loop to proceed every nic of every 
    node).
    """
    import comoonics.cluster
    
    # create Reader object
    reader = Sax2.Reader()

    # parse the document
    my_file = os.fdopen(os.open("test/cluster.conf", os.O_RDONLY))
    doc = reader.fromStream(my_file)
    my_file.close()

    nics = xpath.Evaluate(comoonics.cluster.netdev_path, doc)

    for element in nics:
        # create example comnode
        obj = ComoonicsClusterNodeNic(element, doc)

        try:
            name = obj.getName()
        except NameError:
            name = "no name, raise exception, OK for test"
        
        print "name: " + name + " - mac:" + obj.getMac()
        
        # test functions
        print "\tobj.getName:" + name
        print "\tobj.getMac():" + obj.getMac()
        print "\tobj.getIP():" + obj.getIP()
        print "\tobj.getGateway():" + str(obj.getGateway())
        print "\tobj.getNetmask():" + obj.getNetmask()
        print "\tobj.getMaster():" + obj.getMaster()
        print "\tobj.getSlave():" + obj.getSlave()
        print "\tobj:" + str(obj)

if __name__ == '__main__':
    main()

# $Log: ComClusterNodeNic.py,v $
# Revision 1.7  2008-07-08 07:25:31  andrea2
# Use constants (xpathes, filenames) from __init__
#
# Revision 1.6  2008/06/10 10:15:42  marc
# fixed getIP to work with dhcp and being able to resolve it
#
# Revision 1.5  2008/05/09 12:57:46  marc
# - implemented BUG#218 right ip returning whenever node is configured for dhcp
#
# Revision 1.4  2007/09/19 06:41:47  andrea2
# adapted source code in dependence on Python Style Guide, removed not used imports and statements
#
# Revision 1.3  2007/08/06 12:09:27  andrea2
# Added more Docu, removed ClusterMetainfo
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/10 13:30:56  andrea
# inital version
#
