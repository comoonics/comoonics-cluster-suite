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
obj.setAttribute("option", "option2")
obj2=copy.deepcopy(obj)
obj4=copy.copy(obj)
obj2.setAttribute("option", "option3")
node=obj2.getDocument().createElement('element1a')
obj2.getElement().appendChild(node)
obj3=DataObject(node, doc)

print "Base Object: "
print obj
print "Deep Copy of Object: "
print obj2
print "Copy of Object: "
print obj4
print "Change option =>option2new (obj2, deepcopy)"
obj2.setAttribute("option", "option2new")
print "Change option =>option3new (obj4, copy)"
obj4.setAttribute("option", "option3new")
print "Base Object: "
print obj
print "Deep Copy of Object: "
print obj2
print "Copy of Object: "
print obj4

print "Another object: "
print obj3

