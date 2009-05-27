"""Comoonics clusterNodeNic object module


Represents network interfaces (e.g. of comoonics 
clusternode instances) as an L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterNodeNic.py,v 1.9 2009-05-27 18:31:59 marc Exp $
#


__version__ = "$Revision: 1.9 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cluster/ComClusterNodeNic.py,v $

from ComClusterInfo import ClusterObject
from ComClusterRepository import ComoonicsClusterRepository
from comoonics import ComLog

class ComoonicsClusterNodeNic(ClusterObject):
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
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_name)
    
    def getMac(self):
        """
        @return: Returns mac-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_mac, "")
        
    def getIP(self):
        """
        @return: Returns ip-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        try:
            self.log.debug("get ip attribute: " + self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip))
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
                        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip)
                except:
                    ComLog.debugTraceLog(self.log)
                    return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip)
            else:
                return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip)
        except NameError:
            return ""
    
    def isDHCP(self):
        """
        @return: True when NIC is configured via DHCP else False
        """
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip)=="dhcp"
    
    def getGateway(self):
        """
        @return: Returns gateway of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_gateway, "")
    
    def getNetmask(self):
        """
        @return: Returns netmask of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_netmask, "")
    
    def getMaster(self):
        """Returns master"""
        #optional attribute, return empty string if not set
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_master, "")
    
    def getSlave(self):
        """Returns slave"""
        #optional attribute, return empty string if not set
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_slave, "")

# $Log: ComClusterNodeNic.py,v $
# Revision 1.9  2009-05-27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.8  2008/08/05 13:09:31  marc
# - fixed bugs with constants
# - optimized imports
# - added nonstatic attributes
# - added helper class
#
# Revision 1.7  2008/07/08 07:25:31  andrea2
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
