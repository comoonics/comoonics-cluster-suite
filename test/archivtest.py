import sys
import traceback

sys.path.append("../lib")



import os
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


from comoonics import ComArchiv
from comoonics import ComSystem
from comoonics import ComUtils

# create Reader object
reader = Sax2.Reader()

#parse the document
xml="""
<root>
<archive name="testarchive" format="simple" type="fs"/>
</root>
"""
doc = reader.fromString(xml)

elem=doc.getElementsByTagName("archive")

fname="/etc/fedora-release"
for i in range(len(elem)):
    arc=ComArchiv.Archiv(elem[i],doc)
    print "add File"
    arc.addFile(fname)
    print "get File"
    file=arc.getFileObj(fname)
    print file.readline()
    print "extract File"
    arc.extractFile(fname, "/tmp/test/")
