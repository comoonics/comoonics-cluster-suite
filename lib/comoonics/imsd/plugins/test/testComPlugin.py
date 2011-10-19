import unittest
import inspect
from comoonics.imsd.plugins import ComPlugin

class testDummyPlugin(unittest.TestCase):
    """
    Unittests for the imsd dummy plugins
    """
    def setUp(self):
        self.plugin=ComPlugin.DummyPlugin()
        
    def testCommands(self):
        self.assertEqual(["dummy2", "dummy"], self.plugin.getCommands())
        
    def testCommand(self):
        for _cmd in self.plugin.getCommands():
            self.assertFalse(self.plugin.doCommand(_cmd))

    def testHelp(self):
        self.assertEqual(inspect.getdoc(self.plugin), self.plugin.help_short())

if __name__ == "__main__":
    import logging
    from comoonics import ComLog
    logging.basicConfig()
    ComLog.getLogger().setLevel(logging.DEBUG)
    unittest.main()