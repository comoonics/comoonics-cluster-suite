'''
Created on Jul 14, 2009

@author: marc
'''
import unittest
from comoonics import ComSystem

class Test_ComSystem(unittest.TestCase):
    cmd1='echo "hallo stdout"; echo "hallo stderr" >&2'
    cmd1_result=[ "hallo stdout\n", [ "hallo stdout\n" ], [ 0, ["hallo stdout\n"] ], [ 0, ["hallo stdout\n"], ["hallo stderr\n"] ], (0, "hallo stdout\nhallo stderr" ) ]
    cmd1_sim_result=[ "output cmd1\n",                           # 0
                      [ "output cmd1\n" ],                       # 1
                      [ 0, ["output cmd1\n"] ],                  # 2
                      [ 0, ["output cmd1\n"],["error cmd1\n"] ], # 3
                      (0, "output cmd1\n" ) ]                    # 4
    cmd1_simout="output cmd1\n"
    cmd1_simerr="error cmd1\n"

    def testExecLocalOutputAsString(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalOutput(self.cmd1, True, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_result[0])
    def testExecLocalOutput(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalOutput(self.cmd1, False, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_result[1])
    def testExecLocalGetResult(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalGetResult(self.cmd1, False, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_result[2])
    def testExecLocalGetResultErr(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalGetResult(self.cmd1, True, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_result[3])
    def testExecLocalStatusOutput(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalStatusOutput(self.cmd1, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_result[4])
    def testExecMethodErr(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execMethod(ComSystem.execLocalGetResult, self.cmd1, True)
        self.assertEquals(result, self.cmd1_result[3])
    def testExecLocalStatusOutputFalse(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocalStatusOutput("/bin/false", "output of /bin/false, execLocalStatusOutput")
        self.assertEquals(result, ( 256, "" ))
    def testExecLocalFalse(self):
        ComSystem.setExecMode(None)
        result=ComSystem.execLocal("/bin/false", "output of /bin/false, execLocal")
        self.assertEquals(result, 256)
    def testExecLocalOutputAsStringSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execLocalOutput(self.cmd1, True, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_sim_result[0])
    def testExecLocalOutputSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execLocalOutput(self.cmd1, False, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_sim_result[1])
    def testExecLocalGetResultSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execLocalGetResult(self.cmd1, False, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_sim_result[2])
    def testExecLocalGetResultErrSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execLocalGetResult(self.cmd1, True, self.cmd1_simout, self.cmd1_simerr)
        self.assertEquals(result, self.cmd1_sim_result[3])
    def testExecLocalStatusOutputSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execLocalStatusOutput(self.cmd1, self.cmd1_simout)
        self.assertEquals(result, self.cmd1_sim_result[4])
    def testExecMethodErrSim(self):
        ComSystem.setExecMode(ComSystem.SIMULATE)
        result=ComSystem.execMethod(ComSystem.execLocalGetResult, self.cmd1, True)
        self.assertEquals(result, True)

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(Test_ComSystem)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
