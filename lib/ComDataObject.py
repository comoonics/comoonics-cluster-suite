"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.14 2006-06-29 08:44:20 marc Exp $
#


__version__ = "$Revision: 1.14 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComDataObject.py,v $

import exceptions
import copy
import string
from xml.dom import Element, Node

class DataObject:
    TAGNAME="DataObject"
    __logStrLevel__ = "DataObject"

    '''
    static methods
    '''
    
    '''
    Public methods
    '''
    def __init__(self, element, doc=None):
        self.element=element
        self.document=doc

    def getElement(self):
        return self.element

    def setElement(self, element):
        self.element=element

    def getDocument(self):
        return self.document

    def setDocument(self, doc):
        self.__dict__['document']=doc

    def getAttribute(self,name):
        if not self.__dict__.has_key('element') or not self.element.hasAttribute(name):
            raise exceptions.NameError("No attribute name " + name)
        return self.element.getAttribute(name)

    def hasAttribute(self, name):
        return self.element.hasAttribute(name)

    def setAttribute(self, name, value):
        if not self.element and not isinstance(Element, self.element):
            raise exceptions.IndexError("Element not defined or wrong instance.")
        self.element.setAttribute(name, str(value))

    def updateAttributes(self, frommap):
        '''
        Updates all attribute from frommap that are not already set
        
        frommap - the NamedNodeMap of attributes that are taken as source
        '''
        for i in range(len(frommap)):
            node=frommap.item(i)
            if not self.hasAttribute(node.nodeName) and node.nodeType == Node.ATTRIBUTE_NODE:
                self.setAttribute(node.cloneNode(True))

    def setAttributes(self, nodemap):
        for i in range(len(nodemap)):
            self.setAttribute(nodemap.item(i).nodeName, nodemap.item(i).nodeValue)

    def __copy__(self):
        class EmptyClass: pass
        obj = EmptyClass()
        obj.__class__ = self.__class__
        obj.__dict__.update(self.__dict__)
        return obj

    def __deepcopy__(self, memo):
        class EmptyClass: pass
        obj = EmptyClass()
        obj.__class__ = self.__class__
        obj.__dict__.update(self.__dict__)
        obj.element=self.element.cloneNode(True)
        obj.document=self.document
        return obj
 
    def __str__(self):
        '''
        Return all attributes of element to string
        '''
        str="Classtype: "+self.__class__.__name__+"\nTransient attributes: "
        for attr in self.__dict__.keys():
            str+="%s = %s, " % (attr, self.__dict__[attr])
        str+="\n"
        str+="Elementname: "+self.getElement().tagName
        str+=", persistent Attributes: "
        for i in range(len(self.getElement().attributes)):
            str+="%s = %s, " % (self.getElement().attributes.item(i).name, self.getElement().attributes.item(i).value)
        return str
        
# $Log: ComDataObject.py,v $
# Revision 1.14  2006-06-29 08:44:20  marc
# added updateAttirbutes and minor changes.
#
# Revision 1.13  2006/06/28 17:24:23  mark
# added setAttribues method
#
# Revision 1.12  2006/06/28 13:40:33  marc
# added str() to any attribute value
#
# Revision 1.11  2006/06/27 16:06:28  marc
# changed functionality. Added get/setAttribute for persistent attributes.
#
# Revision 1.10  2006/06/27 14:18:03  marc
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
