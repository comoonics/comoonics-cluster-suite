import sys
import traceback
import copy

sys.path.append("../lib")

import ComDevice
import ComUtils
import ComFileSystem
from ComFileSystem import *

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint

#doc = implementation.createRootNode('file:///article.xml')
doc = xml.dom.getDOMImplementation().createDocument(None, None, None)
cs = doc.createElementNS(EMPTY_NAMESPACE, 'copyset')
dest = doc.createElementNS(EMPTY_NAMESPACE, 'destination')
dest.setAttributeNS(EMPTY_NAMESPACE, 'type', 'filecopy')
cs.appendChild(dest)
device = doc.createElementNS(EMPTY_NAMESPACE, 'device')
device.setAttributeNS(EMPTY_NAMESPACE, 'type', 'lvm')
device.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/VG_SHAREDROOT/LV_SHAREDROOT')
dest.appendChild(device)
lvm = doc.createElementNS(EMPTY_NAMESPACE, 'lvm_config')
device.appendChild(lvm)
fs = doc.createElementNS(EMPTY_NAMESPACE, 'filesystem')
fs.setAttributeNS(EMPTY_NAMESPACE, 'type', 'gfs')
#node = doc.createElementNS(EMPTY_NAMESPACE, 'fs_config')
fs.setAttributeNS(EMPTY_NAMESPACE, 'bsize', '4096')
fs.setAttributeNS(EMPTY_NAMESPACE, 'journals', '8')
fs.setAttributeNS(EMPTY_NAMESPACE, 'clustername', 'mycluster')
fs.setAttributeNS(EMPTY_NAMESPACE, 'locktable', 'mylocktable')
fs.setAttributeNS(EMPTY_NAMESPACE, 'lockproto', 'lock_dlm')
#fs.appendChild(node)
device.appendChild(fs)
mopts=doc.createElementNS(EMPTY_NAMESPACE, 'mount_options')
mopt=doc.createElementNS(EMPTY_NAMESPACE, 'option')
mopt.setAttributeNS(EMPTY_NAMESPACE, 'name', 'noatime')
mopts.appendChild(mopt)
mopt=doc.createElementNS(EMPTY_NAMESPACE, 'option')
mopt.setAttributeNS(EMPTY_NAMESPACE, 'value', 'lock_nolock')
mopt.setAttributeNS(EMPTY_NAMESPACE, 'name', 'lockproto')
mopts.appendChild(mopt)
fs.appendChild(mopts)

doc.appendChild(cs)

PrettyPrint(doc)

dev=ComDevice.Device("/dev/null")
gfs=ComFileSystem.getFileSystem(fs)
gfs.formatDevice(dev)
print gfs.getOptionsString()
gfs.mount(dev, "/mnt/")
gfsneu=copy.deepcopy(gfs) 
#fs.labelDevice("neueslabel", device)
gfs.scanOptions()
print gfs.getOptionsString()
#fs.formatDevice(fsconfig)
#fs=ComFileSystem.getFileSystem("ext3")
#fs.formatDevice(device)
print isinstance(gfsneu, gfsFileSystem)
print gfsneu.getOptionsString()
