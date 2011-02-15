""" Comoonics metadata objects

a metadata object represents a metadata element in a comoonics-enterprisecopy xmlfile. It will be resolved by
the method resolve automatically. That means all known children in the metadata element will be resolved as known.

Until now the only metadata element supports is one with archive children of the following type:
<metadata>
   <archive ../>
   <archive ../>
</metadata>

These are represented by the class ArchiveMetadata.

"""


# here is some internal information
# $Id: ComMetadataSerializer.py,v 1.1 2011-02-15 14:51:50 marc Exp $
#

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ecbase/ComMetadataSerializer.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from xml.dom import Node

class UnsupportedMetadataException(ComException): pass

class MetadataSerializer(DataObject):
    """ The Metadata baseclass """
    __logStrLevel__="MetadataSerializer"
    log=ComLog.getLogger(__logStrLevel__)
    TAG_NAME="metadata"

    def __new__(cls, *args, **kwds):
        if len (args) > 0 and isinstance(args[0], Node):
            archives=args[0].getElementsByTagName("archive")
            if len(archives) > 0:
                cls=ArchiveMetadataSerializer
                ComLog.getLogger(MetadataSerializer.__logStrLevel__).debug("Returning new object %s" %(cls))
                return object.__new__(cls, *args, **kwds)
            else:
                raise UnsupportedMetadataException("Unsupported Metadata type in element " % (args[0].tagName))
        else:
            raise UnsupportedMetadataException("Unsupported Metadata type because no domelement given (%u)" %(len(args)))

    def __init__(self, element, doc=None):
        DataObject.__init__(self, element, doc)

    """ resolves this metadata object. This is an abstract method and has to be implemented by the childrenclasses """
    def resolve(self):
        return None

    """ Serializes the given element into this MetadataObject """
    def serialize(self, element):
        pass


class ArchiveMetadataSerializer(MetadataSerializer):
    """ The Archive Metadata baseclass """
    __logStrLevel__="ArchiveMetadata"
    def __init__(self, element, doc=None):
        MetadataSerializer.__init__(self, element, doc)
        ComLog.getLogger(ArchiveMetadataSerializer.__logStrLevel__).debug("ArchiveMetadata constructor")

    def resolve(self):
#        print "ArchiveMetadata.resolve"
        from comoonics.storage.ComArchive import Archive
        earchive=self.getElement().getElementsByTagName("archive")[0]
        archive=Archive(earchive, self.getDocument())
#        print "Created archive: %s" %(archive)
        element=archive.getNextDOMElement()
        ComLog.getLogger(self.__logStrLevel__).debug("Found element %s" %(element.tagName))
        return element

    def serialize(self, element):
        from comoonics.storage.ComArchive import Archive
        earchive=self.getElement().getElementsByTagName("archive")[0]
        archive=Archive(earchive, self.getDocument())
#        print "Created archive: %s" %(archive)
        ComLog.getLogger(self.__logStrLevel__).debug("Saving element %s to archive" %(element))
        archive.addNextDOMElement(element)
        ComLog.getLogger(self.__logStrLevel__).debug("Saved element %s to archive element" %(element.tagName))

# $Log: ComMetadataSerializer.py,v $
# Revision 1.1  2011-02-15 14:51:50  marc
# initial revision
#
# Revision 1.5  2010/02/09 21:49:13  mark
# added .storage path in includes
#
# Revision 1.4  2007/04/02 11:47:38  marc
# MMG Backup Legato Integration:
# - resolve returns None instead of pass
#
# Revision 1.3  2007/03/26 08:34:01  marc
# - changed logging to new type
# - fixed an unlikely constructor issue
#
# Revision 1.2  2006/11/27 12:13:04  marc
# initial revision
#
# Revision 1.1  2006/11/24 14:34:42  marc
# initial revision
#
# Revision 1.2  2006/11/23 15:30:26  marc
# add TAG_NAME
#
# Revision 1.1  2006/11/23 14:18:49  marc
# initial revision
#
