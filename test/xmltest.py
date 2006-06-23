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
lvm = doc.createElementNS(EMPTY_NAMESPACE, 'volume_management')
vg = doc.createElementNS(EMPTY_NAMESPACE, 'volume_group')
vg.setAttributeNS(EMPTY_NAMESPACE, 'name', 'vg1')
lv1 = doc.createElementNS(EMPTY_NAMESPACE, 'logical_volume')
lv1.setAttributeNS(EMPTY_NAMESPACE, 'name', 'lv1')
lv1.setAttributeNS(EMPTY_NAMESPACE, 'size', '100M')
lv2 = doc.createElementNS(EMPTY_NAMESPACE, 'logical_volume')
lv2.setAttributeNS(EMPTY_NAMESPACE, 'name', 'lv2')
lv2.setAttributeNS(EMPTY_NAMESPACE, 'size', '200M')
pv1 = doc.createElementNS(EMPTY_NAMESPACE, 'physical_volume')
pv1.setAttributeNS(EMPTY_NAMESPACE, 'name', 'pv1')
pv1.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/sdc')
pv2 = doc.createElementNS(EMPTY_NAMESPACE, 'physical_volume')
pv2.setAttributeNS(EMPTY_NAMESPACE, 'name', 'pv2')
pv2.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/sda1')
vg.appendChild(lv1)
vg.appendChild(lv2)
vg.appendChild(pv1)
vg.appendChild(pv2)
lvm.appendChild(vg)

dest.appendChild(lvm)


device = doc.createElementNS(EMPTY_NAMESPACE, 'device')
# device.setAttributeNS(EMPTY_NAMESPACE, 'type', 'lvm')
device.setAttributeNS(EMPTY_NAMESPACE, 'path', '/dev/vg1/lv1')


dest.appendChild(device)
fs = doc.createElementNS(EMPTY_NAMESPACE, 'filesystem')
fs.setAttributeNS(EMPTY_NAMESPACE, 'type', 'gfs')
node = doc.createElementNS(EMPTY_NAMESPACE, 'fs_config')
node.setAttributeNS(EMPTY_NAMESPACE, 'bsize', '4096')
node.setAttributeNS(EMPTY_NAMESPACE, 'journals', '8')
node.setAttributeNS(EMPTY_NAMESPACE, 'clustername', 'mycluster')
node.setAttributeNS(EMPTY_NAMESPACE, 'locktable', 'mylocktable')
node.setAttributeNS(EMPTY_NAMESPACE, 'lockproto', 'lock_dlm')
fs.appendChild(node)
device.appendChild(fs)

doc.appendChild(cs)


# ...using a single tab, rather than 2 spaces, to indent at each level
printDom(doc)
printDeviceName(doc)

print "Name of gfsnode is: " + node.nodeName


