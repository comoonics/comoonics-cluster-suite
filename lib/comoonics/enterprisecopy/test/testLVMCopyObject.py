'''
Created on Mar 3, 2010

@author: marc
'''
import unittest


class Test(unittest.TestCase):


    def testLVMCopyObject(self):
        from comoonics.enterprisecopy.ComCopyObject import CopyObject
        from xml.dom.ext import PrettyPrint
        from xml.dom.ext.reader import Sax2
        from comoonics import ComSystem
        sourcexml="""
        <source type="lvm">
           <volumegroup name='centos' free='32' numlvs='2' attrs='wz--n-' numpvs='1' serial='0' size='3456'>
              <physicalvolume attr='a-' size='3456' name='/dev/sdf2' free='32' format='lvm2'/>
              <logicalvolume origin='' size='512' name='swap' attrs='-wi-a-'/>
              <logicalvolume origin='' size='2912' name='system' attrs='-wi-a-'/>
           </volumegroup>
       </source>
        """
        destxml="""
        <destination type="lvm">
            <volumegroup name="centos_new">
                <physicalvolume name="/dev/sde"/>
            </volumegroup>
        </destination>
        """
        ComSystem.setExecMode(ComSystem.SIMULATE)
        reader = Sax2.Reader(validate=0)
        sourcedoc=reader.fromString(sourcexml)
        destdoc=reader.fromString(destxml)
        try:
            source=CopyObject(sourcedoc.documentElement, sourcedoc)
            dest=CopyObject(destdoc.documentElement, destdoc)
            dest.updateMetaData(source.getMetaData())
        except Exception, e:
            self.assert_("Could not execute copyobject %s => %s. Exception %s." %(source, dest, e))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()