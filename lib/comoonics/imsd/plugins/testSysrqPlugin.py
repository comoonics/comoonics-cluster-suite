'''
Created on 13.04.2011

@author: marc
'''
import unittest
import tempfile
import os.path
import inspect
from comoonics.imsd.plugins.ComSysrqPlugin import SysrqPlugin

class Test(unittest.TestCase):

    def setUp(self):
        self.tmpdir=tempfile.mkdtemp()
        print("tmpdir: %s" %self.tmpdir)
        self.sysreportdir=os.path.dirname(__file__)
        print "sysreportdir: %s, cwd: %s" %(self.sysreportdir, os.path.realpath(os.path.curdir))
        self.plugin=SysrqPlugin()

    def tearDown(self):
        pass

    def testCommands(self):
        self.assertEqual(['sak', 'voyager', 'oom_kill', 'tasks', 'help', 'xmon', 'sync', 'reboot', 'locks', 'shutoff', 'kill', 'blocked', 'rebootf', 'niceable', 'kbd_xlate', 'readonly', 'memory', 'log6', 'log7', 'log4', 'log5', 'log2', 'log3', 'log0', 'log1', 'regs', 'log8', 'log9', 'kgdb', 'timers', 'sigterm'], self.plugin.getCommands())
        
    def testCommand(self):
        for _cmd in self.plugin.getCommands():
            self.failUnlessRaises(IOError, self.plugin.doCommand, _cmd)

    def testHelp(self):
        self.assertEqual(inspect.getdoc(self.plugin), self.plugin.help_short())

if __name__ == "__main__":
    import logging
    from comoonics import ComLog
    logging.basicConfig()
    ComLog.getLogger().setLevel(logging.DEBUG)
    unittest.main()