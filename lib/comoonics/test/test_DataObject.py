import unittest
import sys
import os
from xml.dom.ext.reader import Sax2
from xml import xpath

class test_DataObject(unittest.TestCase):    

    def __init__(self, testMethod="runTest"):
        super(test_DataObject, self).__init__(testMethod)

        # create Reader object
        reader = Sax2.Reader()

        #parse the document
        file=os.fdopen(os.open("example_config.xml",os.O_RDONLY))
        self.doc = reader.fromStream(file)

        element=xpath.Evaluate('//*[@refid="bootfs"]', self.doc)[0]

        from comoonics.ComDataObject import DataObject
        self.obj=DataObject(element, self.doc)

#    def testToString(self):
#        _str=""
#        result=self.obj.__str__()
#        self.assertEquals(str, result, "str(obj):%s != %s" %(_str, result))

    def testHasAttributeXYZ(self):
        attribute="xyz"
        print "Testing hasAttribute(%s)" %attribute
        if self.obj.hasAttribute(attribute):
            self.assert_("Found Attribute \"%s\"!! Should not happen!!!" %attribute)
        else:
            print "No Attribute \"%s\" available. (OK)" % attribute

    def testHasAttributeID(self):
        attribute="id"
        print "Testing hasAttribute(%s)" %attribute
        if self.obj.hasAttribute(attribute):
            print "Found Attribute \"%s\"!! (OK)" %attribute
        else:
            self.assert_("No Attribute \"%s\"!! Should not happen!!!" %attribute)

    def testGetAttributeXYZWDefault(self):
        attribute="xyz"
        default=""
        print "Testing getAttribute(%s, %s)" %(attribute, default)
        result=self.obj.getAttribute(attribute, default)
        self.assertEquals(result, default, "Attribute %s is not default %s but %s" %(attribute, result, default))

    def testGetAttributeIDDefault(self):
        attribute="id"
        default="bootfs"
        print "Testing getAttribute(%s, %s)" %(attribute, default)
        result=self.obj.getAttribute(attribute, default)
        self.assertEquals(result, default, "Attribute %s is not default %s but %s" %(attribute, result, default))

    def testGetAttributeXYZ(self):
        attribute="xyz"
        print "Testing getAttribute(%s)" %(attribute)
        try:
            result=self.obj.getAttribute(attribute)
            self.assert_("Found value for Attribute \"%s\": %s !!!Should not happen !!!" %(attribute, result))
        except:
            print "Exception %s caught (OK)" %sys.exc_value

    def testBooleanAttribute(self):
        from comoonics.ComDataObject import DataObject
        print "Testing boolean"
        path="//device[@id='rootfs']"
        element=xpath.Evaluate(path, self.doc)[0]
        obj=DataObject(element)
        print "%s.options: %s" %(path, obj.getAttribute("options"))
        result=obj.getAttributeBoolean("options")
        print "%s.optionsAsBoolean: '%s'" %(path, result)
        self.assertTrue(result, "AttributeBoolean(%s) should return True but returned %s" %("options", result))

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_DataObject)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
