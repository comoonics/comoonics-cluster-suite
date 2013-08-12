"""Comoonics data object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComDataObject.py,v 1.15 2010-11-22 12:05:03 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = "$Revision: 1.15 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComDataObject.py,v $


import exceptions
from xml.dom import Node

import ComLog
import XmlTools
from ComExceptions import ComException

class NotImplementedYetException(ComException): pass

class DataObject(object):
   TAGNAME="DataObject"
   __logStrLevel__ = "DataObject"

   # static methods

   # Public methods
   def __init__(self, *params):
      """
      __init__(xmlasstring|node, [doc])
      Creates a new DataObject.
      @param xmlasstring: the xml to be parsed as DataObject as string
      @type xmlasstring: string
      @param node: node as xml.dom.Element to be taken as base element
      @type node: xml.dom.Element
      @param doc: the document to be taken as basedocument for the given element
      @type doc: xml.dom.DocuementElement 
      """
      element=None
      doc=None
      if len(params) >= 1:
         if isinstance(params[0], basestring):
            element=XmlTools.parseXMLFile(params[0])
            element=element.documentElement
         else:
            element=params[0]
      if len(params) == 2:
         doc=params[1]
      if element and element.hasAttribute("refid"):
         __newelement=self.searchReference(element, doc)
         element.parentNode.replaceChild(__newelement, element)
         self.element=__newelement
      else:
         self.element=element
      self.document=doc
      self.properties=None
      if element:
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
      self.document=doc

   def getAttribute(self,name,default=None):
      if (not self.__dict__.has_key('element') or not self.element.hasAttribute(name)) and default!=None:
         return default
      elif not self.__dict__.has_key('element') or not self.element.hasAttribute(name):
         raise exceptions.NameError("No attribute name " + name)
#      elif self.element.hasAttribute(name) and self.element.getAttribute(name)=="":
#         return ""
      return self.element.getAttribute(name)

   def hasAttribute(self, name):
      return self.element.hasAttribute(name)

   def setAttribute(self, name, value):
      if not self.element and not self.element.nodeType == Node.ELEMENT_NODE:
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


   def getAttributeBoolean(self, name, default=None):
      ''' returns the boolean value of an attribute
         True:  "yes"|"true" (case insensitive) | "1"
         False: "no"|"false" (case insensitive)  | "0"
      '''
      if not self.hasAttribute(name):
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

   # Privat Methods

   def searchReference(self, element, doc):
      name="unnamed"
      try:
         if element.hasAttribute("name"):
            name=element.getAttribute("name")
         __xquery='//'
#         __xquery+=element.tagName
         __xquery+="*"
         __xquery+='[@id="'
         __xquery+=element.getAttribute("refid")
         __xquery+='"]'
         # cloneNode to be safe
         __element=XmlTools.evaluateXPath(__xquery, doc)[0]
         ComLog.getLogger("DataObject").debug("found refid " + \
                                     element.getAttribute("refid"))
         __childs=XmlTools.evaluateXPath('./*', element)
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
