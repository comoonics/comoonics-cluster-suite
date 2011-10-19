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
        from comoonics.cluster import getClusterRepository, getClusterInfo, clusterconf
        ClusterAssistantHelper.__init__(self, query)
        self.error=False
        # create Reader object
        try:
            clusterRepository = getClusterRepository(clusterconf)
            #create comclusterinfo object
            self.clusterInfo = getClusterInfo(clusterRepository)
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
        
        