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
from comoonics import ComUtils
from comoonics.enterprisecopy import ComCopyset, ComEnterpriseCopy


def printDom(doc):
    PrettyPrint(doc)

# create Reader object
reader = Sax2.Reader()

#parse the document
file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)

#element = xpath.Evaluate('businesscopy/copyset[@type=partition]', doc)[0]
xpathstr='%s/%s[@type="bootloader"]' % (ComEnterpriseCopy.EnterpriseCopy.TAGNAME, ComCopyset.Copyset.TAGNAME)
print "Searching for %s" % xpathstr
element = xpath.Evaluate(xpathstr, doc)[0]
copyset=ComCopyset.getCopyset(element, doc)
copyset.doCopy()