#!/usr/bin/python
"""
Implementation of properties as DataObject
"""

__version__= "$Revision $"

# $Id: ComProperties.py,v 1.2 2007-02-09 11:34:54 marc Exp $

import warnings
from comoonics.ComDataObject import DataObject
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
        if len(args)==2 and type(args[0])==str and not type(args[1])==str:
            doc=args[1]
            element=doc.createElement(Property.TAGNAME)
            super(Property, self).__init__(element, doc)
            self.setAttribute(args[0], True)
        elif len(args)==3 and isinstance(args[0], basestring) and isinstance(args[1], basestring):
            doc=args[2]
            element=doc.createElement(Property.TAGNAME)
            super(Property, self).__init__(element, doc)
            self.setAttribute("name", args[0])
            self.setAttribute("value", args[1])
        else:
            #mylogger.debug("%s, %s" %(type(args[0]), type(args[1])))
            super(Property, self).__init__(*args)
        if self.hasAttribute("name") and not self.hasAttribute("value"):
            self.setAttribute("value", True)

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

mylogger=ComLog.getLogger(Properties.__logStrLevel__)

def main():
    test_str="""
<!DOCTYPE properties SYSTEM "file:/opt/atix/comoonics-cs/xml/comoonics-enterprise-copy.dtd">
<properties>
  <property name="testname1" value="testvalue1"/>
  <property name="testname2" value="testvalue2"/>
  <property name="testflag"/>
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
    print "Getting property %s: %s" %(property_name, properties[property_name].getAttribute("value"))
    property_name="testflag"
    print "Getting property %s: %s" %(property_name, properties[property_name].getAttribute("value"))
    print "Walking through properties"
    for property in properties.iter():
        print "%s" %(property)


if __name__ == '__main__':
    main()
# $Log: ComProperties.py,v $
# Revision 1.2  2007-02-09 11:34:54  marc
# bugfixes with empty params and different constructors
#
# Revision 1.1  2007/01/15 13:58:09  marc
# initial revision
#
