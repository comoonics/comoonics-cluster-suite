import sys
import traceback
import copy
import os

sys.path.append("/home/mark/entwicklung/nashead2004/management/comoonics-clustersuite/python/lib")

import ComDevice
import ComUtils
import ComDataObject
import ComModificationset

#sourcedisk=ComDisk.Disk("/dev/sdd")

#from Ft.Xml import *
#from Ft.Xml.Domlette import implementation, PrettyPrint

import xml.dom
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
    