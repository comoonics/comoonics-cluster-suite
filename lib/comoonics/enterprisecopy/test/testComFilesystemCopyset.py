'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        from comoonics.enterprisecopy.ComPathCopyObject import PathCopyObject 
        from comoonics.enterprisecopy.ComCopyObject import registerCopyObject
        registerCopyObject("path", PathCopyObject)
        
    def testFilesystemCopyObject1(self):
        import tempfile
        from comoonics.enterprisecopy.ComCopyset import Copyset
        tempd=tempfile.mkdtemp("testFilesystemCopyObject1")
        tempf=tempfile.mktemp("testFilesystemCopyObject1", ".tar")
        tempm=tempfile.mktemp("testFilesystemCopyObject1", ".tar.gz")
        _xml="""
    <copyset type="filesystem" name="save-tmp">
        <source type="path">
            <path name="%s"/>
        </source>
        <destination type="backup">
            <metadata>
                <archive name='%s' format='tar' type='file'>
                    <file name='./path.xml'/>
                </archive>
            </metadata>
            <data>
                <archive name='%s' format='tar' type='file' compression='gzip'/>
            </data>
        </destination>
    </copyset>
        """ %(tempd, tempm, tempf)           
        from xml.dom.ext.reader import Sax2
        reader=Sax2.Reader(validate=0)
        doc=reader.fromString(_xml)
        _copyset=Copyset(doc.documentElement, doc)
        self.__testCopyset(_copyset)

    def testFilesystemCopyObject2(self):
        from comoonics.enterprisecopy.ComFilesystemCopyset import FilesystemCopyset
        from comoonics.enterprisecopy.ComPathCopyObject import PathCopyObject
        FilesystemCopyset.DEFAULT_OPTIONS=["--archive", "--update", "--one-file-system"]
        copyset=FilesystemCopyset(PathCopyObject(path="/tmp", source=True), PathCopyObject(path="/tmp2", dest=True))
        self.__testCopyset(copyset)

    def __testCopyset(self, _copyset):
        try:
            _copyset.doPre()
            _copyset.doCopy()
            _copyset.doPost()
        except Exception, e:
            self.assert_("Could not execute copyset %s" %_copyset)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()