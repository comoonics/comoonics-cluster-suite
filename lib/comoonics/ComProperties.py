#!/usr/bin/python
"""
Implementation of properties as DataObject
"""

__version__= "$Revision $"

# $Id: ComProperties.py,v 1.1 2007-01-15 13:58:09 marc Exp $

import warnings
from ComDataObject import DataObject
import ComLog

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
        if len(args)==1:
            super(Property, self).__init__(args[0])
        elif len(args)==3 and type(args[0])==str and type(args[1])==str:
            doc=args[3]
            element=doc.createElement(Property.TAGNAME)
            super(Property, self).__init__(element, doc)
            self.setAttribute(args[0], args[1])
        else:
            super(Property, self).__init__(*args)

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
        self.getProperties()[name]=Property(name, value)

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
            yield property

mylogger=ComLog.getLogger(Properties.__logStrLevel__)

def main():
    test_str="""
<!DOCTYPE properties SYSTEM "file:/opt/atix/comoonics-cs/xml/comoonics-enterprise-copy.dtd">
<properties>
  <property name="testname1" value="testvalue1"/>
  <property name="testname2" value="testvalue2"/>
</properties>
"""
    print "Reading xml.."
    from xml.dom.ext.reader import Sax2
    from xml.dom.ext import PrettyPrint
    reader=Sax2.Reader(validate=1)
    document=reader.fromString(test_str)
    print "OK"
    PrettyPrint(document.documentElement)
    print "Setting properties.."
    properties=Properties(document.documentElement, document)
    print "OK"
    print properties
    property_name="testname2"
    print "Getting property %s: %s" %(property_name, properties[property_name])


if __name__ == '__main__':
    main()
# $Log: ComProperties.py,v $
# Revision 1.1  2007-01-15 13:58:09  marc
# initial revision
#
