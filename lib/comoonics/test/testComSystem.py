'''
Created on Jul 14, 2009

@author: marc
'''
import unittest
from comoonics import ComSystem

class Test_ComSystem(unittest.TestCase):
    cmd1='echo "hallo stdout"'
    cmd1_result="hallo stdout\n"
    cmd2='echo "hallo stderr" >&2'
    cmd2_result="hallo stderr\n"

    def testExecLocalOutput(self):
        result=ComSystem.execLocalOutput(self.cmd1, True, "output cmd1 execLocalOutput")
        self.assertEquals(result, self.cmd1_result)
    def testExecLocalStatusOutput(self):
        result=ComSystem.execLocalStatusOutput(self.cmd1, "output cmd1 execLocalStatusOutput")
        self.assertEquals(result[1], self.cmd1_result[:-1])
    def testExecLocalGetResult(self):
        result=ComSystem.execLocalGetResult(self.cmd1, False, "output cmd1 execLocalGetResult")
        self.assertEquals(result[1][0], self.cmd1_result)
    def testExecLocalOutputErr(self):
        result=ComSystem.execLocalOutput(self.cmd2, True, "output cmd2 execLocalOutput")
        self.assertEquals(result, "")
    def testExecLocalStatusOutputErr(self):
        result=ComSystem.execLocalStatusOutput(self.cmd2, "output cmd2 execLocalStatusOutput")
        self.assertEquals(result[1], self.cmd2_result[:-1])
    def testExecLocalGetResultErr(self):
        result=ComSystem.execLocalGetResult(self.cmd2, True, "output cmd2 execLocalGetResult")
        self.assertEquals(result[2][0], self.cmd2_result)
    def testExecMethodErr(self):
        result=ComSystem.execMethod(ComSystem.execLocalGetResult, self.cmd2, True)
        self.assertEquals(result[2][0], self.cmd2_result)
    def testExecLocalStatusOutputFalse(self):
        result=ComSystem.execLocalStatusOutput("/bin/false", "output of /bin/false, execLocalStatusOutput")
        self.assertTrue(result!=0)
    def testExecLocal(self):
        result=ComSystem.execLocal("/bin/false", "output of /bin/false, execLocal")
        self.assertTrue(result!=0)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(Test_ComSystem)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
