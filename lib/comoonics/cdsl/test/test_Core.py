import unittest
import setup

setupCluster=setup.SetupCluster()        
setupCDSLRepository=setup.SetupCDSLRepository()  

class test_0CoreFunctions(unittest.TestCase):
    def testguessType(self):
        from comoonics.cdsl import guessType
        from comoonics.cdsl.ComCdsl import Cdsl
        _resultpairs=[ [ "unknown", Cdsl.UNKNOWN_TYPE ],
                       [ "hostdependent_dir/shared_dir", Cdsl.SHARED_TYPE ],
                       [ "hostdependent_dir/shared_dir/test123", Cdsl.HOSTDEPENDENT_TYPE ],
                       [ "cluster/shared/hostdependent/shared", Cdsl.HOSTDEPENDENT_TYPE ],
                       [ "cluster/cdsl/1/hostdependent/shared", Cdsl.SHARED_TYPE ],
                       [ "cdsl.local/hostdependent/shared", Cdsl.SHARED_TYPE ] ]
        for _tmp in _resultpairs:
            _result=guessType(_tmp[0], setupCDSLRepository.cdslRepository2, False)
            self.assertEquals(_result, _tmp[1], "guessType(%s): %s != %s." %(_tmp[0], _result, _tmp[1]))
        
    def testisSharedPath(self):
        from comoonics.cdsl import isSharedPath
        _resultpairs=[ [ "hostdependent/shared", False ],
                       [ "cluster/shared/hostdependent/shared", True ],
                       [ "cluster/cdsl/1/hostdependent/shared", False ],
                       [ "cdsl.local/hostdependent/shared", False ] ]
        for _tmp in _resultpairs:
            _result=isSharedPath(_tmp[0], setupCDSLRepository.cdslRepository1, False)
            self.assertEquals(_result, _tmp[1], "%s isSharedPath != %s." %(_tmp[0], _tmp[1]))

    def testisHostdependentPath(self):
        from comoonics.cdsl import isHostdependentPath
        _resultpairs=[ [ "hostdependent/shared", False ],
                       [ "cluster/shared/hostdependent/shared", False ],
                       [ "cluster/cdsl/1/hostdependent/shared", True ],
                       [ "cdsl.local/hostdependent/shared", True ] ]
        for _tmp in _resultpairs:
            _result=isHostdependentPath(_tmp[0], setupCDSLRepository.cdslRepository1, False)
            self.assertEquals(_result, _tmp[1], "%s isHostdependentPath != %s." %(_tmp[0], _tmp[1]))

    def test0Ltimdir(self):
        from comoonics.cdsl import ltrimDir
        _resultpairs=[ [ "../../../../cluster/shared/hostdependent/shared", "cluster/shared/hostdependent/shared" ],
                      [ "/../../../../cluster/shared/hostdependent/shared", "/../../../../cluster/shared/hostdependent/shared" ] ]
        for _tmp in _resultpairs:
            self.assertEquals(ltrimDir(_tmp[0]), _tmp[1], "ltrimDir(%s) == %s" %(_tmp[0], _tmp[1]))
                
    def test0isSubPath(self):
        from comoonics.cdsl import isSubPath
        _resulttriples=[ [ "../../../../cluster/shared/hostdependent/shared", "shared", True ],
                         [ "../../../../cluster/shared/hostdependent/shared", "cluster", True ],
                         [ "../../../../cluster/shared/hostdependent/shared", "..", True ],
                         [ "../../../../cluster/shared/hostdependent/shared", "cluster/shared", True ],
                         [ "../../../../cluster/shared/hostdependent/shared", "xyz", False ], 
                         [ "/../../../../cluster/shared/hostdependent/shared", "shared", True ],
                         [ "/../../../../cluster/shared/hostdependent/shared", "cluster", True ],
                         [ "/../../../../cluster/shared/hostdependent/shared", "..", True ],
                         [ "/../../../../cluster/shared/hostdependent/shared", "cluster/shared", True ],
                         [ "/../../../../cluster/shared/hostdependent/shared", "xyz", False ],
                         [ "cdsl.local/hostdependent/shared", "cdsl.local", True] ]
        for _tmp in _resulttriples:
            self.assertEquals(isSubPath(_tmp[0], _tmp[1]), _tmp[2], "isSubPath(%s, %s) == %s" %(_tmp[0], _tmp[1], _tmp[2])) 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
