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
# $Id: ComMetadata.py,v 1.2 2006-11-23 15:30:26 marc Exp $
#

__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/Attic/ComMetadata.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException
from comoonics import ComLog
from xml.dom import Element, Node

class UnsupportedMetadataException(ComException): pass

class Metadata(DataObject):
    """ The Metadata baseclass """
    __logStrLevel__="ArchiveMetadata"
    TAG_NAME="metadata"
    def __new__(cls, *args, **kwds):
        if len (args) > 0 and isinstance(args[0], Node):
            archives=args[0].getElementsByTagName("archive")
            if len(archives) > 0:
                cls=ArchiveMetadata
                ComLog.getLogger(Metadata.__logStrLevel__).debug("Returning new object %s" %(cls))
                return object.__new__(cls, args, kwds)
            else:
                raise UnsupportedMetadataException("Unsupported Metadata type in element " % (args[0].tagName))
        else:
            raise UnsupportedMetadataException("Unsupported Metadata type because no domelement given (%u)" %(len(args)))


    def __init__(self, element, doc=None):
        DataObject.__init__(self, element, doc)

    """ resolves this metadata object. This is an abstract method and has to be implemented by the childrenclasses """
    def resolve(self):
        pass


class ArchiveMetadata(Metadata):
    """ The Archive Metadata baseclass """
    __logStrLevel__="ArchiveMetadata"
    def __init__(self, element, doc=None):
        print "ArchiveMetadata constructor"
        Metadata.__init__(self, element, doc)

    def resolve(self):
#        print "ArchiveMetadata.resolve"
        from ComArchive import Archive
        earchive=self.getElement().getElementsByTagName("archive")[0]
        archive=Archive(earchive, self.getDocument())
#        print "Created archive: %s" %(archive)
        element=archive.getNextDOMElement()
        ComLog.getLogger(self.__logStrLevel__).debug("Found element %s" %(element.tagName))
        return element

# $Log: ComMetadata.py,v $
# Revision 1.2  2006-11-23 15:30:26  marc
# add TAG_NAME
#
# Revision 1.1  2006/11/23 14:18:49  marc
# initial revision
#
