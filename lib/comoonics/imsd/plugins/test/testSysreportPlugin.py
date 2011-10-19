'''
Created on 13.04.2011

@author: marc
'''
import unittest
import tempfile
import os.path
import inspect
from comoonics.imsd.plugins.ComSysreportPlugin import SysreportPlugin

class Test(unittest.TestCase):

    def setUp(self):
        self.tmpdir=tempfile.mkdtemp()
        print("tmpdir: %s" %self.tmpdir)
        self.sysreportdir=os.path.dirname(__file__)
        print "sysreportdir: %s, cwd: %s" %(self.sysreportdir, os.path.realpath(os.path.curdir))
        self.plugin=SysreportPlugin(templatedir=self.sysreportdir, tmpdir=self.tmpdir)

    def tearDown(self):
        pass

    def testCommands(self):
        self.assertEqual(['sysreportshowparts', 'sysreport'], self.plugin.getCommands())
        
    def testCommand(self):
        for _cmd in self.plugin.getCommands():
            self.assertFalse(self.plugin.doCommand(_cmd, part=['sysreport-linux-base']))

    def testHelp(self):
        self.assertEqual(inspect.getdoc(self.plugin), self.plugin.help_short())

if __name__ == "__main__":
    import logging
    from comoonics import ComLog
    logging.basicConfig()
    ComLog.getLogger().setLevel(logging.DEBUG)
    unittest.main()