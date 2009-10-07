#!/usr/bin/python
import unittest
import os
import os.path
import sys

print "Called %s" %sys.argv

errors=0
exceptions=list()
_path=os.path.join(os.path.dirname(sys.argv[0]), "lib", sys.argv[1].replace(".", os.sep), "test")
testsuite=unittest.TestSuite()
for _testclass in os.listdir(_path):
    if _testclass.endswith(".py"):
        sys.path.append(_path)
        _module=__import__(os.path.splitext(_testclass)[0])
        if hasattr(_module, "test_main"):
            print "Testing test in %s" %_testclass
            try:
                _module.test_main()
            except Exception, e:
                exceptions.append(e)

#print >>sys.stderr, "Errorcode: %u" %len(exceptions)
sys.exit(len(exceptions))
