"""Comoonics clusterNodeNic object module


Represents network interfaces (e.g. of comoonics 
clusternode instances) as an L{DataObject}.

"""


# here is some internal information
# $Id: ComClusterNodeNic.py,v 1.10 2009-07-22 08:37:09 marc Exp $
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


__version__ = "$Revision: 1.10 $"

import comoonics.cluster
from comoonics import ComLog

class ComoonicsClusterNodeNic(comoonics.cluster.ClusterObject):
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
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_name)
    
    def getMac(self):
        """
        @return: Returns mac-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_mac, "")
        
    def getIP(self):
        """
        @return: Returns ip-address of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
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
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_ip)=="dhcp"
    
    def getGateway(self):
        """
        @return: Returns gateway of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_gateway, "")
    
    def getNetmask(self):
        """
        @return: Returns netmask of interface
        @rtype: string
        """
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_netmask, "")
    
    def getMaster(self):
        """Returns master"""
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_master, "")
    
    def getSlave(self):
        """Returns slave"""
        #optional attribute, return empty string if not set
        from ComClusterRepository import ComoonicsClusterRepository
        return self.getAttribute(ComoonicsClusterRepository.attribute_netdev_slave, "")
