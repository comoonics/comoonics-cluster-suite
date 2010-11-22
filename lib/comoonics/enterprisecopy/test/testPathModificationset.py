'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):


    def testPathModificationset1(self):
        _xml="""
    <modificationset type="path" name="copy-to-path">
        <path name="/var/log/">
            <modification type="message">
Hello world
            </modification>
            <modification type="message">
Hello world2
            </modification>
        </path>
    </modificationset>
"""
        self.__testPathModificationset(_xml)

    def testPathModificationSet2(self):
        _xml="""
    <modificationset type="path" name="copy-to-path">
        <path name="/tmp/$(date -u +%G%m%d%k%M%S | /usr/bin/tr -d ' ')">
            <modification type="message">
Hello world
            </modification>
        </path>
    </modificationset>
"""
        self.__testPathModificationset(_xml)

    def __testPathModificationset(self, _xml):
        import comoonics.XmlTools
        from comoonics.enterprisecopy.ComPathModificationset import PathModificationset 
        doc=comoonics.XmlTools.parseXMLString(_xml)
        _modset=PathModificationset(doc.documentElement, doc)
        try:
            _modset.doPre()
            _modset.doModifications()
            _modset.doPost()
        except Exception, e:
            self.assert_("Could not execute PathModificationset %s. Error %s" %(_modset, e))

    def setUp(self):
        from comoonics.enterprisecopy.ComModification import registerModification
        from comoonics.enterprisecopy.ComModificationset import registerModificationset
        from comoonics.enterprisecopy.ComMessage import MessageModification
        from comoonics.enterprisecopy.ComPathModificationset import PathModificationset 
        registerModificationset("path", PathModificationset)
        registerModification("message", MessageModification)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()