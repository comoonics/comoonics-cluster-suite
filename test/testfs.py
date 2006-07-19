import sys
import traceback
import copy

sys.path.append("../lib")

from comoonics import ComDevice
from comoonics import ComUtils
from comoonics import ComFileSystem
from comoonics import ComDataObject
from comoonics.enterprisecopy import ComCopyset
from comoonics.ComFileSystem import *

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


# create Reader object
reader = Sax2.Reader()

file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)

PrettyPrint(doc)

sets = xpath.Evaluate('businesscopy/copyset[@type="filesystem"]', doc)
print sets
for i in range(len(sets)):
    print sets[i]
    cs=ComCopyset.getCopyset(sets[i], doc)
    print "copy command: " + cs.getCopyCommand()
    cs.doCopy()