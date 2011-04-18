'''
Created on Jul 14, 2009

@author: marc
'''
import unittest
from comoonics import XmlTools

xmls = [ """<?xml version='1.0' encoding='UTF-8'?>
<localclone>
  <node name='lilr629'/>
  <destdisks><disk name='/dev/gnbd/singleclone'/></destdisks>
  <kernel version='2.6.9-34.0.1.ELsmp'/>
</localclone>
""",
"""<?xml version='1.0' encoding='UTF-8'?>
<localclone>
  <node name='myname'/>
  <destdisks><disk name='/dev/sda1'/></destdisks>
  <kernel version='2.6.9-34.0.1.ELsmp'/>
</localclone>
""",
"<xyz>abcd</xyz>",
"""<xyz abcd="abs"/>""",
# merge source 1
"""
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
""",
# merge source 2
"""
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
""",
# merge result with only_one
"""<?xml version='1.0' encoding='UTF-8'?>
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
""",
# merge result without onlyone (default)
"""<?xml version='1.0' encoding='UTF-8'?>
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
]
xpaths=[ ("//node/@name", [ "lilr629" ], "myname"), 
         ("/localclone/destdisks/disk/@name", [ "/dev/sda1" ], "mydisk" ) ]
class Test_XmlTools(unittest.TestCase):
    
    def setUp(self):
        self.docs=list()
        for i in range(len(xmls)): 
            if i < len(xpaths):
                self.docs.append([ XmlTools.parseXMLString(xmls[i]), xpaths[i]])
            else:
                self.docs.append([ XmlTools.parseXMLString(xmls[i]) ])

    def test_toPrettyXml(self):
        docstring="""<?xml version="1.0" ?>
\t<x>
\t  <y>
\t    abc
\t  </y>
\t</x>
"""
        doc=XmlTools.parseXMLString(docstring)
        self.assertEquals(docstring.replace("\n", "").replace("\t", "").replace(" ", ""), XmlTools.toPrettyXML(doc).replace("\n", "").replace("\t", "").replace(" ", ""))            

    def test_removePrettyTextNodes(self):
        docstring="""<?xml version="1.0" ?>
<x>
  <y>
  abcdef
  </y>
</x>
"""     
        doc=XmlTools.parseXMLString(docstring)
        XmlTools.removePrettyTextNodes(doc)
        result=XmlTools.toPrettyXML(doc, "  ", "\n")
        self.assertEquals(docstring.replace("\n", "").replace(" ", ""), result.replace("\n", "").replace(" ", ""))        
    
    def test_evaluateXPath(self):
        for doc in self.docs:
            if len(doc) > 1:
                (doc, xpathtest)=doc
                (xpath, expectedresult, dummy) = xpathtest
                result=XmlTools.evaluateXPath(xpath, doc)
                self.assertEquals(result, expectedresult, "Result of xpath %s in document does not equals the expected result: %s != %s" %(xpath, result, expectedresult))
        
    def test_overwrite_attributes_with_xpaths(self):
        for doc in self.docs:
            if len(doc) > 1:
                (doc, xpathtest)=doc
                (xpath, expectedresult, newvalue) = xpathtest
                xml2=XmlTools.overwrite_attributes_with_xpaths(doc.documentElement, { xpath: newvalue })
                buf=XmlTools.toPrettyXML(xml2)
                self.assertEquals(buf.replace("\n", "").replace(" ", "").replace('<?xmlversion="1.0"?>', ""), 
                                  XmlTools.toPrettyXML(doc).replace("\n", "").replace(" ", "").replace('<?xmlversion="1.0"?>', "").replace("lilr629", "myname").replace("/dev/sda1", "mydisk"))

    def test_overwrite_attributes_with_xpaths2(self):
        doc="""<a>
   <b name="hallo"/>
   <b name="hallo2"/>
   <c name="hallo3"/>
   <c name2="hallo4"/>
   <c name="hallo5"/>
</a>
"""
        edoc="""<a>
   <b name="marc"/>
   <b name="marc"/>
   <c name="marc"/>
   <c name2="hallo4"/>
   <c name="marc"/>
</a>
"""
        rdoc=XmlTools.overwrite_attributes_with_xpaths(XmlTools.parseXMLString(doc), {"//b/@name": "marc", "/a/c/@name": "marc"})
        self.failUnlessEqual(XmlTools.toPrettyXML(rdoc).replace("\n", "").replace(" ", "").replace("\t", "").replace('<?xmlversion="1.0"?>', ""), edoc.replace("\n", "").replace(" ", "").replace("\t", ""))   

    def testGetTextFromElement1(self):
        doc=self.docs[2][0]
        self.assertEquals("abcd", XmlTools.getTextFromElement(doc.documentElement))
    def testGetTextFromElement(self):
        doc=self.docs[3][0]
        self.assertEquals(None, XmlTools.getTextFromElement(doc.documentElement))

#    def testMergeTreesWithPK1(self):
#        doc5=self.docs[4][0]xpath
#        doc6=self.docs[5][0]
#        
#        XmlTools.merge_trees_with_pk(doc5.documentElement, doc6.documentElement, doc6, "name", None, True)
#        
#        buf1=XmlTools.toPrettyXML(doc6)
#        result=XmlTools.toPrettyXML(self.docs[6][0])
#        self.assertEquals(buf1.replace("\n", "").replace(" ", ""), result.replace("\n", "").replace(" ", ""), "testMergeTreesWithPK1: expected xml: \n%s, result: \n%s" %(result, buf1))
        
#    def testMergeTreesWithPK2(self):
#        doc5=self.docs[4][0]
#        doc6=self.docs[5][0]
#        
#        XmlTools.merge_trees_with_pk(doc5.documentElement, doc6.documentElement, doc6, "name", None, False)
#        buf1=XmlTools.toPrettyXML(doc6)
#        result=XmlTools.toPrettyXML(self.docs[7][0])
#        self.assertEquals(buf1.replace("\n", "").replace(" ", ""), result.replace("\n", "").replace(" ", ""), "testMergeTreesWithPK2: expected xml: \n%s, result: \n%s" %(result, buf1))#

    def testCloneNode(self):
        for doc in self.docs:
            doc=doc[0]
            buf1=XmlTools.toPrettyXML(doc.documentElement)
            buf2=XmlTools.toPrettyXML(XmlTools.clone_node(doc.documentElement))
            self.assertEquals(buf1, buf2)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(Test_XmlTools)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
