"""

Comoonics cluster configuration package

Provides modules to manage and query the cluster configuration. Discovers type 
of used cluster configuration by parsing given cluster configuration.
"""
import os

__version__='$Revision: 1.7 $'

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

###############
# $Log: __init__.py,v $
# Revision 1.7  2009-05-27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
#
# Revision 1.6  2009/02/24 10:16:01  marc
# added helper method to parse clusterconfiguration
#