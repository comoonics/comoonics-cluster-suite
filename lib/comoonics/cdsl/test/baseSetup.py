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
    if _module.endswith("baseSetup"):
        testpath=os.path.realpath(os.path.dirname(sys.modules[_module].__file__))
                
import tempfile
tmppath=os.path.realpath(tempfile.mkdtemp("", "test_Cdsl"))
print "Tmppath: %s" %tmppath
print "Testpath: %s" %(testpath)

class SetupCluster:
    def __init__(self):
        from comoonics.cluster import getClusterRepository, getClusterInfo
        self.clusterRepositories = []
        self.clusterInfos = []
        self.clusterRepositories.append(getClusterRepository(os.path.join(testpath, "cluster.conf")))
        self.clusterInfos.append(getClusterInfo(self.clusterRepositories[0]))
        
        self.clusterRepositories.append(None)
        self.clusterInfos.append(None)
        
        self.clusterRepositories.append(getClusterRepository(maxnodeidnum=3))
        self.clusterInfos.append(getClusterInfo(self.clusterRepositories[2]))

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

    def _createCDSLFiles(self, _tmppath):
        from comoonics.cdsl import cmpbysubdirs
        _cdsls=self.results.keys()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
            if _cdsl.endswith("d") and not os.path.exists(os.path.join(_tmppath, _cdsl)):
                os.makedirs(os.path.join(_tmppath, _cdsl))
            elif not os.path.exists(os.path.join(_tmppath, _cdsl)):
                open(os.path.join(_tmppath, _cdsl), "w+")

    def _removeCDSLFiles(self, _tmppath):
        from comoonics.cdsl import cmpbysubdirs
        _cdsls=self.results.keys()
        _cdsls.sort(cmpbysubdirs)
        _cdsls.reverse()
        for _cdsl in _cdsls:
            if _cdsl.endswith("d") and os.path.exists(os.path.join(_tmppath, _cdsl)):
                os.rmdir(os.path.join(_tmppath, _cdsl))
            elif os.path.exists(os.path.join(_tmppath, _cdsl)):
                os.remove(os.path.join(_tmppath, _cdsl))

