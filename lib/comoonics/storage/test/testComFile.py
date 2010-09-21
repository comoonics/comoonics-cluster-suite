'''
Created on Sep 8, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):

    def testFileGlobFilename(self):
        import glob
        from comoonics.storage.ComFile import File
        filename="/tmp/*"
        resultfilenames=glob.glob(filename)
        resultelements=File.globFilename(filename, None)
        for resultelement in resultelements:
            filename=resultelement.getAttribute(File.ATTRNAME)
            if not filename in resultfilenames:
                self.assert_("Filename %s does not exist in filenames %s being globbed." %(filename, resultfilenames))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFileGlob']
    unittest.main()