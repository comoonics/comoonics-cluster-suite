import unittest

from comoonics.sos.xmlreport import XmlReport
import stat

class testXMLReport(unittest.TestCase):
    def testXMLReport(self):
        import os
        import sys
        from StringIO import StringIO
        _stats=os.stat(sys.argv[0])
        _report=XmlReport()
        _report.add_command("/bin/test123", 0, "stdout_test123", "stderr_test123", "/tmp/stdout_test123", "/tmp/stderr_test123", "runtime_test123")
        _report.add_file("/tmp/file", _stats)
        _buf=StringIO()
        _report.serialize_to_file(_buf)
        print _buf

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testXMLReport))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(test_suite())