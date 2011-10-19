'''
Created on 20.04.2011

@author: marc
'''
import unittest
from comoonics.analysis.StraceAnalyser import StraceAnalyser, StraceEntry

class Test(unittest.TestCase):
    def setUp(self):
        self.analyser=StraceAnalyser("./strace.out")

    def tearDown(self):
        pass

    def testAvgTimeBetween(self):
        self.assertEquals(float("%1.5f" %self.analyser.avg("timebetween")), 0.00003)

    def testAvgTimeSpend(self):
        self.assertEquals(float("%1.5f" %self.analyser.avg("timespend")), 0.00001)

    def testMinTimeBetween(self):
        print "min(timebetween): %1.7f" %self.analyser.min("timebetween").timebetween
        self.assertEquals(float("%1.7f" %self.analyser.min("timebetween").timebetween), 0)

    def testMinTimeSpend(self):
        print "min(timespend): %1.7f" %self.analyser.min("timespend").timespend
        self.assertEquals(float("%1.7f" %self.analyser.min("timespend").timespend), 0.0000040)

    def testMaxTimeBetween(self):
        print "max(timebetween): %1.7f" %self.analyser.max("timebetween").timebetween
        self.assertEquals(float("%1.7f" %self.analyser.max("timebetween").timebetween), 0.0002720)

    def testMaxTimeSpend(self):
        print "max(timespend): %1.7f" %self.analyser.max("timespend").timespend
        self.assertEquals(float("%1.7f" %self.analyser.max("timespend").timespend), 0.000170)

    def testCountCalls(self):
        self.assertEquals(self.analyser.count(lambda entry: getattr(entry, "call")=="stat"), 3)
        self.assertEquals(self.analyser.count(lambda entry: getattr(entry, "call")=="open"), 5)
        self.assertEquals(self.analyser.count(lambda entry: getattr(entry, "call")=="execve"), 1)

    def testCallTypes(self):
        self.assertEquals(self.analyser.attributevalues("call"), ['execve', 'brk', 'mmap', 'access', 'open', 'stat', 'read', 'fstat', 'mprotect', 'close'])
        
    def testMinHotspots(self):
        result=[StraceEntry(timespend=3.9999999999999998e-06, pid='9351', timebetween=0.000272, call='brk', result='0x1afed000', params='0'), StraceEntry(timespend=3.9999999999999998e-06, pid='9351', timebetween=2.9e-05, call='close', result='0', params='3'), StraceEntry(timespend=6.0000000000000002e-06, pid='9351', timebetween=3.6000000000000001e-05, call='mmap', result='0x2b6272e65000', params=['NULL', '4096', 'PROT_READ|PROT_WRITE', 'MAP_PRIVATE|MAP_ANONYMOUS', '-1', '0'])]
        self.assertEquals(self.analyser.min_hotspots("timespend", 3), result)

    def testMaxHotspots(self):
        result=[StraceEntry(timespend=0.00017000000000000001, pid='9351', timebetween=0.0, call='execve', result='0', params=['"/data/cms/imperia/cgi-bin/site_mydesk.pl"', '["/data/cms/imperia/cgi-bin/site_m"]', '[/* 27 vars */]']), StraceEntry(timespend=3.4999999999999997e-05, pid='9351', timebetween=6.4999999999999994e-05, call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/tls/x86_64/libperl.so"', 'O_RDONLY']), StraceEntry(timespend=2.0999999999999999e-05, pid='9351', timebetween=2.6999999999999999e-05, call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/libresolv.so.2"', 'O_RDONLY'])]
        self.assertEquals(self.analyser.max_hotspots("timespend", 3), result)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()