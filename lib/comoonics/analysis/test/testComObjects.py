"""
Testcases for ComObjects
"""
from comoonics.analysis.ComObjects import GLock, Holder, Waiter, Inode
import unittest
import logging

if __name__ == '__main__':

    class testComObjects(unittest.TestCase):
        output="""GLock
   aspace=26
   glock=2
   incore_le=no
   gl_count=14
   req_bh=no
   gl_flags=5
   object=yes
   ail_bufs=no
   glockid=26
   gl_state=1
   reclaim=no
   lvb_count=0
   req_gh=no
   gl_flags_name=dirty
   new_le=no
   glocktype=inode
   Holder
      gh_flags_name=local_excl
      glock=None
      gh_state_name=exclusive
      gh_state=1
      nodeid=-1
      gh_iflags=1 6 7
      gh_flags=5
      glockid=None
      error=0
      owner=11184
      gh_iflags_name=['promote', 'holder', 'first']
      glocktype=None

"""        
        def testObjects(self):
            _lock=GLock()
            _lock.glock="2"
            _lock.glockid="26"
            _lock.gl_flags="5"
            _lock.gl_count="14"
            _lock.gl_state="1"
            _lock.req_gh ="no"
            _lock.req_bh ="no"
            _lock.lvb_count = "0"
            _lock.object = "yes"
            _lock.new_le = "no"
            _lock.incore_le = "no"
            _lock.reclaim = "no"
            _lock.aspace = "26"
            _lock.ail_bufs = "no"
            _child=self._createHolder()
            _lock.addChild(_child)
            #print _lock
            self.assertEquals(_lock.__str__(), self.output)
        def _createHolder(self):
            _holder=Holder()
            _holder.owner = "11184"
            _holder.gh_state = "1"
            _holder.gh_flags = "5"
            _holder.error = "0"
            _holder.gh_iflags = "1 6 7"
            return _holder
        def _createWaiter(self):
            _waiter=Waiter()
            _waiter.level="3"
            _waiter.owner = "28008"
            _waiter.gh_state = "3"
            _waiter.gh_flags = "3"
            _waiter.error = "0"
            _waiter.gh_iflags = "1"
        def _createInode1(self):
            _inode=Inode()
            _inode.busy=True
            return _inode
        def _createInode2(self):
            _inode=Inode()
            _inode.num = "25/25"
            _inode.type = "1"
            _inode.i_count = "1"
            _inode.i_flags = ""
            _inode.vnode = "no"
            return _inode

    unittest.main()