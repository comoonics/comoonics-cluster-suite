'''
Created on 20.04.2011

@author: marc
'''
import unittest
from comoonics.analysis.StraceAnalyser import StraceParser, StraceEntry

class Test(unittest.TestCase):
    def setUp(self):
        self.parser=StraceParser("./strace.out")

    def tearDown(self):
        pass

    def testEntries(self):
        result=[StraceEntry(timespend='0.000170', pid='9351', timebetween='0.000000', call='execve', result='0', params=['"/data/cms/imperia/cgi-bin/site_mydesk.pl"', '["/data/cms/imperia/cgi-bin/site_m"]', '[/* 27 vars */]']),
StraceEntry(timespend='0.000004', pid='9351', timebetween='0.000272', call='brk', result='0x1afed000', params='0'),
StraceEntry(timespend='0.000006', pid='9351', timebetween='0.000036', call='mmap', result='0x2b6272e65000', params=['NULL', '4096', 'PROT_READ|PROT_WRITE', 'MAP_PRIVATE|MAP_ANONYMOUS', '-1', '0']),
StraceEntry(timespend='0.000006', pid='9351', timebetween='0.000061', call='mmap', result='0x2b6272e66000', params=['NULL', '4096', 'PROT_READ|PROT_WRITE', 'MAP_PRIVATE|MAP_ANONYMOUS', '-1', '0']),
StraceEntry(timespend='0.000013', pid='9351', timebetween='0.000035', call='access', result='-1 ENOENT (No such file or directory)', params=['"/etc/ld.so.preload"', 'R_OK']),
StraceEntry(timespend='0.000035', pid='9351', timebetween='0.000065', call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/tls/x86_64/libperl.so"', 'O_RDONLY']),
StraceEntry(timespend='0.000018', pid='9351', timebetween='0.000082', call='stat', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/tls/x86_64"', '0x7fff7e473e90']),
StraceEntry(timespend='0.000017', pid='9351', timebetween='0.000047', call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/tls/libperl.so"', 'O_RDONLY']),
StraceEntry(timespend='0.000017', pid='9351', timebetween='0.000043', call='stat', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/tls"', '0x7fff7e473e90']),
StraceEntry(timespend='0.000017', pid='9351', timebetween='0.000042', call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/x86_64/libperl.so"', 'O_RDONLY']),
StraceEntry(timespend='0.000017', pid='9351', timebetween='0.000042', call='stat', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/x86_64"', '0x7fff7e473e90']),
StraceEntry(timespend='0.000020', pid='9351', timebetween='0.000042', call='open', result='3', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/libperl.so"', 'O_RDONLY']),
StraceEntry(timespend='0.000016', pid='9351', timebetween='0.000044', call='read', result='832', params=['3', '"\\177ELF\\2\\1\\1\\0\\0\\0\\0\\0\\0\\0\\0\\0\\3\\0>\\0\\1\\0\\0\\0\\340\\34\\3A7\\0\\0\\0"...', '832']),
StraceEntry(timespend='0.000006', pid='9351', timebetween='0.000045', call='fstat', result='0', params=['3', '{st_mode=S_IFREG|0755', 'st_size=1262384', '...}']),
StraceEntry(timespend='0.000008', pid='9351', timebetween='0.000041', call='mmap', result='0x3741000000', params=['0x3741000000', '3363648', 'PROT_READ|PROT_EXEC', 'MAP_PRIVATE|MAP_DENYWRITE', '3', '0']),
StraceEntry(timespend='0.000007', pid='9351', timebetween='0.000027', call='mprotect', result='0', params=['0x374112c000', '2093056', 'PROT_NONE']),
StraceEntry(timespend='0.000011', pid='9351', timebetween='0.000025', call='mmap', result='0x374132b000', params=['0x374132b000', '36864', 'PROT_READ|PROT_WRITE', 'MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE', '3', '0x12b000']),
StraceEntry(timespend='0.000007', pid='9351', timebetween='0.000037', call='mmap', result='0x3741334000', params=['0x3741334000', '4928', 'PROT_READ|PROT_WRITE', 'MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS', '-1', '0']),
StraceEntry(timespend='0.000004', pid='9351', timebetween='0.000029', call='close', result='0', params='3'),
StraceEntry(timespend='0.000021', pid='9351', timebetween='0.000027', call='open', result='-1 ENOENT (No such file or directory)', params=['"/usr/lib64/perl5/5.8.8/x86_64-linux-thread-multi/CORE/libresolv.so.2"', 'O_RDONLY']),
]
        entries=list()
        for entry in self.parser:
            entries.append(entry)
        self.assertEquals(result, entries)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()