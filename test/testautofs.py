import sys
import traceback
import copy

sys.path.append("../lib")

from comoonics import ComDevice
from comoonics import ComUtils
from comoonics import ComFileSystem
from comoonics import ComDataObject
from comoonics import ComMountpoint

from comoonics.enterprisecopy import ComCopyset
from comoonics.ComFileSystem import *
from comoonics.ComMountpoint import *
from comoonics.ComDevice import *

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath

ComSystem.__EXEC_REALLY_DO="ask"

# create Reader object
reader = Sax2.Reader()

xml="""
<root>
    <filesystem type="auto" mkdir="false"/>
    <mountpoint name="/mnt/loop">
        <option name="loop"/>
    </mountpoint>
    <device name="/mnt/test/livecd.iso"/>
</root>
"""
xml2="<test/>"

doc = reader.fromString(xml)

PrettyPrint(doc)
root=doc.getElementsByTagName("root")[0]

fs=ComFileSystem.getFileSystem(root.getElementsByTagName("filesystem")[0], doc)
mp=MountPoint(root.getElementsByTagName("mountpoint")[0], doc)
dev=Device(root.getElementsByTagName("device")[0], doc)

#print fs, mp, dev

fs.mount(dev, mp)

