"""

Comoonics cluster configuration helper package

Provides helper classes that are clusterdependent and will be used by base package. 
Those should never be used outside the comoonics.cluster package.
"""
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

from HelperNotSupported import HelperNotSupportedError

def getClusterHelper(clusterinfo=None):
    """
    Returns a new instance of a cluster helper class that suits the given Base class:
       ComoonicsClusterInfo, RedHatClusterInfo => RedHetClusterHelper
       * => HelperNotSupportedError
    @return: Instance of the cluster helper class.
    @rtype: L{comoonics.cluster.helper.ClusterHelper}
    """
    from RedHatClusterHelper import RedHatClusterHelper
    from comoonics.cluster.ComClusterInfo import RedHatClusterInfo
    cls=RedHatClusterHelper
    if clusterinfo and not isinstance(clusterinfo, RedHatClusterInfo):
        raise HelperNotSupportedError("Clusterinformation %s does not support the cluster helper concept." %(clusterinfo))
    return cls()
        
    
class ClusterHelper(object):
    """
    The base cluster helper class.
    No implementation content yet. But all cluster helper classes have to be derived from here.
    """
    pass

##########
# $Log: __init__.py,v $
# Revision 1.4  2011-02-03 14:42:17  marc
# raise HelperNotSupported if helper cannot be instanciated.
#