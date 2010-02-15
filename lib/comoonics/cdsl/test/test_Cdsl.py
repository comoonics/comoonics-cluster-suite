'''
Created on Apr 28, 2009

@author: marc
'''
import sys
sys.path.append('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])
import unittest
import setup

class test_Cdsl(unittest.TestCase):
    def test_A_CdslDestPaths(self):
        for cdsl in repository.getCdsls():
            dp1=cdsl.getDestPaths()
            dp2=setupCdsls.results[cdsl.src][3]
            self.assertEquals(dp1, dp2, "Destinationpaths for cdsl %s are not equal: %s != %s" %(cdsl.src, dp1, dp2))
#            print "destpaths(%s): %s" %(cdsl, cdsl.getDestPaths())

    def test_B_CdslSourcePaths(self):
        for cdsl in repository.getCdsls():
            sp1=cdsl.getSourcePaths()
            sp2=setupCdsls.results[cdsl.src][2]
            self.assertEquals(sp1, sp2, "Sourcepaths for cdsl %s are not equal: %s != %s" %(cdsl.src, sp1, sp2))
#            print "sourcepaths(%s): %s" %(cdsl, cdsl.getSourcePaths())    
            
#    def test_C_CdslSubPaths(self):
#        for cdsl in repository.getCdsls():
#            sp1=cdsl._getSubPathsToParent()
#            sp2=setupCdsls.results[cdsl.src][4]
#            self.assertEquals(sp1, sp2, "SubPaths2Parent for cdsl %s are not equal: %s != %s" %(cdsl.src, sp1, sp2))
#            print "Subpaths2parent(%s): %s" %(cdsl, cdsl._getSubPathsToParent())
#
    def test_D_getChilds(self):
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        try:
            cdsl = repository.getCdsl("hd/sd")
            resultchilds= [ "hd/sd/hd",
                            "hd/sd/hf" ]
            for child in cdsl.getChilds():
                self.assertTrue(child.src in resultchilds, "Could not find child cdsl %s for parent cdsl %s." %(cdsl, child))
        except CdslNotFoundException:
            self.assert_("Could not find cdsl under \"hd/sd\".")

    def test_E_CdslsCreate(self):
        from comoonics.cdsl import cmpbysubdirs
        _cdsls=repository.getCdsls()
        _cdsls.sort(cmpbysubdirs)
        for _cdsl in _cdsls:
#            print "+ %s\n" %_cdsl
            _cdsl.commit(force=True)
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist!" %(_cdsl.type, _cdsl))

    def test_F_CdslsValidate(self):
        from comoonics.cdsl.ComCdslValidate import CdslValidate
        validate=CdslValidate(repository, setupCluster.clusterinfo)
        _added, _removed=validate.validate(onfilesystem=False, update=False, root=setup.tmppath)
#        print "Validate.."
        self.assertTrue(len(_added)==0 and len(_removed)==0, "Cdslsearch didn't succeed. Added %s, Removed %s" %(_added, _removed))
#        print "Ok\n"
        _cdsls=repository.getCdsls()
#        print "-%s" %_cdsls[-1]
        _removed_cdsl=repository.delete(_cdsls[-1])
        _added, _removed=validate.validate(onfilesystem=True, update=True, root=setup.tmppath)
        self.assertEquals(_added[0].src, _removed_cdsl.src, "The removed cdsl %s is different from the added one %s" %(_added[0].src, _removed_cdsl.src))
#        print "+%s" %_added[0].src

#    def test_CdslOfSameType(self):
#        from comoonics.cdsl.ComCdsl import CdslOfSameType, Cdsl
#        
#        self.assertRaises(CdslOfSameType, Cdsl, "hd/hd", Cdsl.SHARED_TYPE, repository, setupCluster.clusterinfo)
    
    def test_Y_CdslsDeleteNoForce(self):
        import shutil
        from comoonics.cdsl import cmpbysubdirs
        _cdslsrev=repository.getCdsls()
        _cdslsrev.sort(cmpbysubdirs)
        _cdslsrev.reverse()
        for _cdsl in _cdslsrev:
#            print "- %s\n" %_cdsl.src
            _cdsl.delete(True, False)
            _files2remove=list()
            if _cdsl.isHostdependent():
                for nodeid in setupCluster.clusterinfo.getNodeIdentifiers('id'):
                    _file="%s.%s" %(_cdsl.src, nodeid)
                    _files2remove.append(_file)
                _files2remove.append("%s.%s" %(_cdsl.src, "orig"))
            setupCdsls.repository.workingdir.pushd()
            if _cdsl.isHostdependent():
                shutil.move("%s.%s" %(_cdsl.src, "default"), _cdsl.src)
            setupCdsls.repository.workingdir.popd()
            _cdsl.commit()
            setupCdsls.repository.workingdir.pushd()
            for _file in _files2remove:
#                print "- %s" %_file
                if os.path.isdir(_file):
                    shutil.rmtree(_file)
#                    os.removedirs(_file)
                else:
                    os.remove(_file)
            setupCdsls.repository.workingdir.popd()
            self.assertTrue(_cdsl.exists(), "%s CDSL %s does not exist although it was created before." %(_cdsl.type, _cdsl))
            for __cdsl in setupCdsls.repository.getCdsls():
                self.assertTrue(__cdsl.exists(), "The still existant %s cdsl %s does not exist any more." %(__cdsl.type, __cdsl))

    def test_Z_CdslsDelete(self):
        from comoonics.cdsl import cmpbysubdirs
        _cdslsrev=repository.getCdsls()
        _cdslsrev.sort(cmpbysubdirs)
        _cdslsrev.reverse()
        for _cdsl in _cdslsrev:
            print "- %s\n" %_cdsl.src
            setupCdsls.repository.workingdir.pushd()
            _cdsl.delete(True, True)
            self.assertFalse(_cdsl.exists(), "%s CDSL %s exists although it was removed before." %(_cdsl.type, _cdsl))
            for __cdsl in  repository.getCdsls():
                self.assertTrue(__cdsl.exists(), "The still existant %s cdsl %s does not exist any more." %(__cdsl.type, __cdsl))
            setupCdsls.repository.workingdir.popd()

if __name__ == "__main__":
    from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
    import os
    #import sys;sys.argv = ['', 'Test.testName']
    setupCluster=setup.SetupCluster()        
    repository=ComoonicsCdslRepository(clusterinfo=setupCluster.clusterinfo, root=setup.tmppath, usenodeids="True")  
    setupCdsls=setup.SetupCDSLs(repository)
    repository.buildInfrastructure(setupCluster.clusterinfo)
    setupCdsls.setupCDSLInfrastructure(setup.tmppath, repository, setupCluster.clusterinfo)
    module=setup.MyTestProgram(module=test_Cdsl(methodName='run'))
    if module.result.wasSuccessful():
        setupCdsls.cleanUpInfrastructure(setup.tmppath, repository, setupCluster.clusterinfo)
        setup.cleanup()
    sys.exit(not module.result.wasSuccessful())    
