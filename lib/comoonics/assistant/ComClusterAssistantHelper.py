"""
Assistant helper for cluster information
"""

# here is some internal information
# $Id: ComClusterAssistantHelper.py,v 1.2 2010-03-08 12:30:48 marc Exp $
#

__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/assistant/ComClusterAssistantHelper.py,v $


from comoonics.assistant.ComAssistantHelper import AssistantHelper
#from comoonics.cluster.ComClusterRepository import *
#from comoonics.cluster.ComClusterInfo import * 
from comoonics import ComLog

__logStrLevel__="comoonics.assistant.ComAssistantHelper"


class ClusterAssistantHelper(AssistantHelper):
    pass

class RedHatClusterAssistantHelper(ClusterAssistantHelper):
    def __init__(self, query):
        from xml.dom.ext.reader import Sax2
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        ClusterAssistantHelper.__init__(self, query)
        self.error=False
        # create Reader object
        try:
            reader = Sax2.Reader()
            _file = open("/etc/cluster/cluster.conf", "r")
            reader = Sax2.Reader()
            doc = reader.fromStream(_file)
            #create comclusterRepository Object
            clusterRepository = ClusterRepository(doc.documentElement, doc)
            #create comclusterinfo object
            self.clusterInfo = ClusterInfo(clusterRepository)
        except Exception, e:
            ComLog.getLogger(__logStrLevel__).error("Error parsing cluster.conf %s" %e)
            ComLog.errorTraceLog()       
            self.error=True

            
    def scan(self):
        if self.error:
            return 
        if self.query == "clustername":
            return self.scan_clustername()
        
    def scan_clustername(self):
        return [ self.clusterInfo.getClusterName() ]
        
        