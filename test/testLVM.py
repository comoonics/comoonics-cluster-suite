import xml.dom
from xml.dom.ext import PrettyPrint

from exceptions import NameError

import sys
import traceback
from exceptions import Exception
import copy
from xml.xpath          import Compile
from xml.xpath.Context  import Context

sys.path.append("../lib")

import ComLVM
import ComSystem
import ComLog

ComSystem.__EXEC_REALLY_DO=""

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

doc=xml.dom.getDOMImplementation().createDocument(None, None, None)

vgname="vg1"
if len(sys.argv) > 1:
    vgname=sys.argv[1]

lvname=None
if len(sys.argv) > 2:
    lvname=sys.argv[2]
    
pvname=None
if len(sys.argv) > 3:
    pvname=sys.argv[3]

nvgname=None
if len(sys.argv) > 4:
    nvgname=sys.argv[4]

line("init and pre")

vgs=[]

try:
    vgs=ComLVM.LinuxVolumeManager.vglist(doc)
except RuntimeError, re:
    print re

line ("__str__")

for _vg in vgs:
    print "Volume group: "
    print _vg
    for lv in _vg.getLogicalVolumes():
        print "Logical volume: ", lv
    
    for pv in _vg.getPhysicalVolumes():
        print "Physical volume: ", pv

line("XML/DOM")
for _vg in vgs:
    doc.appendChild(_vg.getElement())
    PrettyPrint(doc)
    doc.removeChild(_vg.getElement())

vg=vgs[0]
for _vg in vgs:
    if _vg.getAttribute("name") == vgname:
        vg=_vg
   
line("helperfunctions")

print "ComLVM.LinuxVolumeManager.getPossiblePhysicalExtends()"
try:
    print ComLVM.LinuxVolumeManager.getPossiblePhysicalExtents()
except Exception, e:
    print "Error: getPossiblePhysicalExtends", e

print "ComLVM.LinuxVolumeManager.clampLVSizeRequest(500, 4096)"
try:
    print ComLVM.LinuxVolumeManager.clampLVSizeRequest(500, 4096)
except Exception, e:
    print "Error: clampLVSizeRequest", e

print "ComLVM.LinuxVolumeManager.clampPVSize(500, 4096)"
try:
    print ComLVM.LinuxVolumeManager.clampPVSize(500, 4096)
except Exception, e:
    print "Error: clampPVSize", e

line("LVM Funtionality")

try:
    print "ComLVM.has_lvm()"
    ComLVM.LinuxVolumeManager.has_lvm()
except RuntimeError, re:
    print re
    
try:
    print "VGSCAN: "
    ComLVM.VolumeGroup.scan()
except RuntimeError, re:
    print re
    
try:
    print "VGACTIVATE: "
    vg.activate()
except RuntimeError, re:
    print re
try:
    print "VGDEACTIVATE: "
    vg.deactivate()
except RuntimeError, re:
    print re

if lvname:
    print "creating "+lvname+" on all vgs with free space"
    for _vg in vgs:
        ComLog.getLogger().debug("vg %s free %s" % (_vg.getAttribute("name"), _vg.getAttribute("free")))
        if int(_vg.getAttribute("free")) > 0:
            lv=ComLVM.LogicalVolume(lvname, _vg, doc)
            print "Creating logical volume "+_vg.getAttribute("name")+"/"+lv.getAttribute("name")
            lv.create()
            print "Removing logical volume "+_vg.getAttribute("name")+"/"+lv.getAttribute("name")
            lv.remove()

if pvname and nvgname and lvname:
    print "creating "+nvgname+" on given pvname "+pvname
    vg=ComLVM.VolumeGroup(nvgname, doc)
    pv=ComLVM.PhysicalVolume(pvname, vg, doc)
    lv=ComLVM.LogicalVolume(lvname, vg, doc)
    vg.addPhysicalVolume(pv)
    vg.addLogicalVolume(lv)
    print "Creating physical volume "+pv.getAttribute("name")
    pv.create()
    print "Creating volume group "+vg.getAttribute("name")
    vg.create()
    print "Creating logical volume "+vg.getAttribute("name")+"/"+lv.getAttribute("name")
    lv.create()
    print "Removing logical volume "+vg.getAttribute("name")+"/"+lv.getAttribute("name")
    lv.remove()
    print "Removing volume group "+vg.getAttribute("name")
    vg.remove()
    print "Creating physical volume "+pv.getAttribute("name")
    pv.remove()

line("Byebye")

###############
# $Log: testLVM.py,v $
# Revision 1.2  2006-06-28 17:27:41  marc
# first version
#