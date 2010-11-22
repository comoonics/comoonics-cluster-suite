'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        import tempfile
        from comoonics.enterprisecopy.ComModification import registerModification
        from comoonics.enterprisecopy.ComCatifModification import CatiffileModification, CatifexecModification  
        registerModification("catiffile", CatiffileModification)
        registerModification("catifexec", CatifexecModification)
        self.__tmpdir=tempfile.mkdtemp()

    def _testXML(self, _xml):
        import comoonics.XmlTools
        from comoonics.ComPath import Path
        from comoonics.enterprisecopy import ComModification
        _doc = comoonics.XmlTools.parseXMLString(_xml)
        _path=Path(_doc.documentElement, _doc)
        _path.mkdir()
        _path.pushd()
        for _modification in _doc.documentElement.getElementsByTagName("modification"):
            try:
                _modification=ComModification.getModification(_modification, _doc)
                _modification.doModification()
            except Exception, e:
                self.assert_("Caught exception %s during Catif modification %s" %(e, _modification))
        _path.popd()
        
    def testCatifExecModification(self):
        self._testXML(
"""
<path name="%s">
   <modification type="catifexec">
      <command name="/usr/bin/pstree"/>
   </modification>
</path>
""" %self.__tmpdir)
    def testCatiffileModification1(self):
        self._testXML(
"""
<path name="%s">
   <modification type="catiffile">
      <file name="/etc/*-release"/>
      <file name="$(/bin/ls -d /var/log/Xorg.*.log /var/log/XFree86.*.log 2>/dev/null)"/>
   </modification>
</path>
""" %self.__tmpdir)
    
    def testCatiffileModification2(self):
        self._testXML(
"""
<path name="%s">
   <modification type="catiffile">
      <file name="/etc/ld.so.conf.d"/>
      <file name="/etc/ld.so.conf.dadf"/>
   </modification>
</path>
""" %self.__tmpdir)
    def testCatiffileModification3(self):
        self._testXML(
"""
<path name="%s">
   <modification type="catiffile" errors="ignore">
      <file name="/etc/rc.d"/>
      <file name="/etc/syslog.conf"/>
   </modification>
   <modification type="catifexec">
      <command name="hostname"/>
   </modification>
   <modification type="catifexec">
      <command name="/bin/bash -c 'echo lspci; echo; lspci; echo; echo lspci -n; echo; lspci -n; echo; echo lspci -nv; echo; lspci -nv; echo; echo lspci -nvv; echo; /sbin/lspci -nvv'" log="lspci"/>
   </modification>
</path>
""" %self.__tmpdir)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()