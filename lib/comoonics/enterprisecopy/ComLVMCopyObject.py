""" Comoonics copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComLVMCopyObject.py,v 1.5 2007-04-02 11:49:22 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComLVMCopyObject.py,v $

from ComCopyObject import CopyObject
from comoonics.ComDataObject import DataObject
from comoonics.ComLVM import VolumeGroup, LinuxVolumeManager
from comoonics import ComLog
from comoonics import XmlTools

class LVMCopyObject(CopyObject):
    """ Class for all LVM source and destination objects"""
    __logStrLevel__ = "LVMCopyObject"

    def __init__(self, element, doc):
        CopyObject.__init__(self, element, doc)
        self.vg=None
        vg_element = element.getElementsByTagName(VolumeGroup.TAGNAME)[0]
        self.vg=VolumeGroup(vg_element, doc)

    def prepareAsSource(self):
        self.getVolumeGroup().init_from_disk()
        for pv in LinuxVolumeManager.pvlist(self.getVolumeGroup(), self.getDocument()):
            pv.init_from_disk()
            self.getVolumeGroup().addPhysicalVolume(pv)
        self.activated=False
        for lv in LinuxVolumeManager.lvlist(self.getVolumeGroup(), self.getDocument()):
            lv.init_from_disk()
            self.getVolumeGroup().addLogicalVolume(lv)
            if lv.isActivated() and not self.activated:
                self.activated=True
                self.vg.activate()

    def updateMetaData(self, element):
        ComLog.getLogger(self.__logStrLevel__).debug("%u logical volumes cloning all from source" %(len(self.getVolumeGroup().getLogicalVolumes())))
        #ComLog.getLogger(self.__logStrLevel__).debug("Element to copy %s" %(element))
        if (len(self.getVolumeGroup().getLogicalVolumes()) == 0):
            #ComLog.getLogger(self.__logStrLevel__).debug("0 logical volumes cloning all from source")
            XmlTools.merge_trees_with_pk(element, self.getVolumeGroup().getElement(), self.document, "name", XmlTools.ElementFilter("logicalvolume"))
            self.vg=VolumeGroup(self.getVolumeGroup().getElement(), self.getDocument())
            #self.getVolumeGroup().updateChildrenWithPK(element)
            #from xml.dom.ext import PrettyPrint
            #PrettyPrint(self.getVolumeGroup().getElement())
            #ComLog.getLogger(self.__logStrLevel__).debug("Successfully updated the dom structure for volumegroup")

    def cleanupSource(self):
        pass

    def cleanupDest(self):
        self.cleanupSource()
        if self.activated:
            self.vg.deactivate()

    def prepareAsDest(self):
        pass

    def getVolumeGroup(self):
        return self.vg

    def getMetaData(self):
        return self.vg.getElement()

def main():
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
    print "Testing updateMetData"
    ComSystem.__EXEC_REALLY_DO=""

    reader = Sax2.Reader(validate=0)
    sourcedoc=reader.fromString(sourcexml)
    destdoc=reader.fromString(destxml)
    source=CopyObject(sourcedoc.documentElement, sourcedoc)
    dest=CopyObject(destdoc.documentElement, destdoc)
    print "Source: %s" %(source)
    print "Dest: %s" %(dest)
    dest.updateMetaData(source.getMetaData())
    print "Updating MetaData..."
    PrettyPrint(dest.getElement())

if __name__ == '__main__':
    main()



#################
# $Log: ComLVMCopyObject.py,v $
# Revision 1.5  2007-04-02 11:49:22  marc
# MMG Backup Legato Integration:
# - Journaling for vg_activation
#
# Revision 1.4  2006/12/13 20:17:41  marc
# Support for Metadata
#
# Revision 1.3  2006/11/27 12:11:09  marc
# new version with metadata
#
# Revision 1.2  2006/11/23 14:16:16  marc
# added logStrLevel
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/29 13:47:39  marc
# initial revision
#