class SetupCDSLRepository(SetupBase):
    def __init__(self):
        super(SetupCDSLRepository, self).__init__()
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        from comoonics.cdsl import getCdslRepository
        from comoonics.ComPath import Path
        import shutil
        os.mkdir(os.path.join(tmppath, "repo1"))
        os.mkdir(os.path.join(tmppath, "repo1/repo2"))
        os.mkdir(os.path.join(tmppath, "repo1/repo2/repo3"))
        os.mkdir(os.path.join(tmppath, "repo4"))
        os.mkdir(os.path.join(tmppath, "repo4/repo5"))
        os.mkdir(os.path.join(tmppath, "repo4/repo5/repo6"))
        os.mkdir(os.path.join(tmppath, "repo7"))
        os.mkdir(os.path.join(tmppath, "repo8"))
        os.mkdir(os.path.join(tmppath, "repo8/repo9"))
        os.mkdir(os.path.join(tmppath, "repo8/repo9/repo10"))
        
        # Need for testing migration!!
        # Will be created inside test not here!!
        os.makedirs(os.path.join(tmppath, "repo7", "var/lib/cdsl"))
        shutil.copyfile(os.path.join(testpath, "cdsl4.xml"), os.path.join(tmppath, "repo7", ComoonicsCdslRepository.default_resources[1]))
        
        wpath=Path()
        wpath.pushd(tmppath)
        self.cdslRepositories= []
        
        repopath=os.path.join(tmppath, "repo1")
        cdslRepository1 = getCdslRepository(root=repopath, usenodeids="True")
        cdslRepository2 = getCdslRepository(root=repopath, mountpoint="repo2", usenodeids="True")
        cdslRepository1.addRepository(cdslRepository2)
        cdslRepository3 = getCdslRepository(root=os.path.join(repopath,"repo2"), mountpoint="repo3", usenodeids="True")
        cdslRepository2.addRepository(cdslRepository3)
        self.cdslRepositories.append(cdslRepository1)
        
        repopath=os.path.join(tmppath, "repo4")
        cdslRepository1 = getCdslRepository(root=repopath, mountpoint="", usenodeids="True", maxnodeidnum="4")
        cdslRepository2 = getCdslRepository(root=repopath, mountpoint="repo5", usenodeids="True", maxnodeidnum="4")
        cdslRepository1.addRepository(cdslRepository2)
        cdslRepository3 = getCdslRepository(root=os.path.join(repopath, "repo5"), mountpoint="repo6", usenodeids="True", maxnodeidnum="4")
        cdslRepository2.addRepository(cdslRepository3)
        self.cdslRepositories.append(cdslRepository1)

        repopath=os.path.join(tmppath, "repo8")
        cdslRepository1 = getCdslRepository(root=repopath, usenodeids="True")
        cdslRepository2 = getCdslRepository(root=repopath, mountpoint="repo9", usenodeids="True")
        cdslRepository1.addRepository(cdslRepository2)
        cdslRepository3 = getCdslRepository(root=os.path.join(repopath,"repo9"), mountpoint="repo10", usenodeids="True")
        cdslRepository2.addRepository(cdslRepository3)
        self.cdslRepositories.append(cdslRepository1)

        wpath.popd()
        #self.cdslRepository7 = ComoonicsCdslRepository(root=os.path.join(tmppath, "repo7"))

    def cleanUpInfrastructure(self, path):
        for repo in self.cdslRepositories:
            self.cleanUpRepo(repo)
            os.rmdir(os.path.join(repo.root, repo.getMountpoint()))
            
        # now repo7
        os.remove(os.path.join(tmppath, "repo7", "var", "lib", "cdsl", "cdsl_inventory.xml"))
        os.rmdir(os.path.join(tmppath, "repo7", "var", "lib", "cdsl"))
        os.rmdir(os.path.join(tmppath, "repo7", "var", "lib"))
        os.rmdir(os.path.join(tmppath, "repo7", "var"))
        os.rmdir(os.path.join(tmppath, "repo7"))
    
    def cleanUpRepo(self, repo):
        if repo.getRepositories():
            for childrepo in repo.getRepositories().values():
                self.cleanUpRepo(childrepo)
                os.rmdir(os.path.join(childrepo.root, childrepo.getMountpoint()))
            
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
    
    def _createRepository(self, clusterinfo):
        from comoonics.cdsl import getCdsl, CdslNotFoundException, CDSL_HOSTDEPENDENT_TYPE, CDSL_SHARED_TYPE
        _dirs=self.results.keys()
        _dirs.sort()
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=self.repository.getCdsl(_path)
            except CdslNotFoundException:
                if self.results[_path][1] == True:
                    _cdsl=getCdsl(_path, CDSL_HOSTDEPENDENT_TYPE, self.repository, clusterinfo)
                elif self.results[_path][1] == False:
                    _cdsl=getCdsl(_path, CDSL_SHARED_TYPE, self.repository, clusterinfo)
            
            if _cdsl:
                self.repository.commit(_cdsl)
    
    def setupCDSLInfrastructure(self, path, cdslRepository, clusterinfo):
        from comoonics.ComPath import Path
        self.repository.buildInfrastructure(clusterinfo)
        self._createRepository(clusterinfo)
        wpath=Path()
        wpath.pushd(self.repository.workingdir)
        if os.path.isdir(cdslRepository.getLinkPath()):
            os.rmdir(cdslRepository.getLinkPath())
            os.symlink(os.path.join(cdslRepository.getTreePath(), self.mynodeid), cdslRepository.getLinkPath())
        self._createCDSLFiles(path)
        wpath.popd()

    def cleanUpInfrastructure(self, path, cdslRepository, clusterinfo):
        from comoonics.ComPath import Path
        for cdsl in self.repository.getCdsls():
            if cdsl.exists():
                cdsl.delete(True, True)
        wpath=Path()
        wpath.pushd(self.repository.workingdir)
        if os.path.islink(cdslRepository.getLinkPath()):
            os.remove(cdslRepository.getLinkPath())
            os.mkdir(cdslRepository.getLinkPath())
        cdslRepository.removeInfrastructure(clusterinfo)
        wpath.popd()

from unittest import TestProgram, TextTestRunner

class MyTestProgram(TestProgram):
    repository=None
    def runTests(self):
        if self.testRunner is None:
            self.testRunner = TextTestRunner(verbosity=self.verbosity)
        result = self.testRunner.run(self.test)
        self.result=result

def cleanup():
    if os.path.exists(tmppath):
        os.rmdir(tmppath)