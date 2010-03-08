'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):

    def testSysrqModificationMemory(self):
        __xml="""
   <modification type="sysrq">
      <sysrq command="memory"/>
   </modification>
"""
        self.__testSysrqModification(__xml)

    def testSysrqModificationTasks(self):
        __xml="""
   <modification type="sysrq">
      <sysrq command="memory"/>
      <sysrq command="tasks"/>
   </modification>
"""
        self.__testSysrqModification(__xml)

    def __testSysrqModification(self, _xml):
        from xml.dom.ext.reader import Sax2
        from comoonics.enterprisecopy.ComSysrqModification import SysrqModification
        # create Reader object
        reader = Sax2.Reader()

        _doc = reader.fromString(_xml)
        try:
            _modification=SysrqModification(element=_doc.documentElement, doc=_doc)
            _modification.doModification()
        except Exception, e:
            self.assert_("Exception %s occured during sysrq: %s" %(e, _modification))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()