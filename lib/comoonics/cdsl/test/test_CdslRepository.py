import sys
sys.path.append('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])

import unittest
import baseSetup
from comoonics.ComPath import Path
import os
from comoonics.cdsl import getCdsl,  CDSL_HOSTDEPENDENT_TYPE, CDSL_SHARED_TYPE, CdslNotFoundException, getCdslRepository
import logging
from comoonics import ComLog

class test_CdslRepository(unittest.TestCase):
    cwd=Path(os.getcwd())
    
    def setUp(self):
        pass
        
    def tearDown(self):
        self.cwd.popd()
    
    def testResource(self):
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getResource(), ".cdsl_inventory.xml")

    def testTreePath(self):
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getTreePath(), ".cluster/cdsl")

    def testSharedtreePath(self):
        """
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getSharedTreepath(), ".cluster/shared")

    def testLinkPath(self):
        """
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getLinkPath(), ".cdsl.local")

    def testMountpoint1(self):
        """
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getMountpoint(), "")

    def testMountpoint2(self):
        """
        Test without clusterinfo
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            for childrepo in repository.getRepositories().values():
                self.assertEquals(childrepo.getMountpoint()[0:4], "repo")

    def testDefaultDir(self):
        """
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getDefaultDir(), "default")
    
    def testMaxnodeidnum1(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepositories[0].getMaxnodeidnum(), "0")
 
    def testMaxnodeidnum2(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepositories[1].getMaxnodeidnum(), "4")
 
    def testMaxnodeidnum3(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepositories[2].getMaxnodeidnum(), "0")
 
    def testNodePrefix(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepositories[0].getNodePrefix(), "")
    
    def testUseNodeids(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepositories[0].getUseNodeids(), "True")
    
    def testExpandString(self):
        """
        @rtype: string
        """
        for repository in setupCDSLRepository.cdslRepositories:
            self.assertEquals(repository.getExpandString(), ".cdsl")
    
    def testExpand(self):
        for i in range(len(setupCDSLRepository.cdslRepositories)):
            self._testExpand(setupCDSLRepository.cdslRepositories[i], setupCluster.clusterInfos[i], setupCDSLRepository.results)

    def _testExpand(self, repository, clusterinfo, results):
        """
        Test without clusterinfo
        """
        self.cwd.pushd(os.path.join(repository.root, repository.getMountpoint()))
#        setupCDSLRepository._createCDSLFiles(".")
        _dirs=results.keys()
        _dirs.sort()
        repository.buildInfrastructure(clusterinfo)
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=repository.getCdsl(_path)
            except CdslNotFoundException:
                if results[_path][1] == True:
                    _cdsl=getCdsl(_path, CDSL_HOSTDEPENDENT_TYPE, repository, clusterinfo)
                elif results[_path][1] == False:
                    _cdsl=getCdsl(_path, CDSL_SHARED_TYPE, repository, clusterinfo)
            
            if _cdsl:
                repository.commit(_cdsl)
                _expanded=repository.expandCdsl(_cdsl)
                _isexpanded=repository.isExpandedDir(_expanded)
                _shouldnotbeexpanded=_expanded==_cdsl.src
                self.assertEquals(_expanded, results[_path][0], "Expansion of cdsl \"%s\" => \"%s\" != \"%s\"" %(_cdsl.src, _expanded, results[_path][0]))
                self.assertTrue(_isexpanded or _shouldnotbeexpanded, "Path %s=>%s should be detected as expanded but is not %s!!!" %(_cdsl.src, _expanded, _isexpanded))

        repository.removeInfrastructure(clusterinfo)
#        setupCDSLRepository._removeCDSLFiles(".")
        self.cwd.popd()

    def testCdsls(self):
        for i in range(len(setupCDSLRepository.cdslRepositories)):
            self._testCdsls(setupCDSLRepository.cdslRepositories[i], setupCluster.clusterInfos[i], setupCDSLRepository.results)
        setupCDSLRepository._removeCDSLFiles(baseSetup.tmppath)

    def _testCdsls(self, repository, clusterinfo, results):
        self.cwd.pushd(os.path.join(repository.root, repository.getMountpoint()))
#        setupCDSLRepository._createCDSLFiles(".")
        _dirs=results.keys()
        _dirs.sort()
        repository.buildInfrastructure(clusterinfo)
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=repository.getCdsl(_path)
            except CdslNotFoundException:
                if results[_path][1] == True:
                    _cdsl=getCdsl(_path, CDSL_HOSTDEPENDENT_TYPE, repository, clusterinfo)
                elif results[_path][1] == False:
                    _cdsl=getCdsl(_path, CDSL_SHARED_TYPE, repository, clusterinfo)
            
            if _cdsl:
                self.assert_(repository.commit(_cdsl))
        ComLog.setLevel(logging.DEBUG, "comoonics.cdsl")
        repository.refresh()
        ComLog.setLevel(logging.INFO, "comoonics.cdsl")
        for cdsl in repository.getCdsls():
            self.assert_(repository.delete(cdsl))
        repository.removeInfrastructure(clusterinfo)       
#        setupCDSLRepository._removeCDSLFiles(".")
        self.cwd.popd()
        
    def testBuildInfrastructures(self):
        for i in range(len(setupCDSLRepository.cdslRepositories)):
            self._testBuildInfrastructure(setupCDSLRepository.cdslRepositories[i], setupCluster.clusterInfos[i])

    def _testBuildInfrastructure(self, repository, clusterinfo):
        repository.buildInfrastructure(clusterinfo)
        self.cwd.pushd(os.path.join(repository.root, repository.getMountpoint()))
        self.assertTrue(os.path.isdir(repository.getTreePath()), 
                        "Cdsltree %s is no directory, repository %s!" %(repository.getTreePath(), repository))
        self.assertEquals(repository.getTreePath(True), 
                          os.path.realpath(os.path.join(repository.root, repository.getMountpoint(), repository.getTreePath())), 
                          "Cdsltree %s!=%s, repository %s." %(repository.getTreePath(True), os.path.join(repository.root, repository.getMountpoint(), repository.getTreePath()), repository))
        self.assertTrue(os.path.isdir(repository.getSharedTreepath()), 
                        "Cdsl sharedtree %s is no directory for repository %s!" %(repository.getSharedTreepath(), repository))
        self.assertTrue(os.path.isdir(repository.getLinkPath()), 
                        "Cdsl link %s is no directory for repository %s" %(repository.getLinkPath(), repository))
        if clusterinfo:
            ids=clusterinfo.getNodeIdentifiers("id")
        else:
            ids=range(1, int(repository.getMaxnodeidnum())+1)
        for _node in ids:
            self.assertTrue(os.path.isdir(os.path.join(repository.getTreePath(), str(_node))), 
                            "Cdsl Nodedir %s is no directory for repository %s!" %(os.path.join(repository.getTreePath(), str(_node)), repository))
        repository.removeInfrastructure(clusterinfo)
        self.assertResourcesExist(repository)
        
    def assertResourcesExist(self, repository):
        self.assertFalse(os.path.exists(repository.getResource()), 
                         "The inventory file %s exists although it shouldn't." %repository.getResource())
        for childrepo in repository.getRepositories().values():
            self.assertResourcesExist(childrepo)

    def testVersionException(self):
        from comoonics.cdsl.ComCdslRepository import CdslVersionException
        try:
            getCdslRepository(clusterinfo=setupCluster.clusterInfos[0], root=os.path.join(baseSetup.tmppath, "repo7"))
            self.assert_("CdslVersionException not risn. Error")
        except CdslVersionException:
            pass
    
    def testMigration(self):
        import comoonics.cdsl.migration
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        from comoonics import XmlTools
        from comoonics.cdsl import stripleadingsep
        fromsource=os.path.join(baseSetup.testpath, "cdsl4.xml")
        cwd=Path()
        cwd.pushd(baseSetup.tmppath)
        repository=comoonics.cdsl.migration.migrate(None, ComoonicsCdslRepository.version, fromresource=fromsource, root=baseSetup.tmppath, mountpoint="repo8", ignoreerrors=True)
        oldelement=XmlTools.parseXMLFile(fromsource)
        wanttocdsls=oldelement.documentElement.getElementsByTagName("cdsl")
        for i in range(len(wanttocdsls)):
            wanttocdsl=wanttocdsls[i]
            src=stripleadingsep(wanttocdsl.getAttribute("src"))
            iscdsl=repository.getCdsl(src)
            self.assertTrue(wanttocdsl.getAttribute("timestamp") == iscdsl.getAttribute("timestamp") and \
                            wanttocdsl.getAttribute("type") == iscdsl.getAttribute("type"), \
                            "Cdsl %s has different timestamp or type after migration" %iscdsl)
        os.remove(os.path.join(repository.root, repository.getMountpoint(), repository.resource))
        cwd.popd()
            
if __name__ == "__main__":
    logging.basicConfig()
    ComLog.setLevel(logging.INFO)
    setupCluster=baseSetup.SetupCluster()        
    setupCDSLRepository=baseSetup.SetupCDSLRepository()  
    #import sys;sys.argv = ['', 'Test.testName']
    module=baseSetup.MyTestProgram(module=test_CdslRepository(methodName='run'))
    setupCDSLRepository.cleanUpInfrastructure(baseSetup.tmppath)
    baseSetup.cleanup()
    sys.exit(module.result.wasSuccessful())
