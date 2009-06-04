'''
Created on Apr 28, 2009

@author: marc
'''
import unittest
import setup

setupCluster=setup.SetupCluster()        
setupCDSLRepository=setup.SetupCDSLRepository()  
setupCdsls=setup.SetupCDSLs(setupCDSLRepository.cdslRepository2)

class test_Cdsl(unittest.TestCase):
    def test_A_CdslsCreate(self):
        from comoonics.cdsl.ComCdsl import Cdsl
        for _cdsl in setupCDSLRepository.cdslRepository2.cdsls:
            print "%s\n" %_cdsl.src
            _cdsl = Cdsl(_cdsl.src, _cdsl.type, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo, None, None, setup.tmppath)
            _cdsl.commit(force=True)
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist!" %(_cdsl.type, _cdsl))

    def test_B_CdslsValidate(self):
        from comoonics.cdsl.ComCdslValidate import cdslValidate
        _added, _removed=cdslValidate(setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo, False, setup.tmppath)
        self.assertTrue(len(_added)==0 and len(_removed)==0, "Cdslsearch didn't succeed. Added %s, Removed %s" %(_added, _removed))
        _cdsls=setupCDSLRepository.cdslRepository1.getCdsls()
        _removed_cdsl=setupCDSLRepository.cdslRepository1.delete(_cdsls[-1])
        _added, _removed=cdslValidate(setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo, False, setup.tmppath)
        self.assertEquals(_added[0].src, _removed_cdsl.src, "The removed cdsl %s is different from the added one %s" %(_added[0].src, _removed_cdsl.src))

    def test_Z_CdslsDelete(self):
        _cdslsrev=list()
        _cdslsrev.extend(setupCDSLRepository.cdslRepository1.getCdsls())
        _cdslsrev.reverse()
        for _cdsl in _cdslsrev:
            print "%s\n" %_cdsl.src
            _cdsl.delete(True, True, setup.tmppath)
            self.assertFalse(_cdsl.exists(), "%s CDSL %s exists although it was removed before." %(_cdsl.type, _cdsl))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
    setupCdsls.setupCDSLInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1)
    unittest.main()
    setupCdsls.cleanUpInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
    setupCDSLRepository.cleanUpInfrastructure(setup.tmppath)
