import unittest

from comoonics.fenceacksv.plugins import ComPlugin

class testPlugins(unittest.TestCase):
    """
    Unittests for the fenceacksv plugins
    """
    def testDummyPlugin(self):
        _plugin=self._testPlugin(ComPlugin.DummyPlugin)
        self.assertEqual(["dummy2", "dummy"], _plugin.getCommands())
    def _testPlugin(self, _class):
        import inspect
        _plugin=_class()
        self.assertEqual(inspect.getdoc(_plugin), _plugin.help_short())
        for _cmd in _plugin.getCommands():
            self.assertFalse(_plugin.doCommand(_cmd))
        return _plugin

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPlugins))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())
