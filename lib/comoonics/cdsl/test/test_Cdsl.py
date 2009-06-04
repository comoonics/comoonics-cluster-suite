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
    def testCdslsCreate(self):
        from comoonics.cdsl.ComCdsl import Cdsl
        for _cdsl in setupCDSLRepository.cdslRepository2.cdsls:
            print "%s\n" %_cdsl.src
            _cdsl = Cdsl(_cdsl.src, _cdsl.type, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo, None, None, setup.tmppath)
            _cdsl.commit(force=True)
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist!" %(_cdsl.type, _cdsl))

    def testCdslsDelete(self):
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
