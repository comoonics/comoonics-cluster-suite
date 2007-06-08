"""Comoonics clusterMetainfo object module


Represents network interfaces (e.g. of comoonics 
clusternode instances) as an L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterNodeNic.py,v 1.2 2007-06-08 08:24:47 andrea2 Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNodeNic.py,v $

import os

from xml import xpath
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml.dom.ext.reader.Sax2 import implementation

from comoonics.ComDataObject import DataObject
from comoonics import ComLog

class ComoonicsClusterNodeNic(DataObject):
    """
    Represents network interfaces (e.g. of comoonics 
    clusternode instances) as an L{DataObject}.
    """
    
    log = ComLog.getLogger("comoonics.cluster.ComClusterNodeNic")
    
    def __init__(self,element,doc=None):
        super(ComoonicsClusterNodeNic,self).__init__(element,doc)
              
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
            return self.getAttribute("ip")
        except NameError:
            return ""
    
    def getGateway(self):
        """
        @return: Returns gateway of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get gateway attribute: " + self.getAttribute("gateway"))
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
    # create Reader object
    reader = Sax2.Reader()

    # parse the document
    file=os.fdopen(os.open("test/cluster.conf",os.O_RDONLY))
    doc = reader.fromStream(file)
    file.close()

    Nics=xpath.Evaluate("/cluster/clusternodes/clusternode/com_info/eth", doc)

    for element in Nics:
        # create example comnode
        obj=ComoonicsClusterNodeNic(element, doc)

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
# Revision 1.2  2007-06-08 08:24:47  andrea2
# added Debugging
#
# Revision 1.1  2007/06/05 13:11:21  andrea2
# *** empty log message ***
##
# Revision 0.1  2007/05/10 13:30:56  andrea
# inital version
#
