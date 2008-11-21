import unittest
from optparse import Values
from test import test_support

class testSosReportBase(unittest.TestCase):
    RESULT_FILENAMES=[]
    OPTIONS={}
    def setUp(self):
        from comoonics.sos.sosreport import SosReport
        _options=Values()
        for _key, _value in self.OPTIONS.items():
            setattr(_options, _key, _value)
        self._sosreport=SosReport(_options)
        self._sosreport.checkrootuid=False
        self._sosreport.pluginpaths={"../plugins_test": "comoonics.sos.plugins_test"}
    def testSosReport(self):
        import tarfile
        import os.path
        self._sosreport.main()
        _tarfile=tarfile.open(self._sosreport.policy.report_file)
        for _tarinfo in _tarfile:
            if _tarinfo.isfile():
                self.failUnless(os.path.basename(_tarinfo.name) in self.RESULT_FILENAMES, "%s not in %s" %(os.path.basename(_tarinfo.name), self.RESULT_FILENAMES))

class testSosReport1(testSosReportBase):
    RESULT_FILENAMES=["hosts", "sos_logssos.log", "sosreport.html", "sosreport.xml"]
    OPTIONS={"debug":1, "verbose": 3, "batch": True, "progressbar":False, "nomultithread":True, "plugopts":["null.initd=1"]}

class testSosReport2(testSosReportBase):
    RESULT_FILENAMES=["hosts", "sos_logssos.log", "sosreport.html", "sosreport.xml"]
    OPTIONS={"debug":1, "verbose": 3, "batch": True, "progressbar":False, "nomultithread":False, "plugopts":["null.initd=1"]}

class testSosReport3(testSosReportBase):
    RESULT_FILENAMES=["hosts", "sos_logssos.log", "sosreport.html", "sosreport.xml"]
    OPTIONS={"debug":1, "verbose": 3, "batch": True, "progressbar":False, "nomultithread":False, "onlyplugins": ["null"]}

class testSosReport4(testSosReportBase):
    RESULT_FILENAMES=["hosts", "sos_logssos.log", "sosreport.html", "sosreport.xml", "mtab"]
    OPTIONS={"debug":1, "verbose": 3, "batch": True, "progressbar":False, "nomultithread":False, "usealloptions": True}

class testSosReportNonExistant(testSosReportBase):
    OPTIONS={"debug":1, "verbose": 3, "batch": True, "progressbar":False, "nomultithread":False, "onlyplugins": ["null2"] }
    def testSosReport(self):
        from comoonics.sos.sosreport import SosReportException
        self.failUnlessRaises(SosReportException, self._sosreport.main)

def test_main():
    test_support.run_unittest(testSosReport1, testSosReport2, testSosReport3, testSosReport4, testSosReportNonExistant)

if __name__ == '__main__':
    test_main()