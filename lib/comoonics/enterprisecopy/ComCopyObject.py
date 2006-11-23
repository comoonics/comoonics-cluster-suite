""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""

# here is some internal information
# $Id: ComCopyObject.py,v 1.2 2006-11-23 14:14:45 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComCopyObject.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics.ComJournaled import JournaledObject
from comoonics import ComLog

class UnsupportedCopyObjectException(ComException): pass

#def getCopyObject(element, doc):
#    """ Factory function to create Copy Objects"""
#    __type=element.getAttribute("type")
#    print "getCopyObject(%s)" %(element.tagName)
#    if __type == "filesystem":
#        from ComFilesystemCopyObject import FilesystemCopyObject
#        return FilesystemCopyObject(element, doc)
#    elif __type == "lvm":
#        from ComLVMCopyObject import LVMCopyObject
#        return LVMCopyObject(element, doc)
#    else:
#        raise UnsupportedCopyObjectException("Unsupported CopyObject type %s in element %s" % (__type, element.tagName))
#

class CopyObject(DataObject):
    """ Base Class for all source and destination objects"""
    __logStrLevel__ = "CopyObject"
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        if element.getAttribute("type") == "backup":
            """ resolving metadata if available """
            emetadatas=element.getElementsByTagName("metadata")
            ComLog.getLogger(self.__logStrLevel__).debug("Found %u metadatas" %(len(emetadatas)))
            for emetadata in emetadatas:
                from comoonics.ComMetadata import Metadata
                metadata=Metadata(emetadata)
                newmetadata=metadata.resolve()
#                print "Newchild %s" %(newmetadata)
                element.replaceChild(newmetadata.cloneNode(True, doc), emetadata)

    def prepareAsSource(self):
        pass

    def cleanupSource(self):
        pass

    def cleanupDest(self):
        pass

    def prepareAsDest(self):
        pass


class CopyObjectJournaled(CopyObject, JournaledObject):
    """
    Derives anything from Copyset plus journals all actions.
    Internally CopysetJournaled has a map of undomethods and references to objects that methods should be executed upon.
    If undo is called the journal stack is executed from top to buttom (LIFO) order.
    """
    __logStrLevel__ = "CopysetJournaled"

    def __init__(self, element, doc):
        CopyObject.__init__(self, element, doc)
        JournaledObject.__init__(self)
        self.__journal__=list()
        self.__undomap__=dict()

    def cleanup(self):
        """
        just calls replayJournal
        """
        self.replayJournal()
# $Log: ComCopyObject.py,v $
# Revision 1.2  2006-11-23 14:14:45  marc
# removed factory method
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.3  2006/07/06 11:53:43  mark
# added class CopyObjectJournaled
#
# Revision 1.2  2006/06/29 13:52:49  marc
# added lvm stuff
#
# Revision 1.1  2006/06/28 17:25:16  mark
# initial checkin (stable)
#