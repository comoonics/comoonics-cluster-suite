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

def line(str=None):
    print
    print "--------------------"+str+"---------------------------------"

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

attribute="xyz"
line("Testing hasAttribute(%s)" %attribute)
if obj.hasAttribute(attribute):
    print "Found Attribute \"%s\"!! Should not happen!!!" %attribute
else:
    print "No Attribute \"%s\" available. (OK)" % attribute

attribute="id"
line("Testing hasAttribute(%s)" %attribute)
if obj.hasAttribute(attribute):
    print "Found Attribute \"%s\"!! (OK)" %attribute
else:
    print "No Attribute \"%s\"!! Should not happen!!!" %attribute

attribute="xyz"
default=""
line("Testing getAttribute(%s, %s)" %(attribute, default))
result=obj.getAttribute(attribute, default)
print "Found value for Attribute \"%s\"=\"%s\"" %(attribute, result)

attribute="id"
default="12"
line("Testing getAttribute(%s, %s)" %(attribute, default))
result=obj.getAttribute(attribute, default)
print "Found value for Attribute \"%s\"=\"%s\"" %(attribute, result)

attribute="xyz"
line("Testing getAttribute(%s)" %(attribute))
try:
    result=obj.getAttribute(attribute)
    print "Found value for Attribute \"%s\": %s !!!Should not happen !!!" %(attribute, result)
except:
    import sys
    print "Exception %s caught (OK)" %sys.exc_value

attribute="id"
line("Testing getAttribute(%s)" %(attribute))
try:
    result=obj.getAttribute(attribute)
    print "Found value for Attribute \"%s\": %s (OK)" %(attribute, result)
except:
    import sys
    print "Exception %s caught: !!!!SHould not happen!!!" %sys.exc_value

line("Testing boolean")
path="//device[@id='rootfs']"
element=xpath.Evaluate(path, doc)[0]
obj=DataObject(element)
print "%s.options: %s" %(path, obj.getAttribute("options"))
print "%s.options: '%s'" %(path, obj.getElement().getAttribute("options"))
