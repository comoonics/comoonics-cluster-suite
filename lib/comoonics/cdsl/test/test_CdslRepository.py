import unittest
import setup

setupCluster=setup.SetupCluster()        
setupCDSLRepository=setup.SetupCDSLRepository()  

class test_CdslRepository(unittest.TestCase):
    def testExpand(self):
        from comoonics.cdsl import guessType
        from comoonics.cdsl.ComCdsl import Cdsl
        _results={ "hostdependent_dir": "hostdependent_dir", 
                   "hostdependent_dir/shared_dir": "hostdependent_dir/shared_dir", 
                   "hostdependent_dir/shared_dir/hostdependent_dir": "hostdependent_dir.cdsl/shared_dir/hostdependent_dir",
                   "hostdependent_dir/shared_dir/hostdependent_dir/shared_dir": "hostdependent_dir.cdsl/shared_dir/hostdependent_dir/shared_dir",
                   "hostdependent_dir/shared_dir/hostdependent_file": "hostdependent_dir.cdsl/shared_dir/hostdependent_file",
                   "hostdependent_dir/shared_dir/hostdependent_dir/shared_file": "hostdependent_dir.cdsl/shared_dir/hostdependent_dir/shared_file",
                   "not_existent": "not_existent",
                   "hostdependent_dir/not_existent": "hostdependent_dir/not_existent",
                   "hostdependent_dir/shared_dir/not_existent": "hostdependent_dir.cdsl/shared_dir/not_existent",
                   "hostdependent_dir/shared_dir/hostdependent_dir/not_existent": "hostdependent_dir.cdsl/shared_dir/hostdependent_dir/not_existent",
                   "hostdependent_dir/shared_dir/hostdependent_dir/shared_dir/not_existent": "hostdependent_dir.cdsl/shared_dir/hostdependent_dir/shared_dir/not_existent",
                    }
        _dirs=_results.keys()
        _dirs.sort()
        for _path in _dirs:
            _cdsl=setupCDSLRepository.cdslRepository2.getCdsl(_path)
            if not _cdsl:
                _cdsl=Cdsl(_path, guessType(_path, setupCDSLRepository.cdslRepository2), setupCDSLRepository.cdslRepository2, setupCluster.clusterinfo, None, None, setup.tmppath)
                
            _expanded=setupCDSLRepository.cdslRepository2.expandCdsl(_cdsl)
            self.assertEquals(_expanded, _results[_path], "Expansion of cdsl %s => %s != %s" %(_cdsl.src, _expanded, _results[_path]))

    def testBuildInfrastructure(self):
        import os
        import os.path
        setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
        os.chdir(setup.tmppath)
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getDefaultCdsltree()), "Cdsltree %s is no directory!" %setupCDSLRepository.cdslRepository1.getDefaultCdsltree())
        self.assertEquals(setupCDSLRepository.cdslRepository1.getDefaultCdsltree(True), os.path.join(setup.tmppath, setupCDSLRepository.cdslRepository1.getDefaultCdsltree()), "Cdsltree %s!=%s." %(setupCDSLRepository.cdslRepository1.getDefaultCdsltree(True), os.path.join(setup.tmppath, setupCDSLRepository.cdslRepository1.getDefaultCdsltree())))
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getDefaultCdsltreeShared()), "Cdsl sharedtree %s is no directory!" %setupCDSLRepository.cdslRepository1.getDefaultCdsltreeShared())
        self.assertTrue(os.path.isdir(setupCDSLRepository.cdslRepository1.getDefaultCdslLink()), "Cdsl link %s is no directory" %setupCDSLRepository.cdslRepository1.getDefaultCdslLink())
        for _node in setupCluster.clusterinfo.getNodes():
            self.assertTrue(os.path.isdir(os.path.join(setupCDSLRepository.cdslRepository1.getDefaultCdsltree(), _node.getId())), "Cdsl Nodedir %s is no directory!" %os.path.join(setupCDSLRepository.cdslRepository1.getDefaultCdsltree(), _node.getId()))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
