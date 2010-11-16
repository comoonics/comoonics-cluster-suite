'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):


    def setUp(self):
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        from comoonics.enterprisecopy.ComPathCopyObject import PathCopyObject
        from comoonics.enterprisecopy.ComCopyObject import registerCopyObject
        registerCopyObject("path", PathCopyObject)

    def tearDown(self):
        pass


    def testName(self):
        _xml="""
    <copyset type="filesystem" name="save-sysreport-redhat">
        <source type="path">
            <path name="/tmp/sysreport-$(date -u +%G%m%d%k%M%S | /usr/bin/tr -d ' ')"/>
        </source>
        <destination type="backup">
            <metadata>
                <archive name='/tmp/meta-clone-lilr627-02.tar' format='tar' type='file'>
                    <file name='./path.xml'/>
                </archive>
            </metadata>
            <data>
                <archive name='/tmp/path-02.tgz' format='tar' type='file' compression='gzip'/>
            </data>
        </destination>
    </copyset>"""
        from comoonics.enterprisecopy.ComCopyset import Copyset
        from comoonics import XmlTools
        doc=XmlTools.parseXMLString(_xml)
        _copyset=Copyset(doc.documentElement, doc)
        self.__testPathCopyset(_copyset)
           
    def __testPathCopyset(self, _modset):
        try:
            _modset.doPre()
            _modset.doCopy()
            _modset.doPost()
        except Exception, e:
            self.assert_("Could not execute copyset %s. Error: %s" %(_modset, e))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()