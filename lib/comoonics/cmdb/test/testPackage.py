'''
Created on 28.03.2011

@author: marc
'''
import unittest
from comoonics.cmdb.Packages import Package
Package.DEFAULT_HASHLEVEL=4

class Test(unittest.TestCase):

    def setUp(self):
        self.sources=["localhost", "localhost123"]
        self.package=Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="x86_64")
        self.package.allsources=self.sources
        self.package.addsource("localhost")

    def tearDown(self):
        pass

    def testhash(self):
        #print hash(self.package)
        self.assertEquals(hash(self.package), hash("kernelx86_642.6.18164-el5"))

    def testEquals(self):
        self.assertEquals(self.package, Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="x86_64", allsources=self.sources, sources=["localhost123"]))

    def testNotEquals1(self):
        self.assertNotEquals(self.package, Package(name="kernel-devel", version="2.6.18", subversion="164-el5", architecture="x86_64", allsources=self.sources, sources=["localhost123"]))
    def testNotEquals2(self):
        self.assertNotEquals(self.package, Package(name="kernel", version="2.6.18", subversion="194-el5", architecture="x86_64", allsources=self.sources, sources=["localhost123"]))
    def testNotEquals3(self):
        self.assertNotEquals(self.package, Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="i386", allsources=self.sources, sources=["localhost123"]))

    def testDeepCmp(self):
        self.assertEquals(self.package.cmp(Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="x86_64", allsources=self.sources, sources=["localhost"]), True), 0)

    def testNotDeepCmp1(self):
        package=Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="x86_64", sources=["localhost123"], allsources=self.sources)
        self.assertEquals(self.package.cmp(package, True), -1)
    def testNotDeepCmp2(self):
        self.assertEquals(self.package.cmp(Package(name="kernel", version="2.6.18", subversion="194-el5", architecture="x86_64", allsources=self.sources, sources=["localhost"]), True), -1)
    def testNotDeepCmp3(self):
        self.assertEquals(self.package.cmp(Package(name="kernel", version="2.6.18", subversion="164-el5", architecture="i386", allsources=self.sources, sources=["localhost123"]), True), 1)
        
    def testToString(self):
        self.assertEquals(str(self.package), "kernel-2.6.18-164-el5.x86_64")
    def testRepr(self):
        self.assertEquals(self.package.__repr__(), 'Package(name="kernel", architecture="x86_64", version="2.6.18", subversion="164-el5", sources=[\'localhost\'], allsources=[\'localhost\', \'localhost123\'], hashlevel=4, index=0)')
        
    def testCopy(self):
        package=self.package.copy()
        self.assertEquals(self.package, package)
        package.addsource("localhost1")
        self.assertEquals(self.package, package)
        self.assertNotEquals(self.package.sources, package.sources)
        
    def testAddSource1(self):
        self.package.addsource("localhost123")
        self.assertEquals(self.package.resolvesources(), self.sources, "Sources from package %s != sources %s" %(self.package.resolvesources(), self.sources))
        
    def testAddSource2(self):
        self.package.addsource("localhost1")
        self.assertEquals(self.package.resolvesources(), ["localhost", "localhost1"], "Sources from package %s != sources %s" %(self.package.resolvesources(), self.sources))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetName']
    unittest.main()