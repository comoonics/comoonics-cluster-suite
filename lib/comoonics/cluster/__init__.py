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

__version__='$Revision: 1.9 $'

__all__=['clusterconf', 'querymapfile', 'clusterdtd', 'RedHatClusterConst', 'OSRClusterConst']

# needed files
try:
    clusterconf=os.environ["CLUSTERCONF"]
except:
    clusterconf = "/etc/cluster/cluster.conf"
try:
    querymapfile=os.environ["QUERYMAPFILE"]
except:
    querymapfile="/etc/comoonics/cluster_query_mappings.txt"

def parseClusterConf(_clusterconf=clusterconf, _validate=False):
    # parse the document and create comclusterinfo object
    file = os.fdopen(os.open(_clusterconf,os.O_RDONLY))
    doc= parseClusterConfFP(file, _clusterconf, _validate)
    file.close()
    return doc

def parseClusterConfFP(_clusterconffp, _clusterconf, _validate=False):
    from comoonics import ComLog
    from xml.dom.ext.reader import Sax2
    reader = Sax2.Reader(validate=_validate)
    try:
        doc = reader.fromStream(_clusterconffp)
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
    from comoonics.cluster.ComClusterRepository import RedHatClusterRepository
    
    logging.basicConfig()
    
    parser.add_option("-d", "--verbose", action="callback", callback=setDebug, help="Quiet, does not show any output")
    parser.add_option("-c", "--clusterconf", dest="clusterconf", default=RedHatClusterRepository.getDefaultClusterConf())
    return parser

###############
# $Log: __init__.py,v $
# Revision 1.9  2009-07-22 13:01:58  marc
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