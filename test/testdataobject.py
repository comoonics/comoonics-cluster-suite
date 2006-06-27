import sys
import os
import copy
import xml.dom
from xml.dom import EMPTY_NAMESPACE
from xml.dom.ext import PrettyPrint


sys.path.append("../lib")



from ComDataObject import *

doc = xml.dom.getDOMImplementation().createDocument(None, None, None)
node = doc.createElement('element1')
node.setAttribute("name", "element1")
doc.appendChild(node)

obj=DataObject(node, doc)
obj.option="option2"
obj2=copy.deepcopy(obj)
obj2.option="option3"
node=obj2.getDocument().createElement('element1a')
obj2.getElement().appendChild(node)
obj3=DataObject(node, doc)

print obj
print obj2
print obj3

