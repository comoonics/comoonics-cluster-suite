""" Comoonics Archive copy object module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComArchiveCopyObject.py,v 1.1 2006-11-23 15:30:55 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComArchiveCopyObject.py,v $

from ComCopyObject import CopyObjectJournaled
from comoonics.ComDataObject import DataObject
from ComMetadata import Metadata

class ArchiveCopyObject(CopyObjectJournaled):
    """ Class for all source and destination objects"""
    __logStrLevel__ = "ArchiveCopyObject"

    def __init__(self, element, doc):
        CopyObjectJournaled.__init__(self, element, doc)
        self.vg=None
        self.metadata_element = element.getElementsByTagName(Metadata.TAGNAME)[0]
        self.data_element = element.getElementsByTagName("data")

    def prepareAsSource(self):
        self.vg.activate()

    def cleanupSource(self):
        pass
#        self.vg.deactivate()

    def archiveMetaData(self, source):
        """ Writes the metadata from source to this archive """
        pass

    def archiveData(self, source):
        pass

    def cleanupDest(self):
        self.cleanupSource()

    def prepareAsDest(self):
        pass

    def getVolumeGroup(self):
        return self.vg

#################
# $Log: ComArchiveCopyObject.py,v $
# Revision 1.1  2006-11-23 15:30:55  marc
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