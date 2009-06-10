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
        from comoonics.cdsl import cmpbysubdirs
        from comoonics.cdsl.ComCdsl import Cdsl
        _cdsls=setupCDSLRepository.cdslRepository2.getCdsls()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
            print "+ %s\n" %_cdsl.src
            _cdsl = Cdsl(_cdsl.src, _cdsl.type, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo, None, None)
            _cdsl.commit(force=True)
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist!" %(_cdsl.type, _cdsl))

    def test_B_CdslsValidate(self):
        from comoonics.cdsl.ComCdslValidate import CdslValidate
        validate=CdslValidate(setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
        _added, _removed=validate.validate(onfilesystem=False, update=False, root=setup.tmppath)
        print "Validate.."
        self.assertTrue(len(_added)==0 and len(_removed)==0, "Cdslsearch didn't succeed. Added %s, Removed %s" %(_added, _removed))
        print "Ok\n"
        _cdsls=setupCDSLRepository.cdslRepository1.getCdsls()
        print "-%s" %_cdsls[-1]
        _removed_cdsl=setupCDSLRepository.cdslRepository1.delete(_cdsls[-1])
        _added, _removed=validate.validate(onfilesystem=True, update=True, root=setup.tmppath)
        self.assertEquals(_added[0].src, _removed_cdsl.src, "The removed cdsl %s is different from the added one %s" %(_added[0].src, _removed_cdsl.src))
        print "+%s" %_added[0].src

    def test_C_CdslSubPaths(self):
        for cdsl in setupCDSLRepository.cdslRepository2.getCdsls():
            print "Subpaths2parent(%s): %s" %(cdsl, cdsl._getSubPathsToParent())

    def test_D_CdslDestPaths(self):
        for cdsl in setupCDSLRepository.cdslRepository2.getCdsls():
            print "destpaths(%s): %s" %(cdsl, cdsl.getDestPaths())

    def test_E_CdslSourcePaths(self):
        for cdsl in setupCDSLRepository.cdslRepository2.getCdsls():
            print "sourcepaths(%s): %s" %(cdsl, cdsl.getSourcePaths())

    def test_Z_CdslsDelete(self):
        from comoonics.cdsl import cmpbysubdirs
        _cdslsrev=setupCDSLRepository.cdslRepository1.getCdsls()
        _cdslsrev.sort(cmpbysubdirs)
        _cdslsrev.reverse()
        for _cdsl in _cdslsrev:
            print "- %s\n" %_cdsl.src
            _cdsl.delete(True, True)
            self.assertFalse(_cdsl.exists(), "%s CDSL %s exists although it was removed before." %(_cdsl.type, _cdsl))
            for __cdsl in  setupCDSLRepository.cdslRepository1.getCdsls():
                self.assertTrue(__cdsl.exists(), "The still existant %s cdsl %s does not exist any more." %(__cdsl.type, __cdsl))

# overwrite the I exit if I want unittest.Testprogram
class myTestProgram(unittest.TestProgram):
    def  runTests(self):
        if self.testRunner is None:
            self.testRunner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = self.testRunner.run(self.test)
        self.success= not result.wasSuccessful()

if __name__ == "__main__":
    import os
    import sys
    #import sys;sys.argv = ['', 'Test.testName']
    setupCDSLRepository.cdslRepository1.buildInfrastructure(setupCluster.clusterinfo)
    setupCdsls.setupCDSLInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1)
    prg=myTestProgram()
    setupCdsls.cleanUpInfrastructure(setup.tmppath, setupCDSLRepository.cdslRepository1, setupCluster.clusterinfo)
    setupCDSLRepository.cleanUpInfrastructure(setup.tmppath)
    os.rmdir(setup.tmppath)
    sys.exit(prg.success)
