import sys
import traceback

sys.path.append("../lib")



import os
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath


from comoonics.ecbase import ComUtils
from comoonics.enterprisecopy import ComRegexpModification

def printDom(doc):
    PrettyPrint(doc)

# create Reader object
reader = Sax2.Reader()

#parse the document
document_file="./example_regexp_mod.xml"
print "Parsing document %s" %document_file
file=os.fdopen(os.open(document_file, os.O_RDONLY))
doc = reader.fromStream(file)
print "OK"
element = doc.documentElement
file = element.getElementsByTagName("file")[0]
print "Doing regexpmodification"
regexpmod=ComRegexpModification.RegexpModification(element, doc)
regexpmod.doRegexpModifications(file, False, sys.stdout)
print "OK"