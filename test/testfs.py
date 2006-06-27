import sys
import traceback
import copy

sys.path.append("../lib")

import ComDevice
import ComUtils
import ComFileSystem
import ComDataObject
from ComFileSystem import *

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath

XML="""<?xml version="1.0" encoding="UTF-8"?>
<businesscopy>
<volume_management>
  <volume_group name="vg1">
  <logical_volume name="lv1" size="100M"/>
  <logical_volume name="lv2" size="200M"/>
  <physical_volume path="/dev/sdc" name="pv1"/>
  <physical_volume path="/dev/sda1" name="pv2"/>
  </volume_group>
</volume_management>
<copyset>
  <source type="filecopy">
    <filesystem type="gfs"/>
    <mountpoint path="/cluster/pool/data"/>
  </source>
  <destination type="filecopy">
    <device path="/dev/vg1/lv1">
      <filesystem bsize="4096" journals="8" clustername="mycluster" lockproto="lock_dlm" locktable="mylocktable" type="gfs"/>
      <mountpoint path="/mnt/tmp">
        <option name="noatime"/>
        <option name="lockproto" value="lock_nolock"/>
      </mountpoint>
    </device>
  </destination>
</copyset>
<bootdisk path="/dev/wasauchimmer" loader="grub"/>
</businesscopy>
"""

## Copier:
## -----------
## getCopier(copyset)
## ComCopierLocalFilecopy(Copier)
## evtl mount
## cp -ax or rsync -a...

# create Reader object
reader = Sax2.Reader()

#parse the document
doc = reader.fromString(XML)

PrettyPrint(doc)

sets = xpath.Evaluate('copyset', doc)
for i in range(len(sets)):
    print sets[i]
    devnode=xpath.Evaluate('destination/device', sets[i])[0]
    dev=ComDevice.Device(devnode, doc)
    print dev
    fsnode=xpath.Evaluate('filesystem', devnode)[0]
    fs=ComFileSystem.getFileSystem(fsnode, doc)
    print fs
    mpnode=xpath.Evaluate('mountpoint', devnode)[0]
    mp=ComFileSystem.MountPoint(mpnode, doc)
    print mp
    fs.formatDevice(dev)
    fs.mount(dev, mp)
    fs.umountDev(dev)
    fs.umountDir(mp)
    

#gfs=ComFileSystem.getFileSystem(fs)
#gfs.formatDevice(dev)
#print gfs.getOptionsString()
#gfs.mount(dev, "/mnt/")
#gfsneu=copy.deepcopy(gfs) 
#fs.labelDevice("neueslabel", device)
#gfs.scanOptions()
#print gfs.getOptionsString()
#fs.formatDevice(fsconfig)
#fs=ComFileSystem.getFileSystem("ext3")
#fs.formatDevice(device)
#print isinstance(gfsneu, gfsFileSystem)
#print gfsneu.getOptionsString()
