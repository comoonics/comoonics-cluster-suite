"""

Comoonics cluster configuration package

Provides modules to manage and query the cluster configuration. Discovers type 
of used cluster configuration by parsing given cluster configuration.
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

import os

__version__='$Revision: 1.11 $'

__all__=['clusterconf', 'querymapfile', 'clusterdtd', 'RedHatClusterConst', 'OSRClusterConst']

# needed files
try:
    clusterconf=os.environ["CLUSTERCONF"]
except:
    clusterconf = "/etc/cluster/cluster.conf"
try:
    querymapfile=os.environ["QUERYMAPFILE"]
except:
    querymapfile="/etc/comoonics/querymap.cfg"

def parseClusterConf(_clusterconf=clusterconf, _validate=False):
    if not _clusterconf:
        _clusterconf=clusterconf
    # parse the document and create comclusterinfo object
    file = os.fdopen(os.open(_clusterconf,os.O_RDONLY))
    doc= parseClusterConfFP(file, _clusterconf, _validate)
    file.close()
    return doc

def parseClusterConfFP(_clusterconffp, _clusterconf, _validate=False):
    from comoonics import ComLog
    from comoonics import XmlTools
    try:
        doc = XmlTools.parseXMLFP(_clusterconffp)
    except Exception, arg:
        ComLog.getLogger().critical("Problem while reading clusterconfiguration (%s): %s" %(_clusterconf, str(arg)))
        raise
    return doc

def setDebug(option, opt, value, parser):
    from comoonics import ComLog
    import logging
    ComLog.setLevel(logging.DEBUG)
#    ComLog.getLogger().propagate=1

def commonoptparseroptions(parser):
    """
    Sets the give optparser to the common options needed by all cdsl commands.
    """
    import logging
    from ComClusterRepository import RedHatClusterRepository
    
    logging.basicConfig()
    
    parser.add_option("-v", "--verbose", action="callback", callback=setDebug, help="Be more chatty. Default is to talk only about important things.")
    parser.add_option("-c", "--clusterconf", dest="clusterconf", default=RedHatClusterRepository.getDefaultClusterConf(), 
                      help="Overwrite cluster configurationfile. Default: %default.")
    return parser

def get_defaultsfiles():
    import os.path
    default_dir = "/etc/comoonics"
    home_dir = os.path.join(os.environ['HOME'], ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cluster.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cluster.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CLUSTER_CFG" 

###############
# $Log: __init__.py,v $
# Revision 1.11  2010-11-21 21:45:28  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.10  2010/02/05 12:13:08  marc
# - take default clusterconf if none given
#
# Revision 1.9  2009/07/22 13:01:58  marc
# ported to getopts
#
# Revision 1.8  2009/07/22 08:37:09  marc
# Fedora compliant
#
# Revision 1.7  2009/05/27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.6  2009/02/24 10:16:01  marc
# added helper method to parse clusterconfiguration
#