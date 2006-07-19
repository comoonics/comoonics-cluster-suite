import sys
import os
import copy
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import Sax2
from xml import xpath

sys.path.append("../lib")


from comoonics.ComDataObject import *



# create Reader object
reader = Sax2.Reader()

#parse the document
file=os.fdopen(os.open("./example_config.xml",os.O_RDONLY))
doc = reader.fromStream(file)


print'search for id "rootfs"'
element=xpath.Evaluate('//*[@refid="bootfs"]', doc)[0]

obj=DataObject(element, doc)
PrettyPrint(obj.getElement())
print obj

