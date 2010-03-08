'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def testSCSIRescan(self):
        from xml.dom.ext.reader import Sax2
        from comoonics.enterprisecopy.ComSCSIRequirement import SCSIRequirement
        from comoonics.scsi.ComSCSI import SCSIException
        reader=Sax2.Reader(validate=0)
        xmlbuf='<requirement type="scsi" format="fc" name="rescan" dest="host16"/>'
        doc=reader.fromString(xmlbuf)
        scsireq=SCSIRequirement(doc.documentElement, doc)
        try:
            scsireq.doPre()
            self.assert_("Expecting exception that host cannot be written.")
        except SCSIException, se:
            pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()