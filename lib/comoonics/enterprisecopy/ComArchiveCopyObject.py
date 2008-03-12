""" Comoonics Archive copy object module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComArchiveCopyObject.py,v 1.7 2008-03-12 09:40:18 marc Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComArchiveCopyObject.py,v $

from xml import xpath

from comoonics import ComLog, ComSystem
from ComCopyObject import CopyObjectJournaled
from comoonics.ComExceptions import ComException
from comoonics.ComDataObject import DataObject
from comoonics.ComMetadataSerializer import MetadataSerializer
from comoonics.ComArchive import Archive

class ArchiveCopyObject(CopyObjectJournaled):
    """ Class for all source and destination objects"""
    __logStrLevel__ = "ArchiveCopyObject"
    log=ComLog.getLogger(__logStrLevel__)

    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        __serializer=self.element.getElementsByTagName("metadata")[0]
        self.serializer=MetadataSerializer(__serializer)


    def prepareAsSource(self):
        self.metadata=self.serializer.resolve()

    def cleanupSource(self):
        pass

    def getMetaData(self):
        ''' returns a list of metadata elements '''
        return self.metadata

    def updateMetaData(self, element):
        ''' updates all meta data information '''
        self.metadata=element

    def getDataArchive(self):
        ''' returns data archive object'''
        try:
            __archive=xpath.Evaluate('data/archive', self.element)[0]
            return Archive(__archive, self.document)
        except Exception:
            raise ComException("no data archiv description found")


    def prepareAsDest(self):
        ''' writes all metadata to archive'''
        self.log.debug("prepareAsDest()")
        ComSystem.execMethod(self.serializer.serialize, self.metadata)

    def cleanupDest(self):
        pass



#################
# $Log: ComArchiveCopyObject.py,v $
# Revision 1.7  2008-03-12 09:40:18  marc
# made it simulation save
#
# Revision 1.6  2007/04/02 11:48:55  marc
# *** empty log message ***
#
# Revision 1.5  2007/03/26 07:51:36  marc
# - added logging
# - moved serializer.serialize to prepareAsDest (if not it is also called by undo)
#
# Revision 1.4  2006/12/08 09:37:27  mark
# some minor fixes
#
# Revision 1.3  2006/11/27 09:47:34  mark
# some fixes
#
# Revision 1.2  2006/11/24 11:12:47  mark
# adapted to new CopyObject
#
# Revision 1.1  2006/11/23 15:30:55  marc
# initial revision
#
# Revision 1.2  2006/11/23 14:16:16  marc
# added logStrLevel
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/29 13:47:39  marc
# initial revision
#