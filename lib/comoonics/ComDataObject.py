"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.7 2007-03-26 08:19:16 marc Exp $
#


__version__ = "$Revision: 1.7 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComDataObject.py,v $


import exceptions
import copy
import string
from xml.dom import Element, Node
from xml import xpath
from xml.dom.ext import PrettyPrint

import ComLog
import XmlTools
from ComExceptions import *


class DataObject(object):
    TAGNAME="DataObject"
    __logStrLevel__ = "DataObject"

    '''
    static methods
    '''

    '''
    Public methods
    '''
    def __init__(self, element, doc=None):
        if element.hasAttribute("refid"):
            __newelement=self.searchReference(element, doc)
            element.parentNode.replaceChild(__newelement, element)
            self.element=__newelement
        else:
            self.element=element
        self.document=doc
        self.properties=None
        from comoonics.ComProperties import Properties as Props
        properties=element.getElementsByTagName(Props.TAGNAME)
        if len(properties) > 0:
            self.properties=Props(properties[0], self.document)

    def getProperties(self):
        return self.properties

    def getElement(self):
        return self.element

    def setElement(self, element):
        self.element=element

    def getDocument(self):
        return self.document

    def setDocument(self, doc):
        self.__dict__['document']=doc

    def getAttribute(self,name,default=None):
        if (not self.__dict__.has_key('element') or not self.element.hasAttribute(name)) and default!=None:
            return default
        elif not self.__dict__.has_key('element') or not self.element.hasAttribute(name):
            raise exceptions.NameError("No attribute name " + name)
        elif self.element.hasAttribute(name) and self.element.getAttribute(name)=="":
            return True
        return self.element.getAttribute(name)

    def hasAttribute(self, name):
        return self.element.hasAttribute(name)

    def setAttribute(self, name, value):
        if not self.element and not isinstance(Element, self.element):
            raise exceptions.IndexError("Element not defined or wrong instance.")
        if type(value)==bool:
            self.element.setAttribute(name, "")
        else:
            self.element.setAttribute(name, str(value))

    def updateAttributes(self, frommap):
        '''
        Updates all attribute from frommap that are not already set

        frommap - the NamedNodeMap of attributes that are taken as source
        '''
        for i in range(len(frommap)):
            node=frommap.item(i)
            if not self.hasAttribute(node.nodeName) and node.nodeType == Node.ATTRIBUTE_NODE:
                self.getElement().setAttributeNode(node.cloneNode(True))

    def setAttributes(self, nodemap):
        for i in range(len(nodemap)):
            self.setAttribute(nodemap.item(i).nodeName, nodemap.item(i).nodeValue)


    def getAttributeBoolean(self, name, default=False):
        ''' returns the boolean value of an attribute
            True:  "yes"|"true" (case insensitive) | "1"
            False: "no"|"false" (case insensitive)  | "0"
        '''
        if not self.hasAttribute(self):
            return default
        value=self.getAttribute(name).lower()
        if value == "yes" or value == "true" or value == "1":
            return True
        if value == "no" or value == "false" or value == "0":
            return False
        return default



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

    """
    Privat Methods
    """

    def searchReference(self, element, doc):
        name="unnamed"
        try:
            if element.hasAttribute("name"):
                name=element.getAttribute("name")
            __xquery='//'
#            __xquery+=element.tagName
            __xquery+="*"
            __xquery+='[@id="'
            __xquery+=element.getAttribute("refid")
            __xquery+='"]'
            # cloneNode to be safe
            __element=xpath.Evaluate(__xquery, doc)[0]
            ComLog.getLogger("DataObject").debug("found refid " + \
                                                 element.getAttribute("refid"))
            __childs=xpath.Evaluate('./*', element)
            __new=__element.cloneNode(True)
            self.appendChildren(__new, __childs)
            return __new
        except exceptions.Exception:
            raise ComException("Element "+element.tagName+" with name "+name+" and id " + element.getAttribute("refid") \
                               + " not found. Query: " + __xquery)

    def appendChildren(self, element, nodelist):
        for i in range(len(nodelist)):
            element.appendChild(nodelist[i])

    def appendChild(self, child):
        self.element.appendChild(child.getElement())

    def updateChildrenWithPK(self, dataobject, pk="name"):
        """ add all children from dataobject
        if they are not already there.
        pk is used as primary key.
        Also adds all Attributes from dataobject if the are not present.
        """
        XmlTools.merge_trees_with_pk(dataobject.getElement(), self.element, self.document, pk)

# $Log: ComDataObject.py,v $
# Revision 1.7  2007-03-26 08:19:16  marc
# - added boolean attributes as true ones with attributes without values
#
# Revision 1.6  2007/02/28 10:12:25  mark
# added getAttributeBoolean()
#
# Revision 1.5  2007/02/09 11:28:30  marc
# added optional but general support for properties.
#
# Revision 1.4  2006/12/08 09:44:18  mark
# added support for PartitionCopyobject
#
# Revision 1.3  2006/11/23 14:17:10  marc
# baseclass is now object
#
# Revision 1.2  2006/10/19 10:03:18  marc
# bugfix
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.21  2006/07/05 13:06:20  marc
# added getAttribute with default
#
# Revision 1.20  2006/06/30 08:00:52  mark
# bugfixes in ref
#
# Revision 1.19  2006/06/29 13:49:10  marc
# bugfix in updateAttributes
#
# Revision 1.18  2006/06/29 10:38:11  mark
# bug fixes
#
# Revision 1.17  2006/06/29 10:22:48  mark
# bug fixes
#
# Revision 1.16  2006/06/29 09:27:23  mark
# made constructor more fancy
#
# Revision 1.15  2006/06/29 09:13:23  mark
# added support for reference refid attribute
#
# Revision 1.14  2006/06/29 08:44:20  marc
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
