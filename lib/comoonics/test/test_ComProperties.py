'''
Created on Dec 15, 2009

@author: marc
'''
import unittest
from comoonics.ComProperties import Properties

xml_str="""
<!DOCTYPE properties SYSTEM "file:/opt/atix/comoonics-cs/xml/comoonics-enterprise-copy.dtd">
<properties>
  <property name="testname1">testvalue1</property>
  <property name="testname2" value="testvalue2"/>
  <property name="testflag"/>
</properties>
"""

class test_Properties(unittest.TestCase):
   def __init__(self, testMethod="runTest"):
      from comoonics import XmlTools
      super(test_Properties, self).__init__(testMethod)
      document=XmlTools.parseXMLString(xml_str)
      self.properties=Properties(document.documentElement, document)

   def test_getProperty1(self):
      property_name="testname1"
      result1="testvalue1"
      result2=self.properties[property_name].getValue()
      self.assertEquals(result1, result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_getProperty2(self):
      property_name="testname2"
      result1="testvalue2"
      result2=self.properties[property_name].getValue()
      self.assertEquals(result1, result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_getProperty3(self):
      property_name="testflag"
      result1=""
      result2=self.properties[property_name].getValue()
      self.assertEquals(result1, result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_setProperty4(self):
      property_name="testname3"
      result1="testvalue3"
      self.properties[property_name]=result1
      result2=self.properties[property_name].getValue()
      self.assertEquals(result1, result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_setProperty5(self):
      property_name="testflag2"
      result1=True
      self.properties[property_name]=result1
      result2=self.properties[property_name].getValue()
      self.assertEquals("", result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_setProperty6(self):
      property_name="testname4"
      result1=True
      self.properties[property_name]=result1
      result2=self.properties[property_name].getValue()
      self.assertEquals("", result2, "Property[%s]=%s != %s" %(property_name, result1, result2)) 

   def test_getNonProperty(self):
      property_name="testname5"
      self.assertRaises(KeyError, self.properties.getAttribute, property_name)

   def test_keys(self):
      keys1=["testname1", "testname2", "testflag"]
      keys1.sort()
      keys2=self.properties.keys()
      keys2.sort()
      self.assertEquals(keys1, keys2, "self.properties.keys(): %s, expectedresult: %s" %(keys2, keys1))

   def test_list(self):
      expected_result=["testname1=testvalue1", "testname2=testvalue2", "testflag="]
      expected_result.sort()
      result1=self.properties.list().split("\n")
      result1.sort()
      self.assertEquals(result1, expected_result, "self.properties.list(): %s\nexpectedresult: %s" %(result1, expected_result))

class test_Properties2(test_Properties):
   """
   Test Properties with other constructor
   """
   def __init__(self, testMethod="runTest"):
      super(test_Properties, self).__init__(testMethod)
      self.properties=Properties(testname1="testvalue1", testname2="testvalue2", testflag=True)

def test_main():
   try:
      from test import test_support
      test_support.run_unittest(test_Properties)
      test_support.run_unittest(test_Properties2)
   except ImportError:
      unittest.main()

if __name__ == '__main__':
   test_main()
