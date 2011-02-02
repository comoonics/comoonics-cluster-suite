import sys
sys.path.append('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])

import unittest
import baseSetup
from comoonics.ComPath import Path
import os


class test_CdslRepository(unittest.TestCase):
    cwd=Path(os.getcwd())
    
    def setUp(self):
        pass
        
    def tearDown(self):
        self.cwd.popd()
    
    def testResource1(self):
        self.assertEquals(setupCDSLRepository.cdslRepository1.getResource(), ".cdsl_inventory.xml")

    def testResource2(self):
        """
        Test without clusterinfo
        """
        self.assertEquals(setupCDSLRepository.cdslRepository4.getResource(), ".cdsl_inventory.xml")

    def testTreePath(self):
        self.assertEquals(setupCDSLRepository.cdslRepository1.getTreePath(), ".cluster/cdsl")

    def testSharedtreePath(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getSharedTreepath(), ".cluster/shared")

    def testLinkPath(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getLinkPath(), ".cdsl.local")

    def testMountpoint1(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getMountpoint(), "")

    def testMountpoint2(self):
        """
        Test without clusterinfo
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository4.getMountpoint(), "repo4")

    def testDefaultDir(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getDefaultDir(), "default")
    
    def testMaxnodeidnum1(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getMaxnodeidnum(), "0")
 
    def testMaxnodeidnum2(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository4.getMaxnodeidnum(), "4")
 
    def testNodePrefix(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getNodePrefix(), "")
    
    def testUseNodeids(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getUseNodeids(), "True")
    
    def testExpandString(self):
        """
        @rtype: string
        """
        self.assertEquals(setupCDSLRepository.cdslRepository1.getExpandString(), ".cdsl")
    
    def testExpand1(self):
        from comoonics.cdsl.ComCdsl import Cdsl
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        _dirs=setupCDSLRepository.results.keys()
        _dirs.sort()
        setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
        self.cwd.pushd(baseSetup.tmppath)
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=setupCDSLRepository.cdslRepository1.getCdsl(_path, setupCDSLRepository.cdslRepository1)
            except CdslNotFoundException:
                if setupCDSLRepository.results[_path][1] == True:
                    _cdsl=Cdsl(_path, Cdsl.HOSTDEPENDENT_TYPE, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
                elif setupCDSLRepository.results[_path][1] == False:
                    _cdsl=Cdsl(_path, Cdsl.SHARED_TYPE, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
            
            if _cdsl:
                setupCDSLRepository.cdslRepository1.commit(_cdsl)
                _expanded=setupCDSLRepository.cdslRepository1.expandCdsl(_cdsl)
                _isexpanded=setupCDSLRepository.cdslRepository1.isExpandedDir(_expanded)
                _shouldnotbeexpanded=_expanded==_cdsl.src
                self.assertEquals(_expanded, setupCDSLRepository.results[_path][0], "Expansion of cdsl \"%s\" => \"%s\" != \"%s\"" %(_cdsl.src, _expanded, setupCDSLRepository.results[_path][0]))
                self.assertTrue(_isexpanded or _shouldnotbeexpanded, "Path %s=>%s should be detected as expanded but is not %s!!!" %(_cdsl.src, _expanded, _isexpanded))

        setupCDSLRepository.cdslRepository1.removeInfrastructure(setupCluster.clusterinfo)
        self.cwd.popd()

    def testExpand2(self):
        """
        Test without clusterinfo
        """
        from comoonics.cdsl.ComCdsl import Cdsl
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        self.cwd.pushd(baseSetup.tmppath)
        _dirs=setupCDSLRepository.results.keys()
        _dirs.sort()
        setupCDSLRepository.cdslRepository4.buildInfrastructure()
        for _path in _dirs:
            _cdsl=None
            try:
                _cdsl=setupCDSLRepository.cdslRepository4.getCdsl(_path)
            except CdslNotFoundException:
                if setupCDSLRepository.results[_path][1] == True:
                    _cdsl=Cdsl(_path, Cdsl.HOSTDEPENDENT_TYPE, setupCDSLRepository.cdslRepository4)
                elif setupCDSLRepository.results[_path][1] == False:
                    _cdsl=Cdsl(_path, Cdsl.SHARED_TYPE, setupCDSLRepository.cdslRepository4)
            
            if _cdsl:
                setupCDSLRepository.cdslRepository4.commit(_cdsl)
                _expanded=setupCDSLRepository.cdslRepository4.expandCdsl(_cdsl)
                _isexpanded=setupCDSLRepository.cdslRepository4.isExpandedDir(_expanded)
                _shouldnotbeexpanded=_expanded==_cdsl.src
                self.assertEquals(_expanded, setupCDSLRepository.results[_path][0], "Expansion of cdsl \"%s\" => \"%s\" != \"%s\"" %(_cdsl.src, _expanded, setupCDSLRepository.results[_path][0]))
                self.assertTrue(_isexpanded or _shouldnotbeexpanded, "Path %s=>%s should be detected as expanded but is not %s!!!" %(_cdsl.src, _expanded, _isexpanded))

        setupCDSLRepository.cdslRepository4.removeInfrastructure()
        self.cwd.popd()

    def testBuildInfrastructure1(self):
        setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
        self.cwd.pushd(os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository1.getMountpoint()))
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getTreePath()), "Cdsltree %s is no directory!" %setupCDSLRepository.cdslRepository1.getTreePath())
        self.assertEquals(setupCDSLRepository.cdslRepository1.getTreePath(True), os.path.realpath(os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository1.getTreePath())), "Cdsltree %s!=%s." %(setupCDSLRepository.cdslRepository1.getTreePath(True), os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository1.getTreePath())))
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getSharedTreepath()), "Cdsl sharedtree %s is no directory!" %setupCDSLRepository.cdslRepository1.getSharedTreepath())
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getLinkPath()), "Cdsl link %s is no directory" %setupCDSLRepository.cdslRepository1.getLinkPath())
        for _node in setupCluster.clusterinfo.getNodes():
            self.assertTrue(os.path.isdir(os.path.join(setupCDSLRepository.cdslRepository1.getTreePath(), _node.getId())), "Cdsl Nodedir %s is no directory!" %os.path.join(setupCDSLRepository.cdslRepository1.getTreePath(), _node.getId()))
        setupCDSLRepository.cdslRepository1.removeInfrastructure(setupCluster.clusterinfo)
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository1.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository2.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository3.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())
        self.assert_("Test assertion")

    def testBuildInfrastructure2(self):
        """
        Test without clusterinfo
        """
        setupCDSLRepository.cdslRepository4.buildInfrastructure()
        self.cwd.pushd(os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository4.getMountpoint()))
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository4.getTreePath()), "Cdsltree %s is no directory!" %setupCDSLRepository.cdslRepository1.getTreePath())
        self.assertEquals(setupCDSLRepository.cdslRepository4.getTreePath(True), os.path.realpath(os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository4.getMountpoint(), setupCDSLRepository.cdslRepository4.getTreePath())), "Cdsltree %s!=%s." %(setupCDSLRepository.cdslRepository1.getTreePath(True), os.path.join(baseSetup.tmppath, setupCDSLRepository.cdslRepository1.getTreePath())))
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository4.getSharedTreepath()), "Cdsl sharedtree %s is no directory!" %setupCDSLRepository.cdslRepository1.getSharedTreepath())
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository4.getLinkPath()), "Cdsl link %s is no directory" %setupCDSLRepository.cdslRepository1.getLinkPath())
        for _node in range(1, int(setupCDSLRepository.cdslRepository4.getMaxnodeidnum())+1):
            self.assertTrue(os.path.isdir(os.path.join(setupCDSLRepository.cdslRepository4.getTreePath(), str(_node))), "Cdsl Nodedir %s is no directory!" %os.path.join(setupCDSLRepository.cdslRepository4.getTreePath(), str(_node)))
        setupCDSLRepository.cdslRepository4.removeInfrastructure()
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository4.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository5.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())
        self.assertFalse(os.path.exists(setupCDSLRepository.cdslRepository6.getResource()), "The inventory file %s exists although it shouldn't." %setupCDSLRepository.cdslRepository1.getResource())

    def testVersionException(self):
        from comoonics.cdsl.ComCdslRepository import CdslVersionException, ComoonicsCdslRepository
        try:
            setupCDSLRepository.cdslRepository7 = ComoonicsCdslRepository(clusterinfo=setupCluster.clusterinfo, root=os.path.join(baseSetup.tmppath, "repo7"))
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
    setupCluster=baseSetup.SetupCluster()        
    setupCDSLRepository=baseSetup.SetupCDSLRepository(setupCluster.clusterinfo)  
    #import sys;sys.argv = ['', 'Test.testName']
    module=baseSetup.MyTestProgram(module=test_CdslRepository(methodName='run'))
    setupCDSLRepository.cleanUpInfrastructure(baseSetup.tmppath)
    baseSetup.cleanup()
    sys.exit(module.result.wasSuccessful())
    
