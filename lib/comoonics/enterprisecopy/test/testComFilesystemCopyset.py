'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        import tempfile
        import os.path
        from comoonics.enterprisecopy.ComPathCopyObject import PathCopyObject 
        from comoonics.enterprisecopy.ComCopyObject import registerCopyObject
        registerCopyObject("path", PathCopyObject)
        self.files = [ "test1", "test2", "test3", "test4", "test5" ]
        self.tempdirsource=tempfile.mkdtemp("destsource")
        self.tempdirdest=tempfile.mkdtemp("destdir")
        self.temparchivesource=tempfile.mkstemp(".tar.gz", "archivesource")
        self.temparchivemetadata=tempfile.mkstemp(".tar", "archivemetatdata")
        self.sourcedisk="/dev/zda"
        self.destdisk="/dev/zdb"
        for f in self.files:
            _f=open(os.path.join(self.tempdirsource, f), "w")
            _f.close()
            
    def tearDown(self):
        import os.path
        for f in self.files:
            if os.path.exists(os.path.join(self.tempdirsource, f)):
                os.remove(os.path.join(self.tempdirsource, f))
            if os.path.exists(os.path.join(self.tempdirdest, f)):
                os.remove(os.path.join(self.tempdirdest, f))
        if os.path.exists(self.temparchivemetadata[1]):
            os.remove(self.temparchivemetadata[1])
        if os.path.exists(self.temparchivesource[1]):
            os.remove(self.temparchivesource[1])
                                       
    def testFilesystemCopyObjectArchive1(self):
        import tarfile
        import os.path
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
        """ %(self.tempdirsource, self.temparchivemetadata[1], self.temparchivesource[1])           
        self.__testCopyset(_xml)
        tar=tarfile.open(self.temparchivesource[1])
        tarok=True
        for tarinfo in tar:
            if tarinfo.name == "./":
                continue
            elif os.path.basename(tarinfo.name) in self.files:
                continue
            else:
                tarok=False
        self.failIfEqual(tarok , False, "Tarfile %s does not consist of files %s." %(self.temparchivesource[1], self.files))
        tar.close()

        tar=tarfile.open(self.temparchivemetadata[1])
        tarok=True
        for tarinfo in tar:
            if tarinfo.name == "./":
                continue
            elif os.path.basename(tarinfo.name) == "path.xml":
                continue
            else:
                tarok=False
        self.failIfEqual(tarok , False, "MetadataTarfile %s does not consist of files path.xml." %(self.temparchivemetadata[1]))
        tar.close()

    def testFilesystemCopyObjectArchive2(self):
        import tarfile
        import os.path
        _xml="""
    <copyset type="filesystem" name="save-tmp">
        <source type="backup">
            <metadata>
                <archive name='%s' format='tar' type='file'>
                    <file name='./path.xml'/>
                </archive>
            </metadata>
            <data>
                <archive name='%s' format='tar' type='file' compression='gzip'/>
            </data>
        </source>
        <destination type="path">
            <path name="%s"/>
        </destination>
    </copyset>
        """ %(self.temparchivemetadata[1], self.temparchivesource[1], self.tempdirdest)
        # Create what we need
        self.testFilesystemCopyObjectArchive1()           
        self.__testCopyset(_xml)
        destok=True
        for f in self.files:
            if os.path.exists(os.path.join(self.tempdirdest, f)):
                continue
            else:
                destok=False
        self.failIfEqual(destok , False, "Destination %s does not consist of files %s." %(self.tempdirdest, self.files))

    def testFilesystemCopyObject1(self):
        import os.path
        _xml="""
    <copyset type="filesystem" name="save-tmp">
        <source type="path">
            <path name="%s"/>
        </source>
        <destination type="path">
            <path name="%s"/>
        </destination>
    </copyset>
        """ %(self.tempdirsource, self.tempdirdest)           
        self.__testCopyset(_xml)
        destok=True
        for f in self.files:
            if os.path.exists(os.path.join(self.tempdirdest, f)):
                continue
            else:
                destok=False
        self.failIfEqual(destok , False, "Destination %s does not consist of files %s." %(self.tempdirdest, self.files))

    def testFilesystemCopyObject2(self):
        from comoonics import ComSystem
        _xml="""
 <copyset type="filesystem" name="save-tmp">
    <source type="filesystem">
      <device id="sourcerootfs" name="/dev/vg_vmware_cluster_sr/lv_sharedroot" options="skipmount">
        <filesystem type="gfs"/>
        <mountpoint name="/">
          <option value="lock_nolock" name="lockproto"/>
          <option value="hdfhgg" name="locktable"/>
        </mountpoint>
      </device>
    </source>
    <destination type="filesystem">
      <device id="destrootfs" name="/dev/vg_vmware_cluster_srC/lv_sharedroot">
        <filesystem clustername="vmware_cluster" type="gfs"/>
        <mountpoint name="/var/lib/com-ec/dest">
          <option value="lock_nolock" name="lockproto"/>
          <option value="jhdshf" name="locktable"/>
        </mountpoint>
      </device>
    </destination>
 </copyset>
        """          
        oldexecmode=ComSystem.getExecMode()
        ComSystem.setExecMode(ComSystem.SIMULATE)
        self.__testCopyset(_xml)
        ComSystem.setExecMode(oldexecmode)

    def __testCopyset(self, _xml):
        from xml.dom.ext.reader import Sax2
        from comoonics.enterprisecopy.ComFilesystemCopyset import FilesystemCopyset
        reader=Sax2.Reader(validate=0)
        doc=reader.fromString(_xml)
        _copyset=FilesystemCopyset(doc.documentElement, doc)
        try:
            _copyset.doPre()
            _copyset.doCopy()
            _copyset.doPost()
        except Exception, e:
            import traceback
            traceback.print_exc(None)
            self.fail("Could not execute copyset %s, error: %s" %(_copyset.getAttribute("name"), e))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()