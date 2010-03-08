""" Comoonics file module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFile.py,v 1.3 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.3 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComFile.py,v $

from comoonics.ComDataObject import DataObject

class File(DataObject):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)
        
# $Log: ComFile.py,v $
# Revision 1.3  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2010/02/09 21:48:51  mark
# added .storage path in includes
#
# Revision 1.1  2009/09/28 15:13:36  marc
# moved from comoonics here
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/30 08:01:25  mark
# initial checkin
#
