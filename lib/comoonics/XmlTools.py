"""
Collection of xml tools
"""

__version__= "$Revision $"

# $Id: XmlTools.py,v 1.19 2011-02-21 16:25:19 marc Exp $
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import warnings
#import xml.dom.Node
from xml.dom import Node
from comoonics import ComLog

logger=ComLog.getLogger("comoonics.XmlTools")

XPATH_SEP='/'

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

def evaluateXPath(path, element):
    try:
        import xml.dom
        from xml.xpath import Evaluate
        result=Evaluate(path, element)
        if hasattr(result,'__iter__'):
            for i in range(len(result)):
                if isinstance(result[i], xml.dom.Node) and result[i].nodeType == xml.dom.Node.ATTRIBUTE_NODE:
                    result[i]=result[i].value
        elif result==False or result==True:
            return result
        else:
            result=[result]
        return result
    except ImportError:
        # Implementation for etree
        from lxml.etree import XPath, fromstring, tounicode
        # returns a list of _ElementStringResult
        buf=toPrettyXML(element)
        elist=XPath(path).evaluate(fromstring(buf))
        nodelist=list()
        # if is iterable
        if hasattr(elist,'__iter__'):
            for eelement in elist:
                # either the returnlist is a stringlist or a element list
                if isinstance(eelement, basestring):
                    nodelist.append(eelement)
                else:
                    nodelist.append(parseXMLString(tounicode(eelement)).documentElement)
        elif elist==False or elist==True:
            return elist
        else:
            nodelist.append(elist)
        return nodelist

def overwrite_element_with_xpaths(element, xpaths):
    """ Overwrites all node values referred with the xpaths and the given values. Xpaths has to be a map with
        xpath as key and value as value. All other referred nodetypes are silently ignored.
    """
    for xpath in xpaths.keys():
        try:
            logger.debug("overwrite_element_with_xpaths xpath %s=%s, rootnode: %s, type(element): %s, class(element): %s" %(xpath, xpaths[xpath], element, type(element), element.__class__))
            if isinstance(element, Node):
                sets = evaluateXPath(xpath, element)
                logger.debug("overwrite_element_with_xpaths found %u matches. overwriting." %len(sets))
                for _set in sets:
                    if not isinstance(_set, basestring):
                        _set.nodeValue=xpaths[xpath]
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
    for s_child in source.childNodes:

        if filter and filter.acceptNode(s_child) != ElementFilter.FILTER_ACCEPT: continue
        if s_child.nodeType != Node.ELEMENT_NODE: continue


        # get pk values from source childs
        pkval=s_child.getAttribute(pk)
        tagname=s_child.tagName

        #print "found source element node %s, %s: %s" %(tagname, pk, pkval)

        # do we already have this child ?
        #elems=self.element.getElementsByTagName(tagname)
        # no we don't

        #logger.debug("merge_trees_with_pk xpath: %s/@%s='%s'" %(tagname, pk, pkval))
        try:
            _path=evaluateXPath(tagname+"/@"+pk+"='"+pkval+"'", dest)
        except:
            #ComLog.debugTraceLog(logger)
            _path=False
        if not _path:
            #print "we don't have this element, adding"
            # lets copy things from the source
            # - create new element
            d_child=doc.createElement(tagname)
            # - add all Attributes
            for i in range(s_child.attributes.length):
                attrnode=s_child.attributes.item(i)
                d_child.setAttribute(attrnode.name, s_child.getAttribute(attrnode.name))
            # - add child
            #print "add new child"
            if not onlyone:
                add_element_to_node_sorted(d_child, dest, pk)

        # yes we have
        else:
            # - get this child
            d_child=evaluateXPath(tagname+"[@"+pk+"='"+pkval+"']", dest)[0]

        # - copy all attributes
        for i in range(s_child.attributes.length):
            attrnode=s_child.attributes.item(i)
            #print "new attribute: %s" % attrnode.name
            if not d_child.hasAttribute(attrnode.name):
                d_child.setAttribute(attrnode.name, s_child.getAttribute(attrnode.name))
        # recursion on child
        merge_trees_with_pk(s_child, d_child, doc, pk, filter, onlyone)

