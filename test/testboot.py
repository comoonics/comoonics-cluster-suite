import sys
import traceback

sys.path.append("../lib")



import os
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


import ComDisk
import ComUtils
import ComCopyset


def printDom(doc):
    PrettyPrint(doc)

# create Reader object
reader = Sax2.Reader()

#parse the document
file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)

#element = xpath.Evaluate('businesscopy/copyset[@type=partition]', doc)[0]
element = xpath.Evaluate('businesscopy/copyset[@type="bootloader"]', doc)[0]
copyset=ComCopyset.getCopyset(element, doc)
copyset.doCopy()