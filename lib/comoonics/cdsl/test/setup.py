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

class SetupBase(object):
    results={ "hd": (
                     "hd", 
                     True, 
                     [u'hd'],  # sourcepath
                     [u'.cluster/cdsl/1/hd', u'.cluster/cdsl/3/hd', u'.cluster/cdsl/2/hd', u'.cluster/cdsl/default/hd'], 
                     []
                     ),
              "hd/sd": (
                        "hd/sd", 
                        False, 
                        [u'.cluster/cdsl/1/hd/sd', u'.cluster/cdsl/3/hd/sd', u'.cluster/cdsl/2/hd/sd', u'.cluster/cdsl/default/hd/sd'],
                        [u'.cluster/shared/hd/sd'], 
                        [u'.cluster/shared/hd']
                        ), 
              "hd/sd/hf": (
                           "hd/.cdsl.sd/hf", 
                           True, 
                           [u'.cluster/shared/hd/sd/hf'], # sourcepath 
                           [u'.cluster/cdsl/1/hd/.cdsl.sd/hf', u'.cluster/cdsl/3/hd/.cdsl.sd/hf', u'.cluster/cdsl/2/hd/.cdsl.sd/hf', u'.cluster/cdsl/default/hd/.cdsl.sd/hf'], 
                           [u'.cluster/cdsl/1/hd/.cdsl.sd', u'.cluster/cdsl/3/hd/.cdsl.sd', u'.cluster/cdsl/2/hd/.cdsl.sd', u'.cluster/cdsl/default/hd/.cdsl.sd']
                           ),
              "hd/sd/hd": (
                           "hd/.cdsl.sd/hd", 
                           True, 
                           [u'.cluster/shared/hd/sd/hd'], # sourcepath 
                           [u'.cluster/cdsl/1/hd/.cdsl.sd/hd', u'.cluster/cdsl/3/hd/.cdsl.sd/hd', u'.cluster/cdsl/2/hd/.cdsl.sd/hd', u'.cluster/cdsl/default/hd/.cdsl.sd/hd'], 
                           [u'.cluster/cdsl/1/hd/.cdsl.sd', u'.cluster/cdsl/3/hd/.cdsl.sd', u'.cluster/cdsl/2/hd/.cdsl.sd', u'.cluster/cdsl/default/hd/.cdsl.sd']
                           ),
              "hd/sd/hd/sd": (
                              "hd/sd/.cdsl.hd/sd", 
                              False, 
                              [u'.cluster/cdsl/1/hd/.cdsl.sd/hd/sd', u'.cluster/cdsl/3/hd/.cdsl.sd/hd/sd', u'.cluster/cdsl/2/hd/.cdsl.sd/hd/sd', u'.cluster/cdsl/default/hd/.cdsl.sd/hd/sd'], 
                              [u'.cluster/shared/hd/sd/.cdsl.hd/sd'], 
                              [u'.cluster/shared/hd/sd/.cdsl.hd']
                              ),
              "hd/sd/hd/sf": (
                              "hd/sd/.cdsl.hd/sf", 
                              False, 
                              [u'.cluster/cdsl/1/hd/.cdsl.sd/hd/sf', u'.cluster/cdsl/3/hd/.cdsl.sd/hd/sf', u'.cluster/cdsl/2/hd/.cdsl.sd/hd/sf', u'.cluster/cdsl/default/hd/.cdsl.sd/hd/sf'], 
                              [u'.cluster/shared/hd/sd/.cdsl.hd/sf'], 
                              [u'.cluster/shared/hd/sd/.cdsl.hd']
                              ),
#                  "hd/sd/hd/sd/hd": ("hd/.cdsl.sd/hd/.cdsl.sd/hd", True),
#                      "hd/sd/hd/sd/hf": ("hd/.cdsl.sd/hd/.cdsl.sd/hf", True),
#                      "ne": ("ne", None),
#                      "hd/ne": ("hd/ne", None),
#                      "hd/sd/ne": ("hd/sd/ne", None),
#                      "hd/sd/hd/ne": ("hd/.cdsl.sd/hd/ne", None),
#                      "hd/sd/hd/sd/ne": ("hd/sd/.cdsl.hd/sd/ne", None),
                     }

