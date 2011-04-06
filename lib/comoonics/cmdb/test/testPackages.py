'''
Created on 28.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.Packages import Packages, Package

class Test(unittest.TestCase):


    def setUp(self):
        self.sources=["localhost", "localhost1"]
        Package.DEFAULT_HASHLEVEL=4
        self.packages=Packages(self.sources)
        self.testpackage=Package("kernel", "2.6.18", "164.el5", "x86_64", ["localhost"], self.sources)
        self.testpackage2=Package("kernel", "2.6.18", "164.el5", "x86_64", ["localhost1"], self.sources)
        self.testpackage3=Package("kernel-devel", "2.6.18", "164.el5", "x86_64", ["localhost"], self.sources)
        self.testpackage4=Package("kernel-devel", "2.6.18", "164.el5", "i686", ["localhost1"], self.sources)
        self.testpackage5=Package("kernel-debuginfo", "2.6.18", "164.el5", "x86_64", ["localhost"], self.sources)
        self.testpackage6=Package("kernel-debuginfo", "2.6.18", "194.el5", "x86_64", ["localhost1"], self.sources)

    def tearDown(self):
        pass

#    def testaddPackages(self):
#        self.packages.add(self.testpackage)
#        self.packages.add(self.testpackage2)
#        self.packages.add(self.testpackage3)
#        self.packages.add(self.testpackage4)
#        self.packages.add(self.testpackage5)
#        self.packages.add(self.testpackage6)
#        print self.testpackage.__repr__()
#        print self.testpackage2.__repr__()
#        print self.testpackage3.__repr__()
#        print self.testpackage4.__repr__()
#        print self.testpackage5.__repr__()
#        print self.testpackage6.__repr__()
#        keys=self.packages.packages.keys()
#        keys.sort()
#        retkeys=[hash("kernel-develi686"), hash("kernelx86_642.6.18164.el5"), hash("kernel-develx86_64"), hash("kernel-debuginfox86_642.6.18164.el5"), hash("kernel-debuginfox86_642.6.18194.el5")]
#        retkeys.sort()
#        print keys
#        print retkeys
#        print self.packages
#        self.assertEquals(keys, retkeys)

    def testaddPackage1(self):
        self.packages.add(self.testpackage)
        self.assertTrue(self.testpackage in self.packages, "Could not add package %s to packages %s" %(self.testpackage, self.packages))
        
    def testaddPackage2(self):
        self.packages.add(self.testpackage2)
        self.assertTrue(self.testpackage2 in self.packages, "Could not add package %s to packages %s" %(self.testpackage2, self.packages))
        
    def testContains1(self):
        self.packages.add(self.testpackage)
        self.failUnless(self.testpackage in self.packages, "%s in %s" %(self.testpackage.__repr__(), self.packages))
        self.failUnless(not self.testpackage2 in self.packages, "%s not in %s" %(self.testpackage2.__repr__(), self.packages))
        self.failUnless(not self.testpackage3 in self.packages, "%s not in %s" %(self.testpackage3.__repr__(), self.packages))

    def testContains2(self):
        self.packages.add(self.testpackage)
        self.packages.add(self.testpackage2)
        self.failUnless(self.testpackage in self.packages, "%s in %s" %(self.testpackage.__repr__(), self.packages))
        self.failUnless(self.packages[self.testpackage2] in self.packages, "%s in %s" %(self.testpackage2.__repr__(), self.packages))
        self.failUnless(not self.testpackage3 in self.packages, "%s not in %s" %(self.testpackage3.__repr__(), self.packages))

    def testContains3(self):
        self.packages.add(self.testpackage)
        self.packages.add(self.testpackage3)
        self.failUnless(self.testpackage in self.packages, "%s in %s" %(self.testpackage.__repr__(), self.packages))
        self.failUnless(not self.testpackage2 in self.packages, "%s not in %s" %(self.testpackage2.__repr__(), self.packages))
        self.failUnless(self.testpackage3 in self.packages, "%s in %s" %(self.testpackage3.__repr__(), self.packages))

    def testremove1(self):
        self.packages.add(self.testpackage)
        self.packages.remove(self.testpackage)
        self.assertFalse(self.testpackage in self.packages, "%s should not be part of packages." %self.testpackage.__repr__())
        
    def testremove2(self):
        self.packages.add(self.testpackage.copy())
        self.packages.add(self.testpackage2.copy())
        self.packages.remove(self.testpackage)
        self.assertFalse(self.testpackage in self.packages, "%s should not be part of packages: %s." %(self.testpackage.__repr__(), self.packages))
        self.assertTrue(self.testpackage2 in self.packages, "%s should be part of packages, packages: %s." %(self.testpackage2.__repr__(), self.packages))
        
    def testremove3(self):
        self.packages.add(self.testpackage.copy())
        self.packages.add(self.testpackage2.copy())
        del self.packages[self.testpackage]
        self.assertFalse(self.testpackage in self.packages, "%s should not be part of packages: %s." %(self.testpackage.__repr__(), self.packages))
        self.assertTrue(self.testpackage2 in self.packages, "%s should be part of packages, packages: %s." %(self.testpackage2.__repr__(), self.packages))

    def testiterrange(self):
        self.packages.add(self.testpackage)
        self.packages.add(self.testpackage2)
        self.packages.add(self.testpackage3)
        self.packages.add(self.testpackage4)
        self.packages.add(self.testpackage5)
        self.packages.add(self.testpackage6)
        self.assertEquals(list(self.packages.iterrange(0, 2)), 
                          [Package(name="kernel-debuginfo", architecture="x86_64", version="2.6.18", subversion="194.el5",
                                   sources=['localhost1'], allsources=['localhost', 'localhost1'], hashlevel=4, 
                                   index=4), 
                           Package(name="kernel-devel", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                   sources=['localhost'], allsources=['localhost', 'localhost1'], hashlevel=4, index=1)])
        self.assertEquals(list(self.packages.iterrange(4, 6)), 
                          [Package(name="kernel-debuginfo", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                   sources=['localhost'], allsources=['localhost', 'localhost1'], hashlevel=4, index=3)])
        #print list(self.packages.iterrange(2, 4))
        self.assertEquals(list(self.packages.iterrange(2, 4)),
                           [Package(name="kernel", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                    sources=['localhost', 'localhost1'], allsources=['localhost', 'localhost1'], 
                                    hashlevel=4, index=0), 
                            Package(name="kernel-devel", architecture="i686", version="2.6.18", subversion="164.el5", 
                                    sources=['localhost1'], allsources=['localhost', 'localhost1'], 
                                    hashlevel=4, index=2)])
    def testiterrange2(self):
        self.packages.add(self.testpackage)
        self.packages.add(self.testpackage2)
        self.packages.add(self.testpackage3)
        self.packages.add(self.testpackage4)
        self.packages.add(self.testpackage5)
        self.packages.add(self.testpackage6)
        self.assertEquals(list(self.packages.iterrange(0, 2, self.packages.sort)), 
                          [Package(name="kernel-debuginfo", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                   sources=['localhost'], allsources=['localhost', 'localhost1'], hashlevel=4, index=3), 
                           Package(name="kernel-debuginfo", architecture="x86_64", version="2.6.18", subversion="194.el5", 
                                   sources=['localhost1'], allsources=['localhost', 'localhost1'], hashlevel=4, index=4)])
        self.assertEquals(list(self.packages.iterrange(4, 6)), 
                          [Package(name="kernel-debuginfo", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                   sources=['localhost'], allsources=['localhost', 'localhost1'], hashlevel=4, index=3)])
        #print list(self.packages.iterrange(2, 4))
        self.assertEquals(list(self.packages.iterrange(2, 4)),
                           [Package(name="kernel", architecture="x86_64", version="2.6.18", subversion="164.el5", 
                                    sources=['localhost', 'localhost1'], allsources=['localhost', 'localhost1'], 
                                    hashlevel=4, index=0), 
                            Package(name="kernel-devel", architecture="i686", version="2.6.18", subversion="164.el5", 
                                    sources=['localhost1'], allsources=['localhost', 'localhost1'], hashlevel=4, index=2)])
        
    def testsort(self):
        self.packages.add(self.testpackage)
        self.packages.add(self.testpackage2)
        self.packages.add(self.testpackage3)
        self.packages.add(self.testpackage4)
        self.packages.add(self.testpackage5)
        self.packages.add(self.testpackage6)
        print map(lambda pkg: pkg.hashstring(), self.packages.sort())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()