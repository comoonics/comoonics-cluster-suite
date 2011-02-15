import sys
import traceback

sys.path.append("../lib")



import os
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


from comoonics import ComDisk
from comoonics import ComSystem
from comoonics.ecbase import ComUtils
from comoonics.enterprisecopy import ComCopyset
from comoonics.ComDisk import Disk

# create Reader object
reader = Sax2.Reader()

#parse the document
xml="""
<root>
<disk name="/dev/sdf"/>
<disk name="/dev/sdg"/>
<disk name="/dev/gnbd/masterroot"/>
</root>
"""
doc = reader.fromString(xml)

elem=doc.getElementsByTagName("disk")

for i in range(len(elem)):
    disk=Disk(elem[i],doc)
    if disk.hasPartitionTable():
        print disk.getAttribute("name")+" has partiton table\n"
    else:
        print disk.getAttribute("name")+" has no partition table\n"

