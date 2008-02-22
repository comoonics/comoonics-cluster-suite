#!/usr/bin/python
"""
Collection of xml tools
"""

__version__= "$Revision $"

# $Id: XmlTools.py,v 1.8 2008-02-22 09:42:57 mark Exp $

import warnings
import xml.dom.Node
from xml.dom import Node
from xml.dom.ext.reader import Sax2
from comoonics import ComLog

logger=ComLog.getLogger("comoonics.XmlTools")

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
            logger.debug("overwrite_element_with_xpaths xpath %s=%s, rootnode: %s, type(element): %s, class(element): %s" %(xpath, xpaths[xpath], element, type(element), element.__class__))
            if isinstance(element, xml.dom.Node):
                from xml.dom   import Element, Node
                from xml.xpath import Evaluate
                sets = Evaluate(xpath, element)
                logger.debug("overwrite_element_with_xpaths found %u matches. overwriting." %len(sets))
                for set in sets:
                    set.nodeValue=xpaths[xpath]
            else:
                import libxml2
                ctxt = element.xpathNewContext()
                sets = ctxt.xpathEvalExpression(xpath)
                for set in sets:
                    logger.debug("%s, %s" %(set.name, set.content))
                    set.setContent(xpaths[xpath])
                    logger.debug("%s, %s" %(set.name, set.content))
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

