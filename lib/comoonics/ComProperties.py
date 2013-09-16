"""
Implementation of properties as DataObject
"""

__version__= "$Revision $"

# $Id: ComProperties.py,v 1.10 2010-11-22 12:25:51 marc Exp $
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

from comoonics.ComDataObject import DataObject
import ComLog
from xml.dom import Node

class Property(DataObject):
   TAGNAME="property"
   ATTRIBUTE_NAME="name"
   ATTRIBUTE_TYPE="type"
   ATTRIBUTE_VALUE="value"
   __logStrLevel__ = "ComProperties"
   logger=ComLog.getLogger("ComProperty")

   '''
   static methods
   '''
   @staticmethod
   def createElement():
      import xml.dom
      impl=xml.dom.getDOMImplementation()
      doc=impl.createDocument(None, Property.TAGNAME, None)
      element=doc.documentElement
      return (element, doc)

   '''
   Public methods
   '''
   def __init__(self, *args, **kwds):
      if (len(args)==2 or len(args)==3) and isinstance(args[0], basestring) and not isinstance(args[1], basestring):
         doc=args[len(args)-1]
         element=doc.createElement(Property.TAGNAME)
         super(Property, self).__init__(element, doc)
         self.setAttribute(Property.ATTRIBUTE_NAME, args[0])
         self.logger.debug("Setting value %s to True" %(args[0]))
         self.setAttribute(Property.ATTRIBUTE_VALUE, True)
      elif len(args)==3 and isinstance(args[0], basestring) and isinstance(args[1], basestring):
         doc=args[2]
         element=doc.createElement(Property.TAGNAME)
         super(Property, self).__init__(element, doc)
         self.setAttribute(Property.ATTRIBUTE_NAME, args[0])
         self.setAttribute(Property.ATTRIBUTE_VALUE, args[1])
      elif kwds:
         (doc, element)=Property.createElement()
         super(Property, self).__init__(element, doc)
         self.setAttribute(Property.ATTRIBUTE_NAME, kwds["name"])
         self.setAttribute(Property.ATTRIBUTE_VALUE, kwds["value"])
      else:
#         self.logger.debug("%s, %s" %(type(args[0]), type(args[1])))
         super(Property, self).__init__(*args)
      if self.hasAttribute(Property.ATTRIBUTE_NAME) and not self.hasAttribute(Property.ATTRIBUTE_VALUE) and len(self.getElement().childNodes)==0:
         self.setAttribute(Property.ATTRIBUTE_VALUE, True)

   def __str__(self):
      return "Property:{ %s: %s}" %(self.getAttribute(Property.ATTRIBUTE_NAME), self.getValue())
   
   def getType(self):
      if self.hasAttribute(Property.ATTRIBUTE_TYPE):
         return self.getAttribute(Property.ATTRIBUTE_TYPE, None)
      else:
         return None
   
   def getValue(self):
      if len(self.getElement().childNodes)>0:
         buf=""
         for _child in self.getElement().childNodes:
            if _child.nodeType == Node.TEXT_NODE:
               buf+=_child.nodeValue
      else:
         buf=self.getAttribute(Property.ATTRIBUTE_VALUE)
      buf=buf.strip()
      thetype=self.getType()
      if thetype:
         try:
            buf=thetype(buf)
         except:
            pass
      return buf

class Properties(DataObject):
   TAGNAME="properties"
   logger=ComLog.getLogger("ComProperties")
   
   '''
   static methods
   '''
   @staticmethod
   def createDocument():
      import xml.dom
      impl=xml.dom.getDOMImplementation()
      return impl.createDocument(None, Properties.TAGNAME, None)

   @staticmethod
   def createElement():
      doc=Properties.createDocument()
      element=doc.documentElement
      return (element, doc)

   '''
   Public methods
   '''
   def __init__(self, *args, **kwds):
      if args and len(args)<=2:
         element=args[0]
         if len(args) < 2:
            doc=Properties.createDocument()
         else:
            doc=args[1]
         super(Properties, self).__init__(element, doc)
         self.properties=dict()
         for eproperty in self.getElement().getElementsByTagName(Property.TAGNAME):
            prop=Property(eproperty, self.getDocument())
            self.properties[prop.getAttribute(Property.ATTRIBUTE_NAME)]=prop
      else:
         (element, doc)=Properties.createElement()
         super(Properties, self).__init__(element, doc)
         self.properties=dict()
         if kwds:
            for name, value in kwds.items():
               self.properties[name]=Property(name, value, self.getDocument())

   def getProperties(self):
      return self.properties
   def getProperty(self, name, d=None):
      return self.getProperties().get(name, Property(name, d, self.getDocument()))
   def setProperty(self, name, value):
      self.getProperties()[name]=Property(name, value, self.getDocument())

   def __delitem__(self, name):
      del self.getProperties()[name]

   def __getitem__(self, name):
      return self.getProperty(name)
   def __setitem__(self, name, value):
      self.setProperty(name, value)
   def get(self, name, d=None):
      return self.getProperty(name, d)
   def has_key(self, name):
      return self.properties.has_key(name)
   def iter(self):
      for prop in self.properties:
         yield self.properties.get(prop)
   def items(self):
      return self.properties.items()
   def keys(self):
      return self.properties.keys()
   def values(self):
      return self.properties.values()
   def getAttribute(self, name):
      if self.has_key(name):
#         ComLog.getLogger("Properties").debug("name: %s, value: %s" %(name, self.getProperty(name).getAttribute("value")))
         return self.getProperty(name).getAttribute(Property.ATTRIBUTE_VALUE)
      else:
         raise KeyError(name)
   def list(self, _pairsdelim="\n", _pairdelim="=", ):
      buf=list()
      for _property in self.iter():
         buf.append("%s%s%s" %(_property.getAttribute(Property.ATTRIBUTE_NAME), _pairdelim, _property.getValue()))
      return _pairsdelim.join(buf)
   def __str__(self):
      return "Properties:{"+", ".join( map(lambda prop: str(prop), self.properties.values()))+"}"
