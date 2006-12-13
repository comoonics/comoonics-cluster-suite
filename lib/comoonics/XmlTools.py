#!/usr/bin/python
"""
Collection of xml tools
"""

__version__= "$Revision $"

# $Id: XmlTools.py,v 1.3 2006-12-13 20:17:15 marc Exp $

import warnings
from xml.dom import Node

class ElementFilter(object):
    FILTER_ACCEPT = 1
    FILTER_REJECT = 2
    FILTER_SKIP   = 3

    def __init__(self, name=""):
        self.name_filter=name

    def acceptNode(self, node):
        if node.nodeType == Node.ELEMENT_NODE:
            if self.name_filter and type(self.name_filter) == str and self.name_filter==node.tagName:
                return ElementFilter.FILTER_ACCEPT
            elif self.name_filter and type(self.name_filter) == str and self.name_filter!=node.tagName:
                return ElementFilter.FILTER_REJECT
            elif self.name_filter and self.name_filter.match(node.tagName):
                return ElementFilter.FILTER_ACCEPT
            else:
                return ElementFilter.FILTER_REJECT
        else:
            return ElementFilter.FILTER_REJECT

def overwrite_element_with_xpaths(element, xpaths):
    """ Overwrites all node values referred with the xpaths and the given values. Xpaths has to be a map with
        xpath as key and value as value. All other referred nodetypes are silently ignored.
    """
    for xpath in xpaths.keys():
        try:
            import xml

            if isinstance(element, xml.dom.Node):
                from xml.dom   import Element, Node
                from xml.xpath import Evaluate
                sets = Evaluate(xpath, element)
                for set in sets:
                    set.nodeValue=xpaths[xpath]
            else:
                import libxml2
                ctxt = element.xpathNewContext()
                sets = ctxt.xpathEvalExpression(xpath)
                for set in sets:
                    print "%s, %s" %(set.name, set.content)
                    set.setContent(xpaths[xpath])
                    print "%s, %s" %(set.name, set.content)
#                import StringIO
#                ctxt.xpathFreeContext()
#                f = StringIO.StringIO()
#                buf = libxml2.createOutputBuffer(f, 'UTF-8')
#                element.saveFormatFileTo(buf, 'UTF-8', 0)
#                print f.getvalue()
        except:
            warnings.warn("Could not apply value \"%s\" to xpath \"%s\"." %(xpaths[xpath], xpath))
            import traceback
            traceback.print_exc()

    return element

def merge_trees_with_pk(source, dest, doc, pk="name", filter=None):
    """ add all element children from element source to
    if they are not already there.
    doc is the destination DOMDocument
    pk is used as primary key.
    If filter [NodeFilter] is the DOM2 Nodefilter interface is applied to any element to be checked.
    True and False are to be returned
    Also adds all Attributes from dataobject if the are not present.
    """
    #get source childs

    import xml
    from xml import xpath

    for s_child in source.childNodes:

        if filter and filter.acceptNode(s_child) != ElementFilter.FILTER_ACCEPT: continue
        if s_child.nodeType != xml.dom.Node.ELEMENT_NODE: continue


        # get pk values from source childs
        pkval=s_child.getAttribute(pk)
        tagname=s_child.tagName

        #print "found source element node %s, %s: %s" %(tagname, pk, pkval)

        # do we already have this child ?
        #elems=self.element.getElementsByTagName(tagname)
        # no we don't
        if not xpath.Evaluate(tagname+"/@"+pk+"='"+pkval+"'", dest):
            #print "we don't have this element, adding"
            # lets copy things from the source
            # - create new element
            d_child=doc.createElement(tagname)
            # - add child
            #print "add new child"
            add_element_to_node_sorted(d_child, dest, pk)

        # yes we have
        else:
            # - get this child
            d_child=xpath.Evaluate(tagname+"[@"+pk+"='"+pkval+"']", dest)[0]

        # - copy all attributes
        for attrnode in xpath.Evaluate("@*", s_child):
            #print "new attribute: %s" % attrnode.name
            if not d_child.hasAttribute(attrnode.name):
                d_child.setAttribute(attrnode.name, s_child.getAttribute(attrnode.name))
        # recursion on child
        merge_trees_with_pk(s_child, d_child, doc, pk)


def add_element_to_node_sorted(child, elem, key):
    """ adds an  element child into the elem tree
    with respect to the key-Attribute value
    TODO add generic comparison method (see lamda)
    """
    import xml

    keyval=child.getAttribute(key)

    for mychild in elem.childNodes:

        if mychild.nodeType != xml.dom.Node.ELEMENT_NODE: continue

        if mychild.getAttribute(key) > keyval:
            elem.insertBefore(child, mychild)
            return elem

    elem.appendChild(child)
    return elem

def main():
    xml="""<?xml version="1.0" encoding="UTF-8"?>
<localclone>
  <node name="lilr629"/>
  <destdisks><disk name="/dev/gnbd/singleclone"/></destdisks>
  <kernel version="2.6.9-34.0.1.ELsmp"/>
</localclone>
    """
    from xml.dom.ext import PrettyPrint
    from xml.dom.minidom import parseString
    doc=parseString(xml)
    xpaths={"/localclone/node/@name": "myname",
            "/localclone/destdisks/disk/@name": "/dev/sda1"}
    print "-----------_Before_-------------"
    PrettyPrint(doc)
    overwrite_element_with_xpaths(doc.documentElement, xpaths)
    print "-----------_After(overwrite_element_with_xpaths)_--------------"
    PrettyPrint(doc)

if __name__ == '__main__':
    main()

#################
# $Log: XmlTools.py,v $
# Revision 1.3  2006-12-13 20:17:15  marc
# added tests and ElementFilter
#
# Revision 1.2  2006/12/08 09:47:40  mark
# added merge_trees_with_pk
# added add_element_to_node_sorted
#
# Revision 1.1  2006/12/08 09:00:22  marc
# *** empty log message ***
#
# Revision 1.1  2006/12/08 08:32:05  marc
# initial revision
#