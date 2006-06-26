"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.4 2006-06-26 19:12:18 marc Exp $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDataObject.py,v $

import exceptions
import copy

class DataObject:
    def __init__(self, element):
        self.__dict__['element']=element

    def getElement(self):
        return self.__dict__['element']

    def setElement(self, element):
        self.__dict__['element']=element

    def __getattribute__(self,name):
        return self.__getattr__(name)
        
    def __getattr__(self,name):
        if not self.__dict__.has_key('element') or not self.__dict__['element'].hasAttribute(name):
            raise exceptions.NameError("No attribute name " + name)
        return self.__dict__['element'].getAttribute(name)

    def __setattribute__(self, name, value):
        self.__setattr__(name, value)

    def __setattr__(self, name, value):
        self.__dict__['element'].setAttribute(name, value)

    def __copy__(self):
        class EmptyClass: pass
        obj = EmptyClass()
        obj.__class__ = self.__class__
        obj.__dict__.update(self.__dict__)
#        obj.items = list(self.items)
        #obj = self.__class__.__new__(self.__class__)
        #obj.__class__ = self.__class__
        obj.__dict__['element']=self.__dict__['element'].cloneNode(True)
        return obj
 
# $Log: ComDataObject.py,v $
# Revision 1.4  2006-06-26 19:12:18  marc
# added copy method
#
# Revision 1.3  2006/06/26 15:11:19  mark
# added attribute check
#
# Revision 1.2  2006/06/26 14:38:52  marc
# Added generic selectors (getattr, setattr) for any attribute in element
#
# Revision 1.1  2006/06/23 14:08:56  mark
# inital checkin (stable)
#
