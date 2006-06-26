import xml.dom
from xml.dom.ext import PrettyPrint

from exceptions import NameError

import sys
import traceback
import copy
from xml.xpath          import Compile
from xml.xpath.Context  import Context

sys.path.append("../lib")

import ComLVM

doc = xml.dom.getDOMImplementation().createDocument(None,None,None)
cs = doc.createElement('copyset')
dest = doc.createElement('destination')
dest.setAttribute('type', 'filecopy')
cs.appendChild(dest)
lvm = doc.createElement('volume_management')
vg = doc.createElement('volume_group')
vg.setAttribute('name', 'vg1')
lv1 = doc.createElement('logical_volume')
lv1.setAttribute('name', 'lv1')
lv1.setAttribute('size', '100M')
lv2 = doc.createElement('logical_volume')
lv2.setAttribute('name', 'lv2')
lv2.setAttribute('size', '200M')
pv1 = doc.createElement('physical_volume')
pv1.setAttribute('name', 'pv1')
pv1.setAttribute('path', '/dev/sdc')
pv2 = doc.createElement('physical_volume')
pv2.setAttribute('name', 'pv2')
pv2.setAttribute('path', '/dev/sda1')
vg.appendChild(lv1)
vg.appendChild(lv2)
vg.appendChild(pv1)
vg.appendChild(pv2)
lvm.appendChild(vg)
dest.appendChild(lvm)


device = doc.createElement('device')
# device.setAttribute('type', 'lvm')
device.setAttribute('path', '/dev/vg1/lv1')


dest.appendChild(device)
fs = doc.createElement('filesystem')
fs.setAttribute('type', 'gfs')
node = doc.createElement('fs_config')
node.setAttribute('bsize', '4096')
node.setAttribute('journals', '8')
node.setAttribute('clustername', 'mycluster')
node.setAttribute('locktable', 'mylocktable')
node.setAttribute('lockproto', 'lock_dlm')
fs.appendChild(node)
device.appendChild(fs)

doc.appendChild(cs)
expression = Compile("copyset/destination/volume_management/volume_group")
context = Context(doc)
nodes = expression.evaluate(context)
print "TagName of volume group: "+ nodes[0].tagName
vg=ComLVM.VolumeGroup(nodes[0])
vg.size='10G'
try:
    print "VGSCAN: "
    vg.vgscan()
except RuntimeError, re:
    print re
    
try:
    print "VGACTIVATE: "
    vg.vgactivate()
except RuntimeError, re:
    print re
try:
    print "VGDEACTIVATE: "
    vg.vgdeactivate()
except RuntimeError, re:
    print re
    
print "Name of volume group: ", vg.name
print "Size of volume group: ", vg.size
try:
    print "Uninitialized value of \"xtf\": ", vg.xtf
except NameError, ne: 
    print "Error: ", ne

for lv in vg.getLogicalVolumes():
    print "Name of logical volume: ", lv.name
    
for pv in vg.getPhysicalVolumes():
    print "Name of logical volume: ", pv.name

print "Copying vg "+vg.name+" to new group "
newvg=copy.copy(vg)
print "Newvg name. "+newvg.name
newvg.name="newvg"
print "VG Name: "+vg.name+" newvg name: "+newvg.name
    
print "XML: "
PrettyPrint(doc)
