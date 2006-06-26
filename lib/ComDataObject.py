"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.2 2006-06-26 14:38:52 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDataObject.py,v $


class DataObject:
    def __init__(self, element):
        self.__dict__['element']=element

    def getElement(self):
        return self.__dict__['element']

    def setElement(self, element):
        self.__dict['element']=element

    def __getattribute__(self,name):
        return self.__getattr__(name)
        
    def __getattr__(self,name):
        return self.__dict__['element'].getAttribute(name)

    def __setattribute__(self, name, value):
        self.__setattr__(name, value)

    def __setattr__(self, name, value):
        self.__dict__['element'].setAttribute(name, value)

# $Log: ComDataObject.py,v $
# Revision 1.2  2006-06-26 14:38:52  marc
# Added generic selectors (getattr, setattr) for any attribute in element
#
# Revision 1.1  2006/06/23 14:08:56  mark
# inital checkin (stable)
#