class SetupCDSLRepository(SetupBase):
    def __init__(self, clusterinfo):
        super(SetupCDSLRepository, self).__init__()
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        import shutil
        os.mkdir(os.path.join(tmppath, "repo2"))
        os.mkdir(os.path.join(tmppath, "repo2/repo3"))
        os.mkdir(os.path.join(tmppath, "repo4"))
        os.mkdir(os.path.join(tmppath, "repo4/repo5"))
        os.mkdir(os.path.join(tmppath, "repo4/repo5/repo6"))
        os.mkdir(os.path.join(tmppath, "repo7"))
        os.mkdir(os.path.join(tmppath, "repo8"))
        os.makedirs(os.path.join(tmppath, "repo7", "var/lib/cdsl"))
        shutil.copyfile("cdsl4.xml", os.path.join(tmppath, "repo7", ComoonicsCdslRepository.default_resources[1]))
        
        self.cdslRepository1 = ComoonicsCdslRepository(clusterinfo=clusterinfo, root=tmppath, usenodeids="True")
        self.cdslRepository2 = ComoonicsCdslRepository(clusterinfo=clusterinfo, root=tmppath, mountpoint="repo2", usenodeids="True")
        self.cdslRepository1.addRepository(self.cdslRepository2)
        self.cdslRepository3 = ComoonicsCdslRepository(clusterinfo=clusterinfo, root=os.path.join(tmppath,"repo2"), mountpoint="repo3", usenodeids="True")
        self.cdslRepository2.addRepository(self.cdslRepository3)
        
        self.cdslRepository4 = ComoonicsCdslRepository(root=tmppath, mountpoint="repo4", usenodeids="True", maxnodeidnum="4")
        self.cdslRepository5 = ComoonicsCdslRepository(root=os.path.join(tmppath, "repo4"), mountpoint="repo5", usenodeids="True", maxnodeidnum="4")
        self.cdslRepository4.addRepository(self.cdslRepository5)
        self.cdslRepository6 = ComoonicsCdslRepository(root=os.path.join(tmppath, "repo4", "repo5"), mountpoint="repo6", usenodeids="True", maxnodeidnum="4")
        self.cdslRepository5.addRepository(self.cdslRepository6)
        
        #self.cdslRepository7 = ComoonicsCdslRepository(root=os.path.join(tmppath, "repo7"))

    def cleanUpInfrastructure(self, path):
        import shutil
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        os.rmdir(os.path.join(self.cdslRepository6.root, self.cdslRepository6.getMountpoint())) 
        os.rmdir(os.path.join(self.cdslRepository5.root, self.cdslRepository5.getMountpoint())) 
        os.rmdir(os.path.join(self.cdslRepository4.root, self.cdslRepository4.getMountpoint())) 
        os.rmdir(os.path.join(self.cdslRepository3.root, self.cdslRepository3.getMountpoint())) 
        os.rmdir(os.path.join(self.cdslRepository2.root, self.cdslRepository2.getMountpoint()))
        os.remove(os.path.join(tmppath, "repo7", ComoonicsCdslRepository.default_resources[1]))
        shutil.rmtree(os.path.join(tmppath, "repo7"))
        os.rmdir(os.path.join(tmppath, "repo8"))
            
class SetupCDSLs(SetupBase):
    def __init__(self, repository, mynodeid="1"):
        """
        Method to check if Module handels nested cdsls correctly. Creates a nested 
        cdsl-structure and check every single cdsl for existance. Creates a cdsl-object 
        without commiting it to filesystem to check if exists()-method fails correctly.
        """
        super(SetupCDSLs, self).__init__()

        #create cluster objects
        # create cdsl objects
        self.repository=repository
        self._createCDSLFiles(tmppath)
        self.mynodeid=mynodeid
        # cdslname: { expanded, HD/Shareed, sourcepaths, destpaths, subpaths
    
    def _createCDSLFiles(self, _tmppath):
        from comoonics.cdsl import cmpbysubdirs
        _cdsls=self.results.keys()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
            if _cdsl.endswith("d") and not os.path.exists(os.path.join(_tmppath, _cdsl)):
                os.makedirs(os.path.join(_tmppath, _cdsl))
            elif not os.path.exists(os.path.join(_tmppath, _cdsl)):
                open(os.path.join(_tmppath, _cdsl), "w+")

    def setupCDSLInfrastructure(self, path, cdslRepository, clusterinfo):
        from comoonics.cdsl.ComCdsl import Cdsl
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        self.repository.buildInfrastructure(clusterinfo)
        _dirs=self.results.keys()
        _dirs.sort()
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=self.repository.getCdsl(_path)
            except CdslNotFoundException:
                if self.results[_path][1] == True:
                    _cdsl=Cdsl(_path, Cdsl.HOSTDEPENDENT_TYPE, self.repository, clusterinfo)
                elif self.results[_path][1] == False:
                    _cdsl=Cdsl(_path, Cdsl.SHARED_TYPE, self.repository, clusterinfo)
            
            if _cdsl:
                self.repository.commit(_cdsl)
        
        self.repository.workingdir.pushd()
        if os.path.isdir(cdslRepository.getLinkPath()):
            os.rmdir(cdslRepository.getLinkPath())
            os.symlink(os.path.join(cdslRepository.getTreePath(), self.mynodeid), cdslRepository.getLinkPath())
        self._createCDSLFiles(path)
        self.repository.workingdir.popd()

    def cleanUpInfrastructure(self, path, cdslRepository, clusterinfo):
        for cdsl in self.repository.getCdsls():
            if cdsl.exists():
                cdsl.delete(True, True)
        self.repository.workingdir.pushd()
        if os.path.islink(cdslRepository.getLinkPath()):
            os.remove(cdslRepository.getLinkPath())
            os.mkdir(cdslRepository.getLinkPath())
        cdslRepository.removeInfrastructure(clusterinfo)

from unittest import TestProgram, TextTestRunner

class MyTestProgram(TestProgram):
    def runTests(self):
        if self.testRunner is None:
            self.testRunner = TextTestRunner(verbosity=self.verbosity)
        result = self.testRunner.run(self.test)
        self.result=result

def cleanup():
    if os.path.exists(tmppath):
        os.rmdir(tmppath)