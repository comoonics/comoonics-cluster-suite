"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.1 2006-06-23 14:08:56 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDataObject.py,v $


class DataObject:
    def __init__(self, element):
        self.element=element

    def getElement(self):
        return self.element

    def setElement(self, element):
        self.element=element


# $Log: ComDataObject.py,v $
# Revision 1.1  2006-06-23 14:08:56  mark
# inital checkin (stable)
#
