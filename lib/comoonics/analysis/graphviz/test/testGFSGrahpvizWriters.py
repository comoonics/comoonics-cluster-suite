"""
Testcases for ComGLockWriters
"""
from comoonics.analysis.ComGLockParser import GLockParser
from comoonics.analysis.graphviz.ComGraphvizWriters import GraphvizGLockWriter
import unittest

def createGraphs():
    _locks=dict()
    for _file in testComGraphvizWriters.output.keys():
        print "File: %s" %_file
        _parser=GLockParser(open(_file))
        _writer=GraphvizGLockWriter()
        _name=_writer.NAME
        print "Writer: %s" %_name
        _writer.out="%s.svg" %_file
        _writer.writeBegin()
        _locks=_parser.items()
        for _lock in _locks:
            _writer.write(_lock)
        _writer.writeEnd()
#        print _buf.getvalue()

if __name__ == '__main__':
    class testComGraphvizWriters(unittest.TestCase):
        output={"lockdump-multiholder.out": { "graphviz": """ """},
        "lockdump-multiwaiter.out": { "graphviz": """ """},
        "lockdump-inode.out": { "graphviz": """ """}}
        def testGraphvizGLockWriter(self):
            import StringIO
            _locks=dict()
            for _file in self.output.keys():
                print "File: %s" %_file
                _parser=GLockParser(open(_file))
                _locks[_file]=_parser.items()
            _writer=GraphvizGLockWriter()
            _name=_writer.NAME
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

    import sys
    if sys.argv[1]=="--create" or sys.argv[1]=="-c":
        print "Creating graphs."
        createGraphs()
    else:
        unittest.main()

#############################
# $Log: testGFSGrahpvizWriters.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#            