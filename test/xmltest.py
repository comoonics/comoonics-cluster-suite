#from Ft.Xml import MarkupWriter

#writer = MarkupWriter()
#writer.startDocument() 

#writer.startElement(u'filesystem')
#writer.attribute(u'type', u'gfs')
#writer.attribute(u'journals', u"10")
#writer.endElement(u'filesystem')




from Ft.Xml import *
from Ft.Xml.Domlette import implementation, PrettyPrint


def printDom(doc):
    PrettyPrint(doc)

def printDeviceName(doc):
    node = doc.xpath("*/destination/device/@path")
    print node[0].value







doc = implementation.createRootNode('file:///article.xml')
cs = doc.createElementNS(EMPTY_NAMESPACE, 'copyset')
dest = doc.createElementNS(EMPTY_NAMESPACE, 'destination')
dest.setAttributeNS(EMPTY_NAMESPACE, 'type', 'filecopy')
cs.appendChild(dest)
device = doc.createElementNS(EMPTY_NAMESPACE, 'device')
device.setAttributeNS(EMPTY_NAMESPACE, 'type', 'lvm')
device.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/VG_wasauchimmer/LV_wasauchimmer')
dest.appendChild(device)
lvm = doc.createElementNS(EMPTY_NAMESPACE, 'lvm_config')
device.appendChild(lvm)
fs = doc.createElementNS(EMPTY_NAMESPACE, 'filesystem')
fs.setAttributeNS(EMPTY_NAMESPACE, 'type', 'gfs')
node = doc.createElementNS(EMPTY_NAMESPACE, 'fs_config')
node.setAttributeNS(EMPTY_NAMESPACE, 'bsize', '4096')
node.setAttributeNS(EMPTY_NAMESPACE, 'journals', '8')
node.setAttributeNS(EMPTY_NAMESPACE, 'clustername', 'mycluster')
node.setAttributeNS(EMPTY_NAMESPACE, 'locktable', 'mylocktable')
node.setAttributeNS(EMPTY_NAMESPACE, 'lockproto', 'lock_dlm')
fs.appendChild(node)
dest.appendChild(fs)

doc.appendChild(cs)


# ...using a single tab, rather than 2 spaces, to indent at each level
printDom(doc)
printDeviceName(doc)

print "Name of gfsnode is: " + node.nodeName


