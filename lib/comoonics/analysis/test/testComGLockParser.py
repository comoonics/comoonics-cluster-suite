"""
Testcases for ComGLockParser
"""
from comoonics.analysis.ComGLockParser import GLockParser
import unittest
import os

if __name__ == '__main__':

    class testComGLockParser(unittest.TestCase):
        output={
                "lockdump-multiwaiter.out": """GLock
   glocktype=inode
   glockid=26
   glock=2
   Holder
      gh_flags_name=local_excl
      gh_state_name=exclusive
      gh_state=1
      nodeid=-1
      gh_iflags=1 6 7
      gh_flags=5
      error=0
      owner=11184
      gh_iflags_name=['promote', 'holder', 'first']
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Waiter
      gh_flags_name=any
      level=3
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_iflags=1
      gh_flags=3
      error=0
      owner=11174
      gh_iflags_name=promote
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Waiter
      gh_flags_name=any
      level=3
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_iflags=1
      gh_flags=3
      error=0
      owner=11176
      gh_iflags_name=promote
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Inode
      busy=True
""",
    "lockdump-multiholder.out": """GLock
   glocktype=inode
   glockid=23
   glock=2
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=11182
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=27484
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=2446
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=2883
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=9515
   Holder
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_flags=error
      owner=19449
""",
    "lockdump-inode.out": """GLock
   glocktype=inode
   glockid=25
   glock=2
   Holder
      gh_flags_name=local_excl
      gh_state_name=exclusive
      gh_state=1
      nodeid=-1
      gh_iflags=1 6 7
      gh_flags=5
      error=0
      owner=11184
      gh_iflags_name=['promote', 'holder', 'first']
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Waiter
      gh_flags_name=any
      level=3
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_iflags=1
      gh_flags=3
      error=0
      owner=11174
      gh_iflags_name=promote
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Waiter
      gh_flags_name=any
      level=3
      gh_state_name=shared
      gh_state=3
      nodeid=-1
      gh_iflags=1
      gh_flags=3
      error=0
      owner=11176
      gh_iflags_name=promote
   Waiter
      level=3
      gh_state_name=shared
      gh_state=-1
      nodeid=-1
      owner=-1
   Inode
      num=25
"""}
        def testGLockParser(self):
            for _file in self.output.keys():
                print "File: %s" %_file
                _parser=GLockParser(open(_file))
                for _lock in _parser.items():
                    self.assertEquals(_lock.__str__(), self.output[_file])
                
    unittest.main()