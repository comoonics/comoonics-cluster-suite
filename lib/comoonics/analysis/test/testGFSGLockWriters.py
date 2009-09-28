"""
Testcases for ComGLockWriters
"""
from comoonics.analysis.ComGLockWriters import getLockdumpWriterRegistry
from comoonics.analysis.ComGLockParser import GLockParser
import unittest

if __name__ == '__main__':

    class testComGLockWriters(unittest.TestCase):
        output={"lockdump-multiholder.out": { "__default__": """GLock
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 11182
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 27484
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 2446
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 2883
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 9515
    Holder
        gh_flags = error
        gh_state = 3
        gh_state_name = shared
        nodeid = -1
        owner = 19449
    glock = 2
    glockid = 23
    glocktype = inode
"""},
        "lockdump-multiwaiter.out": { "__default__": """GLock
    Holder
        error = 0
        gh_flags = 5
        gh_flags_name = local_excl
        gh_iflags = 1 6 7
        gh_iflags_name = promote,holder,first
        gh_state = 1
        gh_state_name = exclusive
        nodeid = -1
        owner = 11184
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Waiter
        error = 0
        gh_flags = 3
        gh_flags_name = any
        gh_iflags = 1
        gh_iflags_name = promote
        gh_state = 3
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = 11174
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Waiter
        error = 0
        gh_flags = 3
        gh_flags_name = any
        gh_iflags = 1
        gh_iflags_name = promote
        gh_state = 3
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = 11176
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Inode
        busy = True
    glock = 2
    glockid = 26
    glocktype = inode
"""},
        "lockdump-inode.out": { "__default__": """GLock
    Holder
        error = 0
        gh_flags = 5
        gh_flags_name = local_excl
        gh_iflags = 1 6 7
        gh_iflags_name = promote,holder,first
        gh_state = 1
        gh_state_name = exclusive
        nodeid = -1
        owner = 11184
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Waiter
        error = 0
        gh_flags = 3
        gh_flags_name = any
        gh_iflags = 1
        gh_iflags_name = promote
        gh_state = 3
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = 11174
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Waiter
        error = 0
        gh_flags = 3
        gh_flags_name = any
        gh_iflags = 1
        gh_iflags_name = promote
        gh_state = 3
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = 11176
    Waiter
        gh_state = -1
        gh_state_name = shared
        level = 3
        nodeid = -1
        owner = -1
    Inode
        num = 25
    glock = 2
    glockid = 25
    glocktype = inode
"""}}
        def testGLockWriters(self):
            import StringIO
            _locks=dict()
            for _file in self.output.keys():
                print "File: %s" %_file
                _parser=GLockParser(open(_file))
                _locks[_file]=_parser.items()
            for _name, _writer in getLockdumpWriterRegistry().items():
                print "Writer: %s" %_name
                for _file, _locklist in _locks.items():
                    _buf=StringIO.StringIO()
                    _writer.out=_buf
                    _writer.writeBegin()
                    for _lock in _locklist:
                        _writer.write(_lock)
                    _writer.writeEnd()
                    print _buf.getvalue()
                    self.assertEquals(self.output[_file][_name].replace("\t", "    "), _buf.getvalue().replace("\t", "    "), "Could not match output for file %s and writer %s" %(_file, _name))
    unittest.main()

#############################
# $Log: testGFSGLockWriters.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#            