import sys
import traceback

sys.path.append("../lib")

import ComDevice
import ComUtils
import ComFileSystem

#sourcedisk=ComDisk.Disk("/dev/sdd")

from Ft.Xml import *
from Ft.Xml.Domlette import implementation, PrettyPrint


doc = implementation.createRootNode('file:///article.xml')
cs = doc.createElementNS(EMPTY_NAMESPACE, 'copyset')
dest = doc.createElementNS(EMPTY_NAMESPACE, 'destination')
dest.setAttributeNS(EMPTY_NAMESPACE, 'type', 'filecopy')
cs.appendChild(dest)
device = doc.createElementNS(EMPTY_NAMESPACE, 'device')
device.setAttributeNS(EMPTY_NAMESPACE, 'type', 'lvm')
device.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/VG_wasauchimmer/LV_wasauchimmer')
dest.appendChild(device)
lvm = doc.createElementNS(EMPTY_NAMESPACE, 'lvm_config')
device.appendChild(lvm)
fs = doc.createElementNS(EMPTY_NAMESPACE, 'filesystem')
fs.setAttributeNS(EMPTY_NAMESPACE, 'type', 'gfs')
node = doc.createElementNS(EMPTY_NAMESPACE, 'fs_config')
node.setAttributeNS(EMPTY_NAMESPACE, 'bsize', '4096')
node.setAttributeNS(EMPTY_NAMESPACE, 'journals', '8')
node.setAttributeNS(EMPTY_NAMESPACE, 'clustername', 'mycluster')
node.setAttributeNS(EMPTY_NAMESPACE, 'locktable', 'mylocktable')
node.setAttributeNS(EMPTY_NAMESPACE, 'lockproto', 'lock_dlm')
fs.appendChild(node)
dest.appendChild(fs)

doc.appendChild(cs)

fs=ComFileSystem.getFileSystem("gfs")
#fs.labelDevice("neueslabel", device)
fsconfig=ComFileSystem.FileSystemConfig(doc)
fs.formatDevice(fsconfig)
#fs=ComFileSystem.getFileSystem("ext3")
#fs.formatDevice(device)