def getDOMImplementation(*params):
    import xml.dom
    impl=None
    if params:
        try:
            impl=xml.dom.getDOMImplementation(params)
        except (ImportError, TypeError):
            pass
    if not impl:
#        try:
#            import Ft.Xml.Domlette
#            impl=Ft.Xml.Domlette.implementation
#        except (ImportError, TypeError):
        impl=xml.dom.getDOMImplementation()
    return impl

def parseXMLFile(xmlfile, validate=False):
    """
    Parses the given XML file and returns a xml.dom.Document as result.
    @param xmlfile: the path to the file to be parsed.
    @type  xmlfile: L{String}
    @param validate: If it should also be validated (Default: False)
    @type  validate: L{Boolean}
    @return: the document element.
    @rtype: L{xml.dom.Document} 
    """
    import os
    filep = os.fdopen(os.open(xmlfile, os.O_RDONLY))
    doc= parseXMLFP(filep, validate)
    filep.close()
    return doc

def parseXMLFP(filep, validate=False):
#    try:
#        from Ft.Xml import Parse
#        doc=Parse(filep)
#    except ImportError:
    import xml.dom.minidom
    doc=xml.dom.minidom.parse(filep)
    return doc

def parseXMLString(xmlstring, validate=False):
#    try:
#        from Ft.Xml import Parse
#        doc=Parse(xmlstring)
#    except ImportError:
    import xml.dom.minidom
    doc=xml.dom.minidom.parseString(xmlstring)
    return doc

def toPrettyXML(node, ident="\t", newl="\n"):
    import cStringIO
    buf=cStringIO.StringIO()
    toPrettyXMLFP(node, buf, ident, newl)
    return buf.getvalue()

def toPrettyXMLFP(node, filep, ident="\t", newl="\n"):
#    try:
#        from Ft.Xml.Domlette import PrettyPrint
#        import cStringIO
#        buf = cStringIO.StringIO()
#        PrettyPrint(node, stream=buf)
#        return buf.getvalue()
#    except ImportError:
    try:
        import xml.dom.minidom
        removePrettyTextNodes(node)
        if isinstance(node, xml.dom.minidom.Attr):
            filep.write(node.nodeValue+newl)
        elif isinstance(node, xml.dom.minidom.Node):
            node.writexml(filep, "", ident, newl)
        else:
            from xml.dom.ext import PrettyPrint
            PrettyPrint(node, stream=filep)
    except ImportError:
        try:
            import Ft.Xml.cDomlette
            if isinstance(node, Ft.Xml.cDomlette.Node):
                from Ft.Xml.Lib.Print import  PrettyPrint
                PrettyPrint(node, stream=filep)
        except: 
            from xml.dom.ext import PrettyPrint
            PrettyPrint(node, stream=filep)
            
def removePrettyTextNodes(element, deep=True):
    """
    Removes all child Text Nodes being left from parsing a pretty document. Then toPrettyXml can be used again.
    @param element: The element to be analysed
    @param deep: walk recursive through the tree, default: True
    @return: None 
    """
    import re
    removeTextNodes(element, re.compile("^\s+$"), deep)
    
def removeTextNodes(element, stringorregexp, deep=True):
    """
    Removes all child Text Nodes that match the given stringorrepgexp.
    @param element: the element to be analysed
    @param stringorregexp: the string or regexp to be matched against.
    @param deep: walk recursive through the tree, default: True
    @type string: L<string>, L<re>   
    """ 
    import xml.dom
    child=element.firstChild
    children2remove=list()
    while child:
        if child.nodeType==xml.dom.Node.TEXT_NODE:
            if isinstance(stringorregexp, basestring):
                if child.nodeValue == stringorregexp:
                    element.removeChild(child)
            elif stringorregexp.match(child.nodeValue):
                children2remove.append(child)
        elif child.nodeType==xml.dom.Node.ELEMENT_NODE and deep:
            removeTextNodes(child, stringorregexp, deep)
        child=child.nextSibling
    for child in children2remove:
        element.removeChild(child)
        
