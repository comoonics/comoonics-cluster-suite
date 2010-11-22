import unittest
import sys
import comoonics.XmlTools

class test_DataObject(unittest.TestCase):    

    def __init__(self, testMethod="runTest"):
        import os.path
        super(test_DataObject, self).__init__(testMethod)


        #parse the document
        print self.__class__.__name__
        self.doc = comoonics.XmlTools.parseXMLFile(os.path.join(os.path.dirname(sys.argv[0]), "example_config.xml"))

        from comoonics.ComDataObject import DataObject
        self.obj=DataObject(self.doc.documentElement, self.doc)

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
        element=comoonics.XmlTools.evaluateXPath(path, self.doc)[0]
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