def merge_trees_with_pk(source, dest, doc, pk="name", filter=None, onlyone=False, takesource=False):
    """ add all element children from element source to
    if they are not already there.
    doc is the destination DOMDocument
    pk is used as primary key.
    If filter [NodeFilter] is the DOM2 Nodefilter interface is applied to any element to be checked.
    True and False are to be returned
    Also adds all Attributes from dataobject if the are not present.
    If onlyone then only one child with the same pk is taken.
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

        #logger.debug("merge_trees_with_pk xpath: %s/@%s='%s'" %(tagname, pk, pkval))
        try:
            _path=xpath.Evaluate(tagname+"/@"+pk+"='"+pkval+"'", dest)
        except xpath.pyxpath.SyntaxError:
            #ComLog.debugTraceLog(logger)
            _path=False
        if not _path:
            #print "we don't have this element, adding"
            # lets copy things from the source
            # - create new element
            d_child=doc.createElement(tagname)
            # - add all Attributes
            for attrnode in xpath.Evaluate("@*", s_child):
                d_child.setAttribute(attrnode.name, s_child.getAttribute(attrnode.name))
            # - add child
            #print "add new child"
            if not onlyone:
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
        merge_trees_with_pk(s_child, d_child, doc, pk, filter, onlyone)

def clone_node(node, doc=None):
    """
    clones the given node by creating a new one
    """
    import xml.dom
    if not doc:
        _impl=xml.dom.getDOMImplementation()
        doc=_impl.createDocument(None, node.tagName, None)
    if node.nodeType==xml.dom.Node.ELEMENT_NODE:
        newnode=doc.createElement(node.tagName)
        for _child in node.childNodes:
            newnode.appendChild(clone_node(_child, doc))
        for _i in range(node.attributes.length):
            _attr=node.attributes.item(_i)
            newnode.setAttribute(_attr.nodeName, _attr.nodeValue)
        return newnode
    elif node.nodeType==xml.dom.Node.TEXT_NODE or node.nodeType==xml.dom.Node.CDATA_SECTION_NODE:
        return doc.createTextNode(node.data)
    elif node.nodeType==xml.dom.Node.PROCESSING_INSTRUCTION_NODE:
        return doc.createProcessingInstruction(node.target, node.data)
    elif node.nodeType==xml.dom.Node.COMMENT_NODE:
        return doc.createComment(node.data)
    else:
        return node.cloneNode(1)

def add_element_to_node(child, element, doc=None):
    """
    adds an element @child to the element tree @element. The child is copied.
    """
    import xml.dom
    if not doc:
        _impl=xml.dom.getDOMImplementation()
        doc=_impl.createDocument(None, doc.documentElement.tagName, None)
    if child.nodeType==xml.dom.Node.ELEMENT_NODE:
        newchild=doc.createElement(child.tagName)
        for _child in child.childNodes:
            add_element_to_node(_child, newchild, doc)
        element.appendChild(newchild)
    else:
        element.appendChild(child.cloneNode(1))
    return element

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

def getTextFromElement(element):
    """ Returns the value of the first textnode found in the given element. If no textnode found None is returned """
    return_text=None
    children=element.childNodes
    for child in children:
        if child and child.nodeType == Node.TEXT_NODE:
            return_text=child.nodeValue
    return return_text


def createDOMfromXML(xmlstring, xslfilename=None, validate=0):
    """
    creates a new DOM from a given xml string. Optionally, a xsl file can be used for translation
    """
    reader=Sax2.Reader(validate)
    if xslfilename:
        import libxslt
        import libxml2
        n_doc = libxml2.parseDoc(xmlstring)
        style = libxml2.parseFile(xslfilename)
        xslt_style = libxslt.parseStylesheetDoc(style)
        params={}
        res = xslt_style.applyStylesheet(n_doc, params)
        str_buff=xslt_style.saveResultToString(res)
        xslt_style.freeStylesheet()
        n_doc.freeDoc()
        res.freeDoc()
        doc=reader.fromString(str_buff)
    else:
        doc=reader.fromStream(xmlstring)
    return doc

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
    xpaths={"node/@name": "myname",
            "/localclone/destdisks/disk/@name": "/dev/sda1"}
    print "-----------_Before(overwrite_element_with_xpaths)_-------------"
    PrettyPrint(doc)
    overwrite_element_with_xpaths(doc.documentElement, xpaths)
    print "-----------_After(overwrite_element_with_xpaths)_--------------"
    PrettyPrint(doc)

    xml2="<xyz>abcd</xyz>"
    xml3="""<xyz abcd="abs"/>"""
    doc=parseString(xml2)
    print "getTextFromElement(%s): %s" %(xml2, getTextFromElement(doc.documentElement))
    doc=parseString(xml3)
    print "getTextFromElement(%s): %s" %(xml3, getTextFromElement(doc.documentElement))

    xml1="""
    <a>
       <a name="a">
          <aa/>
       </a>
       <b name="a">
          <ba/>
       </b>
       <c name="b">
          <cb/>
       </c>
    </a>
    """
    xml2="""
    <a>
       <b name="a">
          <bb/>
       </b>
       <c name="b">
          <ca/>
       </c>
       <d name="a">
         <da/>
       </d>
    </a>
    """

    import xml.dom
    print "Testing merging of two documents"
    print "xml1: "
    _xml1=parseString(xml1)
    PrettyPrint(_xml1)
    print "xml2: "
    _xml2=parseString(xml2)
    PrettyPrint(_xml2)
    _result=xml.dom.getDOMImplementation().createDocument(None, "a", None)

    print "Result(onlyone=True): "
    merge_trees_with_pk(_xml1.documentElement, _xml2.documentElement, _xml2, "name", None, True)
    PrettyPrint(_xml2)
    print "Result(onlyone=False): "
    _xml2=parseString(xml2)
    merge_trees_with_pk(_xml1.documentElement, _xml2.documentElement, _xml2, "name", None, False)
    PrettyPrint(_xml2)

    print "Testing clone of element: "
    print "xml2: "
    PrettyPrint(_xml2)
    print "clone_node(xml2)"
    PrettyPrint(clone_node(_xml2.documentElement))

if __name__ == '__main__':
    main()

#################
# $Log: XmlTools.py,v $
# Revision 1.8  2008-02-22 09:42:57  mark
# minor import fix
#
# Revision 1.7  2008/02/21 16:10:59  mark
# added new method createDOMfromXML
#
# Revision 1.6  2007/09/07 14:49:07  marc
# - logging
# - better testing
# - added clone_node
# - extended merge_tree
#
# Revision 1.5  2007/03/12 17:03:18  mark
# Bug Fix: compares pk attributes: fixes bz #35
#
# Revision 1.4  2007/02/09 11:35:44  marc
# added getTextFromElement
#
# Revision 1.3  2006/12/13 20:17:15  marc
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