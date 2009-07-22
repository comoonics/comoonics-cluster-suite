'''
Created on Jul 14, 2009

@author: marc
'''
import unittest
from xml.dom.ext import PrettyPrint
from xml.dom.minidom import parseString
from comoonics import XmlTools
from StringIO import StringIO

xml1="""<?xml version='1.0' encoding='UTF-8'?>
<localclone>
  <node name='lilr629'/>
  <destdisks><disk name='/dev/gnbd/singleclone'/></destdisks>
  <kernel version='2.6.9-34.0.1.ELsmp'/>
</localclone>
"""
xml2="""<?xml version='1.0' encoding='UTF-8'?>
<localclone>
  <node name='myname'/>
  <destdisks><disk name='/dev/sda1'/></destdisks>
  <kernel version='2.6.9-34.0.1.ELsmp'/>
</localclone>
"""
xml3="<xyz>abcd</xyz>"
xml4="""<xyz abcd="abs"/>"""
xml5="""
    <a>
       <a name="a">
          <aa/>
       </a>
       <b name="a">
          <ba/>
       </b>
       <c name="b">
          <cb/>
       </c>
    </a>
"""
xml6="""
    <a>
       <b name="a">
          <bb/>
       </b>
       <c name="b">
          <ca/>
       </c>
       <d name="a">
         <da/>
       </d>
    </a>
"""
xml7="""
<?xml version='1.0' encoding='UTF-8'?>
<a>
  <b name='a'>
    <bb/>
  </b>
  <c name='b'>
    <ca/>
  </c>
  <d name='a'>
    <da/>
  </d>
</a>
"""
xml8="""
<?xml version='1.0' encoding='UTF-8'?>
<a>
  <b name='a'>
    <bb/>
    <ba/>
  </b>
  <a name='a'>
    <aa/>
  </a>
  <c name='b'>
    <ca/>
    <cb/>
  </c>
  <d name='a'>
    <da/>
  </d>
</a>
"""
doc1=parseString(xml1)

class Test_XmlTools(unittest.TestCase):
    
    xpaths={"node/@name": "myname",
            "/localclone/destdisks/disk/@name": "/dev/sda1"}
    def test_overwrite_element_with_xpaths(self):
        XmlTools.overwrite_element_with_xpaths(doc1.documentElement, self.xpaths)
        buf=StringIO()
        PrettyPrint(doc1, buf)
        self.assertEquals(buf.getvalue().replace("\n", "").replace(" ", ""), xml2.replace("\n", "").replace(" ", ""))

    def testGetTextFromElement1(self):
        doc=parseString(xml3)
        self.assertEquals("abcd", XmlTools.getTextFromElement(doc.documentElement))
    def testGetTextFromElement(self):
        doc=parseString(xml4)
        self.assertEquals(None, XmlTools.getTextFromElement(doc.documentElement))

    def testMergeTreesWithPK1(self):
        doc5=parseString(xml5)
        doc6=parseString(xml6)
        
        XmlTools.merge_trees_with_pk(doc5.documentElement, doc6.documentElement, doc6, "name", None, True)
        
        buf1=StringIO()
        PrettyPrint(doc6, buf1)
        self.assertEquals(buf1.getvalue().replace("\n", "").replace(" ", ""), xml7.replace("\n", "").replace(" ", ""))
        
    def testMergeTreesWithPK2(self):
        doc5=parseString(xml5)
        doc6=parseString(xml6)
        
        XmlTools.merge_trees_with_pk(doc5.documentElement, doc6.documentElement, doc6, "name", None, False)
        buf1=StringIO()
        PrettyPrint(doc6, buf1)
        self.assertEquals(buf1.getvalue().replace("\n", "").replace(" ", ""), xml8.replace("\n", "").replace(" ", ""))

    def testCloneNode(self):
        buf1=StringIO()
        buf2=StringIO()
        PrettyPrint(doc1.documentElement, buf1)
        PrettyPrint(XmlTools.clone_node(doc1.documentElement), buf2)
        self.assertEquals(buf1.getvalue(), buf2.getvalue())

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(Test_XmlTools)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
