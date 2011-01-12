'''
Created on May 21, 2010

@author: marc
'''
import unittest
from comoonics.ComPath import Path
import tempfile
import os
import os.path

class Test(unittest.TestCase):
    dirs= [ "test", "test/test", "test/test2" ]
    tmpdir=os.path.realpath(tempfile.mkdtemp())
    
    def setUp(self):
        self.revdirs=list(self.dirs)
        self.revdirs.reverse()
        for _dir in self.dirs:
            os.mkdir(os.path.join(self.tmpdir, _dir)) 

    def tearDown(self):
        for _dir in self.revdirs:
            os.rmdir(os.path.join(self.tmpdir, _dir))
        os.rmdir(self.tmpdir)
#        os.removedirs(self.tmpdir)


    def testPushPopD(self):
        oldcwd=os.getcwd()
        path=Path()
        self.assertEquals(path.getPath(), oldcwd, "Currentpath %s does not equals Path currentpath %s." %(path, oldcwd))
        path.pushd(self.tmpdir)
        self.assertEquals(os.path.realpath(path.getPath()), self.tmpdir, "Currentpath %s does not equals Path currentpath %s." %(path, self.tmpdir))
        for _dir in self.dirs:
            olddir=path.getPath()
            print "%s <==> %s" %(olddir, _dir)
            path.pushd(_dir)
            self.assertEquals(path.getPath(), _dir, "Currentpath %s does not equals Path currentpath %s." %(path, _dir))
            _dir2=path.popd()
            self.assertEquals(_dir2, olddir, "Currentpath %s does not equals Path currentpath %s." %(_dir2, olddir))
        _dir2=path.popd()
        self.assertEquals(_dir2, oldcwd , "Currentpath %s does not equals Path currentpath %s." %(_dir2, oldcwd))
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()