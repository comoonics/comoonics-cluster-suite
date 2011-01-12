'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        import tempfile
        from comoonics.enterprisecopy.ComModification import registerModification
        from comoonics.enterprisecopy.ComCopyModification import CopyModification  
        registerModification("copy", CopyModification)
        self.__tmpdir=tempfile.mkdtemp()

    def _testXML(self, _xml):
        import comoonics.XmlTools
        from comoonics.ComPath import Path
        from comoonics.enterprisecopy import ComModification
        _doc = comoonics.XmlTools.parseXMLString(_xml)
        _path=Path(_doc.documentElement, _doc)
        _path.mkdir()
        _path.pushd(_path.getPath())
        for _modification in _doc.documentElement.getElementsByTagName("modification"):
            try:
                _modification=ComModification.getModification(_modification, _doc)
                _modification.doModification()
            except Exception, e:
                self.assert_("Caught exception %s during Catif modification %s" %(e, _modification))
        _path.popd()
        
    def testCopyModification1(self):
        self._testXML(
"""
<path name="%s">
   <modification type="copy">
      <file sourcefile="/etc/*-release" name="."/>
   </modification>
</path>
""" %self.__tmpdir)

if __name__ == "__main__":
    import logging
    from comoonics import ComLog
    logging.basicConfig()
    ComLog.getLogger().setLevel(logging.DEBUG)
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()