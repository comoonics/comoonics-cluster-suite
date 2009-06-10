import logging
from comoonics import ComLog
from comoonics import ComSystem
import os.path
import sys
ComLog.setLevel(logging.DEBUG)

#set behaviour of comsystem, could be ask, simulate or continue
ComSystem.__EXEC_REALLY_DO="continue"

testpath=os.path.dirname(sys.argv[0])
for _module in sys.modules.keys():
    if _module.endswith("test_Cdsl"):
        testpath=os.path.dirname(sys.modules[_module].__file__)
                
import tempfile
tmppath=tempfile.mkdtemp("", "test_Cdsl")
print "Tmppath: %s" %tmppath

class SetupCluster:
    def __init__(self):
        import comoonics.cluster
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        doc=comoonics.cluster.parseClusterConf(os.path.join(testpath, "cluster.conf"))
    
        self.clusterRepository = ClusterRepository(doc.documentElement,doc)
        self.clusterinfo = ClusterInfo(self.clusterRepository)

class SetupCDSLRepository:
    def __init__(self):
        from comoonics.cdsl.ComCdslRepository import CdslRepository
        import shutil
        shutil.copy(os.path.join(testpath, "cdsl5.xml"), tmppath)
        shutil.copy(os.path.join(testpath, "cdsl4.xml"), tmppath)
        self.cdslRepository1 = CdslRepository(os.path.join(tmppath, "cdsl5.xml"), None, False, mountpoint=tmppath, usenodeids="True")
        self.cdslRepository2 = CdslRepository(os.path.join(tmppath, "cdsl4.xml"), None, False, mountpoint=tmppath, usenodeids="True")
        self.cdslRepository1.root=tmppath
        self.cdslRepository2.root=tmppath
        
    def cleanUpInfrastructure(self, path):
        os.remove(os.path.join(path, "cdsl5.xml"))        
        os.remove(os.path.join(path, "cdsl4.xml"))
            
class SetupCDSLs:
    def __init__(self, repository, mynodeid="1"):
        """
        Method to check if Module handels nested cdsls correctly. Creates a nested 
        cdsl-structure and check every single cdsl for existance. Creates a cdsl-object 
        without commiting it to filesystem to check if exists()-method fails correctly.
        """

        #create cluster objects
        # create cdsl objects
        self.repository=repository
        self._createCDSLFiles(tmppath)
        self.mynodeid=mynodeid
    
    def _createCDSLFiles(self, _tmppath):
        from comoonics.cdsl import cmpbysubdirs
        _cdsls=self.repository.getCdsls()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
            if _cdsl.src.endswith("dir") and not os.path.exists(os.path.join(_tmppath, _cdsl.src)):
                os.makedirs(os.path.join(_tmppath, _cdsl.src))
            elif not os.path.exists(os.path.join(_tmppath, _cdsl.src)):
                open(os.path.join(_tmppath, _cdsl.src), "w+")

    def setupCDSLInfrastructure(self, path, cdslRepository):
        os.chdir(path)
        if os.path.isdir(cdslRepository.getDefaultCdslLink()):
            os.rmdir(cdslRepository.getDefaultCdslLink())
            os.symlink(os.path.join(cdslRepository.getDefaultCdsltree(), self.mynodeid), cdslRepository.getDefaultCdslLink())

    def cleanUpInfrastructure(self, path, cdslRepository, clusterinfo):
        os.chdir(path)
        os.remove(cdslRepository.getDefaultCdslLink())
        for node in clusterinfo.getNodes():
            os.rmdir(os.path.join(cdslRepository.getDefaultCdsltree(), node.getId()))
        os.rmdir(os.path.join(cdslRepository.getDefaultCdsltree(), cdslRepository.getDefaultDefaultDir()))
        os.rmdir(cdslRepository.getDefaultCdsltreeShared())
        _path=cdslRepository.getDefaultCdsltree()
        
        while _path != "":
            os.rmdir(_path)
            _path=os.path.dirname(_path)