def clone_node(node, doc=None):
    """
    clones the given node by creating a new one
    """
    import xml.dom
    if not doc:
        _impl=getDOMImplementation()
        doc=_impl.createDocument(None, node.tagName, None)
    if node.nodeType==Node.ELEMENT_NODE:
        newnode=doc.createElement(node.tagName)
        for _i in range(node.attributes.length):
            _attr=node.attributes.item(_i)
            if _attr:
                newnode.setAttribute(_attr.nodeName, _attr.nodeValue)
        child=node.firstChild
        while child:
            newnode.appendChild(clone_node(child, doc))
            child=child.nextSibling
        return newnode
    elif node.nodeType==Node.TEXT_NODE or node.nodeType==Node.CDATA_SECTION_NODE:
        return doc.createTextNode(node.data)
    elif node.nodeType==Node.PROCESSING_INSTRUCTION_NODE:
        return doc.createProcessingInstruction(node.target, node.data)
    elif node.nodeType==Node.COMMENT_NODE:
        return doc.createComment(node.data)
    else:
        return node.cloneNode(1)

def add_element_to_node(child, element, doc=None):
    """
    adds an element @child to the element tree @element. The child is copied.
    """
    if not doc:
        _impl=getDOMImplementation()
        doc=_impl.createDocument(None, doc.documentElement.tagName, None)
    if child.nodeType==Node.ELEMENT_NODE:
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
    keyval=child.getAttribute(key)

    for mychild in elem.childNodes:

        if mychild.nodeType != Node.ELEMENT_NODE: continue

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


def createDOMfromXML(xmlstring, xslfilename=None, validate=False):
    """
    creates a new DOM from a given xml string. Optionally, a xsl file can be used for translation
    """
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
        doc=parseXMLString(str_buff)
    else:
        import StringIO
        buf=StringIO.StringIO(xmlstring)
        doc=parseXMLFP(buf)
        buf.close()
    return doc

def xpathjoin(path1, *paths):
    """
    Joins the given path to an xpath representation. Queries have to be in the paths.
    @param paths: the paths as an array
    @type list of paths:
    @return: a compiled xpath
    @rtype: xml.xpath.Compile()
    """
    path = path1
    for b in paths:
        if b.startswith(XPATH_SEP):
            path = b
        elif path == '' or path.endswith(XPATH_SEP):
            path +=  b
        else:
            path += XPATH_SEP + b
    return path
   

def xpathsplit(_xpath):
    """
    Returns a list of pathnames of the given xpath
    @param _xpath: the xpath as string
    @type _xpath: string
    @return: a list of xpath elements
    @rtype: list
    """
    if _xpath.startswith(XPATH_SEP):
        return _xpath.split(XPATH_SEP)[1:]
    else:
        return _xpath.split(XPATH_SEP)

#################
# $Log: XmlTools.py,v $
# Revision 1.19  2011-02-21 16:25:19  marc
# - fixed a bug in evaluateXPath that a query that returns False would be given through.
#
# Revision 1.18  2011/01/12 10:06:08  marc
# fixed bug (#398) in evaluateXPath that would cause a bug with old xml implementation (python 2.4 and xml.dom) that would return Attributes as Attr not as value. But expected as value.
#
# Sideeffect was that e.g. com-dsh would not work.
#
# Revision 1.17  2010/12/09 14:58:22  marc
# - getDOMImplemenation:
#   - would still return 4Dom implementation as default instead of default from xml.dom (minidom). Now xml.dom.getDOMImplemenation will be called right away
#
# Revision 1.16  2010/11/21 21:48:53  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#   - finished implementation of XmlTools
#
# Revision 1.15  2010/09/21 14:26:06  marc
# reimplemented most functions so that they can use different implementations.
#
# Revision 1.14  2010/02/05 12:24:15  marc
# - added parseXMLFile
# - changed implementation to default 4DOM then fall back
#
# Revision 1.13  2009/07/22 08:37:40  marc
# fedora compliant
#
# Revision 1.12  2009/06/10 15:19:20  marc
# - added xpathjoin/split
#
# Revision 1.11  2008/07/08 07:27:15  andrea2
# Added validate_xml
#
# Revision 1.10  2008/02/27 10:44:31  marc
# - changed an import
#
# Revision 1.9  2008/02/27 09:15:43  mark
# reversed last change
#
# Revision 1.8  2008/02/22 09:42:57  mark
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