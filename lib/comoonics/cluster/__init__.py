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
from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException

__version__='$Revision: 1.11 $'

#__all__=['clusterconf', 'querymapfile', 'clusterdtd', 'RedHatClusterConst', 'OSRClusterConst', 
#         'getClusterInfo', 'ClusterMacNotFoundException', 'ClusterInformationNotFound', 'ClusterIdNotFoundException',
#         'getClusterRepository', 'ClusterObject', 'ClusterRepositoryConverterNotFoundException' ]


class ClusterMacNotFoundException(ComException): pass
class ClusterInformationNotFound(ComException): pass
class ClusterIdNotFoundException(ComException): pass
class ClusterNodeNoIdFoundException(ComException): pass
class ClusterRepositoryNoNodesFound(ComException): pass

class ClusterObject(DataObject):
    non_statics=dict()
    def __init__(self, *params, **kwds):
        super(ClusterObject, self).__init__(*params, **kwds)
        self.non_statics=dict()
    def isstatic(self, _property):
        if self.non_statics.has_key(_property):
            return False
        return True
    def addNonStatic(self, name, rest=None):
        path_end=self.non_statics
        path_end[name]=rest
    def query(self, _property, *params, **keys):
        pass
    def __getattr__(self, value):
        if not self.isstatic(value):
            return self.query(value)
        else:
            return DataObject.__getattribute__(self, value)

def getClusterInfo(clusterRepository):
    """
    Factory method to return the fitting instance of the cluster information classes#
    @param clusterRepository: the relevant cluster repository
    @type  clusterRepository: L{comoonics.cluster.ComClusterRepository.ClusterRepository}
    @return:                  the clusterinformation relevant to the clusterRepository
    @rtype:                   L{ClusterRepository} 
    """
    from comoonics.cluster.ComClusterRepository import ClusterRepository
    if isinstance(clusterRepository, ClusterRepository):
        cls = clusterRepository.getClusterInfoClass()
    else:
        raise ClusterInformationNotFound("Could not find cluster information for cluster repository %s." %(clusterRepository))
    return cls(clusterRepository)

class ClusterRepositoryConverterNotFoundException(ComException): pass

def getClusterRepository(*args, **kwds):
    """
    Factory method to autocreate a fitting cluster repository.
    The following call semantics are supported:
    getClusterRepository() => SimpleComoonicsClusterRepository
    getClusterRepository(filename) => ComoonicsClusterRepository
    getClusterRepository(docelement, doc, options) => ComoonicsClusterRepository
    getClusterRepository(filename=filename) => ComoonicsClusterRepository
    getClusterRepository(clusterconf=filename) => ComoonicsClusterRepository
    getClusterRepository(maxnodeid=maxnodeid) => SimpleClusterRepository
    Parses the given filename as configuration to the given cluster or already accept a parsed configuration. 
    Right now only xml.dom.Node representation of the cluster configuration is supported.
    @param filename:   representation of the path to the cluster configuration. If it is a xml file it will be parsed. 
                       If not an exception is thrown.
    @type  filename:   L{String} 
    @param docelement: the already parse configuration as dom document.
    @type  docelement: L{xml.dom.Element}
    @param doc:        the document itself.
    @type  doc:        L{xml.dom.Docuement}
    @param options:    options see ClusterRepository constructor.
    @type  options:    L{dict}
    @return:           The best fitting clusterconfiguration repository class instance
    @rtype:            L{ComoonicsClusterRepository}, L{RedHatClusterRepository}, ..
    """
    from comoonics.XmlTools import evaluateXPath
    from comoonics.DictTools import searchDict
    import ComClusterRepository
#    from comoonics.cluster.ComClusterRepository import SimpleComoonicsClusterRepository, ComoonicsClusterRepository, RedHatClusterRepository
    repositoryclass=ComClusterRepository.SimpleComoonicsClusterRepository
    
    clusterconf=None
    if (args and len(args) >= 1 and isinstance(args[0], basestring)) or (kwds and (kwds.has_key("clusterconf") or kwds.has_key("filename"))):
        if args and len(args) >= 1 and isinstance(args[0], basestring):
            clusterconf=args[0]
        elif kwds.has_key("clusterconf"):
            clusterconf=kwds.get("clusterconf")
            del kwds["clusterconf"]
        elif kwds.has_key("filename"):
            clusterconf=kwds.get("filename")
            del kwds["filename"]
    
    if clusterconf and os.path.isfile(clusterconf):
        doc=parseClusterConf(clusterconf)
        newargs=[doc.documentElement,doc]
        newargs.extend(args[1:])
        args=newargs
        if len(evaluateXPath(ComClusterRepository.ComoonicsClusterRepository.getDefaultComoonicsXPath(), doc.documentElement)) > 0:
            repositoryclass = ComClusterRepository.ComoonicsClusterRepository
        elif len(evaluateXPath(ComClusterRepository.RedHatClusterRepository.getDefaultClusterNodeXPath(), doc.documentElement)) > 0:
            repositoryclass = ComClusterRepository.RedHatClusterRepository
    elif len(args) >= 2 or kwds.has_key("element"):
        if args and args[0]:
            element=args[0]
        else:
            element=kwds.get("element", None)
        if (element != None):
            if args and len(args)>=3:
                options=args[2]
            else:
                options=kwds.get("options", {})       
            if evaluateXPath(ComClusterRepository.ComoonicsClusterRepository.getDefaultComoonicsXPath(""), element) or not options:
                repositoryclass = ComClusterRepository.ComoonicsClusterRepository
            elif evaluateXPath(ComClusterRepository.RedHatClusterRepository.getDefaultClusterNodeXPath(), element):
                repositoryclass = ComClusterRepository.RedHatClusterRepository
                
        elif type(args[2]) == dict:
            if searchDict(args[2],"osr"):
                repositoryclass = ComClusterRepository.ComoonicsClusterRepository
            elif searchDict(args[2],ComClusterRepository.RedHatClusterRepository.element_clusternode):
                repositoryclass = ComClusterRepository.RedHatClusterRepository
            
    return repositoryclass(*args, **kwds) #, *args, **kwds)

def getClusterNode(clusterrepository, element, doc=None):
    """
    Decides by content of given element which 
    instance of clusternode (general, redhat 
    or comoonics) has to be created.
    """
    return clusterrepository.getClusterNodeClass(element, doc)

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
    home_dir = os.path.join(os.environ.get('HOME', ''), ".comoonics")
    globalcfgdefault_file= os.path.join(default_dir, "cluster.cfg") 
    localcfgdefault_file= os.path.join(home_dir, "cluster.cfg")
    return globalcfgdefault_file, localcfgdefault_file

def get_defaultsenvkey():
    return "COMOONICS_CLUSTER_CFG" 

from comoonics.cluster.ComQueryMap import QueryMap

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