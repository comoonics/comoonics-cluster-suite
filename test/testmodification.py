import sys
import traceback
import copy
import os

sys.path.append("../lib")

from comoonics import ComDevice
from comoonics import ComDataObject
from comoonics.enterprisecopy import ComModificationset

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
from comoonics.ecbase import ComUtils
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath
from exceptions import *


# create Reader object
reader = Sax2.Reader()

file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)

PrettyPrint(doc)

sets = xpath.Evaluate('businesscopy/modificationset', doc)
print sets
for i in range(len(sets)):
    print sets[i]
    cs=ComModificationset.getModificationset(sets[i], doc)
    cs.doModifications()
    