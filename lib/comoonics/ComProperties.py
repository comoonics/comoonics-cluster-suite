"""
Implementation of properties as DataObject
"""

__version__= "$Revision $"

# $Id: ComProperties.py,v 1.9 2010-11-21 21:48:19 marc Exp $
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

import warnings
from comoonics.ComDataObject import DataObject
import ComLog
from exceptions import KeyError
from xml.dom import Node

class Property(DataObject):
    TAGNAME="property"
    __logStrLevel__ = "ComProperties"

    '''
    static methods
    '''

    '''
    Public methods
    '''
    def __init__(self, *args):
        if (len(args)==2 or len(args)==3) and isinstance(args[0], basestring) and not isinstance(args[1], basestring):
            doc=args[len(args)-1]
            element=doc.createElement(Property.TAGNAME)
            super(Property, self).__init__(element, doc)
            self.setAttribute("name", args[0])
            mylogger.debug("Setting value %s to True" %(args[0]))
            self.setAttribute("value", True)
        elif len(args)==3 and isinstance(args[0], basestring) and isinstance(args[1], basestring):
            doc=args[2]
            element=doc.createElement(Property.TAGNAME)
            super(Property, self).__init__(element, doc)
            self.setAttribute("name", args[0])
            self.setAttribute("value", args[1])
        else:
#            mylogger.debug("%s, %s" %(type(args[0]), type(args[1])))
            super(Property, self).__init__(*args)
        if self.hasAttribute("name") and not self.hasAttribute("value") and len(self.getElement().childNodes)==0:
            self.setAttribute("value", True)

    def getValue(self):
        if len(self.getElement().childNodes)>0:
            buf=""
            for _child in self.getElement().childNodes:
                if _child.nodeType == Node.TEXT_NODE:
                    buf+=_child.nodeValue
        else:
            buf=self.getAttribute("value")
        buf=buf.strip()
        return buf

class Properties(DataObject):
    TAGNAME="properties"
    __logStrLevel__ = "ComProperties"

    '''
    static methods
    '''

    '''
    Public methods
    '''
    def __init__(self, element, doc=None):
        super(Properties, self).__init__(element, doc)
        self.properties=dict()
        for property in self.getElement().getElementsByTagName(Property.TAGNAME):
            property=Property(property, self.getDocument())
            self.properties[property.getAttribute("name")]=property

    def getProperties(self):
        return self.properties
    def getProperty(self, name, d=None):
        return self.getProperties().get(name, d)
    def setProperty(self, name, value):
        self.getProperties()[name]=Property(name, value, self.getDocument())

    def __delitem__(self, name):
        del self.getProperties()[name]

    def __getitem__(self, name):
        return self.getProperty(name)
    def __setitem__(self, name, value):
        self.setProperty(name, value)
    def get(self, name, d=None):
        self.getProperty(name, d)
    def has_key(self, name):
        return self.properties.has_key(name)
    def iter(self):
        for property in self.properties:
            yield self.properties.get(property)
    def items(self):
        return self.properties.items()
    def keys(self):
        return self.properties.keys()
    def values(self):
        return self.properties.values()
    def getAttribute(self, name):
        if self.has_key(name):
#            ComLog.getLogger("Properties").debug("name: %s, value: %s" %(name, self.getProperty(name).getAttribute("value")))
            return self.getProperty(name).getAttribute("value")
        else:
            raise KeyError(name)
    def list(self, _pairsdelim="\n", _pairdelim="=", ):
        buf=list()
        for _property in self.iter():
            buf.append("%s%s%s" %(_property.getAttribute("name"), _pairdelim, _property.getValue()))
        return _pairsdelim.join(buf)
            
mylogger=ComLog.getLogger(Properties.__logStrLevel__)
# $Log: ComProperties.py,v $
# Revision 1.9  2010-11-21 21:48:19  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.8  2010/02/05 12:23:30  marc
# - added list method
#
# Revision 1.7  2009/07/22 08:37:40  marc
# fedora compliant
#
# Revision 1.6  2008/01/25 13:04:50  marc
# better test with flags
#
# Revision 1.5  2007/06/19 13:10:54  marc
# - changed some tests
#
# Revision 1.4  2007/06/13 09:13:08  marc
# - added Properties.items()
# - added Property.getValue()
# - better Boolean handling
#
# Revision 1.3  2007/03/26 08:35:13  marc
# - better testing
# - added keys()
# - added del
# - raising a KeyError as dict does if accessing nonexistend attributes
#
# Revision 1.2  2007/02/09 11:34:54  marc
# bugfixes with empty params and different constructors
#
# Revision 1.1  2007/01/15 13:58:09  marc
# initial revision
#
