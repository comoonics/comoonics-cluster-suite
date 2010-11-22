'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        from comoonics.enterprisecopy.ComMessage import MessageModification, MessageRequirement
        from comoonics.enterprisecopy.ComModification import registerModification
        from comoonics.enterprisecopy.ComRequirement import registerRequirement
        registerModification("message", MessageModification)
        registerRequirement("message", MessageRequirement)

    def testMessageRequirement1(self):
        _xml="""
           <requirement type="message" message="hello world"/>
           """
        self._testMessageRequirement(_xml)
        
    def testMessageRequirement2(self):
        _xml="""
           <requirement type="message">
           <text>hello world
           my dear lad</text>
           </requirement>
           """
        self._testMessageRequirement(_xml)

    def testMessageModification1(self):
        _xml="""
           <modification type="message" message="hello world"/>
           """
        self._testMessageModification(_xml)
        
    def testMessageModification2(self):
        _xml="""
           <modification type="message">
           <text>hello world</text>
           <text>my dear lad</text>
           </modification>
           """
        self._testMessageModification(_xml)

    def _testMessageRequirement(self, _xml):
        from comoonics.enterprisecopy.ComRequirement import getRequirement
        import comoonics.XmlTools
        doc=comoonics.XmlTools.parseXMLString(_xml)
        _req=getRequirement(doc.documentElement, doc)
        try:
            _req.do()
        except Exception, e:
            self.assert_("Could not execute requirement %s. Exception %s" %(_req, e))

    def _testMessageModification(self, _xml):
        from comoonics.enterprisecopy.ComModification import getModification
        import comoonics.XmlTools
        doc=comoonics.XmlTools.parseXMLString(_xml)
        _mod=getModification(doc.documentElement, doc)
        try:
            _mod.doModification()
        except Exception, e:
            self.assert_("Could not execute modification %s. Exception %s" %(_mod, e))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()