"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.10 2006-06-27 14:18:03 marc Exp $
#


__version__ = "$Revision: 1.10 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDataObject.py,v $

import exceptions
import copy
from xml.dom import Element

class DataObject:
    TAGNAME="DataObject"
    
    def __init__(self, element, doc=None):
        self.__dict__['element']=element
        self.__dict__['document']=doc

    def getElement(self):
        return self.__dict__['element']

    def setElement(self, element):
        self.__dict__['element']=element

    def getDocument(self):
        return self.__dict__['document']

    def setDocument(self, doc):
        self.__dict__['document']=doc

    def __getattr__(self,name):
        if not self.__dict__.has_key('element') or not self.__dict__['element'].hasAttribute(name):
            raise exceptions.NameError("No attribute name " + name)
        return self.__dict__['element'].getAttribute(name)

    def __setattr__(self, name, value):
        if not self.__dict__['element'] and not isinstance(Element, self.__dict__['element']):
            raise exceptions.IndexError("Element not defined or wrong instance.")
        self.__dict__['element'].setAttribute(name, value)

    def __copy__(self):
        class EmptyClass: pass
        obj = EmptyClass()
        obj.__class__ = self.__class__
        obj.__dict__.update(self.__dict__)
        obj.__dict__['element']=self.__dict__['element'].cloneNode(False)
        obj.__dict__['document']=self.__dict__['document']
        return obj

    def __deepcopy__(self, memo):
        class EmptyClass: pass
        obj = EmptyClass()
        obj.__class__ = self.__class__
        obj.__dict__.update(self.__dict__)
        obj.__dict__['element']=self.__dict__['element'].cloneNode(True)
        obj.__dict__['document']=self.__dict__['document']
        return obj
 
    def __str__(self):
        '''
        Return all attributes of element to string
        '''
        str="Classtype: "+self.__class__+", ElementName: "+self.getElement().tagName
        for i in range(len(self.getElement().attributes)):
            str+="%s = %s, " % (self.getElement().attributes.item(i).name, self.getElement().attributes.item(i).value)
        return str

# $Log: ComDataObject.py,v $
# Revision 1.10  2006-06-27 14:18:03  marc
# added error exception for setattr if element does not exist.
#
# Revision 1.9  2006/06/27 14:08:56  marc
# bugfixes
#
# Revision 1.8  2006/06/27 12:00:13  mark
# added doc attribute
#
# Revision 1.7  2006/06/27 09:42:32  marc
# added __str__ method
#
# Revision 1.6  2006/06/27 09:09:16  mark
# changed __deepcopy__ to fullfill interface requirements
#
# Revision 1.5  2006/06/27 06:50:05  marc
# added deepcopy and changed copy to only "copy" the elements in depth 1
#
# Revision 1.4  2006/06/26 19:12:18  marc
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
