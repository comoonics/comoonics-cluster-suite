""" Comoonics file module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFile.py,v 1.5 2010-11-16 11:23:34 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComFile.py,v $

from comoonics.ComDataObject import DataObject
from comoonics.ComExceptions import ComException

class GlobNotSupportedException(ComException):
    def __str__(self):
        return "File globbing to supported for the given file %s." %self.value

class File(DataObject):
    TAGNAME="file"
    ATTRNAME="name"
    def _createElement(filename, document):
        """
        Create an empty file element. If document is given the document is the bases.
        @param filename: the filename to be given to the file
        @type  filename: String
        @param document: the xml.dom.Document to use for creating a new element. If None it will be 
                         automatically created
        @type  document: xml.dom.Document
        @return: The element and the document being created
        @rtype:  [xml.dom.Element, xml.dom.Document] 
        """
        import xml.dom
        if not document:
            impl=xml.dom.getDOMImplementation()
            document=impl.createDocument(None, File.TAGNAME, None)
            element=document.documentElement
        else:
            element=document.createElement(File.TAGNAME)
        element.setAttribute(File.ATTRNAME, filename)
        return (element, document)
    _createElement=staticmethod(_createElement)

    def globFilename(filename, doc):
        """
        Creates a list of File elements for the given filename. The filename is expanded via the 
        glob.glob method.
        @param filename: a string specifying the filename to be taken. Wildcards are allowed.
        @type  filename: String
        @param doc: the DOM document to be used to create the elements
        @type  doc: xml.dom.Document
        @return: a list of Elements being globalized via glob.glob.
        @rtype:  list<xml.dom.Element>
        """
        elements=list()
        try:
            import glob
            # we need to exclude implicit shells from being globbed
            import re
            if re.search("\$\(.*\)", filename):
                raise GlobNotSupportedException(filename)
            else:
                filenames=glob.glob(filename)
                if filenames:
                    for _filename in filenames:
                        (element, doc)=File._createElement(_filename, doc)
                        elements.append(element)
            return elements
        except ImportError:
            return elements
    globFilename=staticmethod(globFilename)
    
    """ Base Class for all source and destination objects"""
    def __init__(self, *params, **keys):
        doc=None
        filename=None
        if params and len(params)==1:
            filename=params[0]
        if params and len(params)==2:
            element=params[0]
            doc=params[1]
        if keys and keys.has_key("element"):
            element=keys["element"]
        if keys and keys.has_key("document"):
            doc=keys["document"]
        if keys and keys.has_key("filename"):
            filename=keys["filename"]
        
        if filename:
            (element, doc)=self._createElement(filename, doc)

        if not element and not doc:
            raise TypeError("File.__init__ takes either 1 or 2 parameters or 1 or 2 keywords as parameters.")

        super(File, self).__init__(element, doc)
        
# $Log: ComFile.py,v $
# Revision 1.5  2010-11-16 11:23:34  marc
# fixed bug with globs being applied on implicit skripts
#
# Revision 1.4  2010/09/21 14:20:44  marc
# added createElement, globFilename and integrated in Constructor
#
# Revision 1.3  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2010/02/09 21:48:51  mark
# added .storage path in includes
#
# Revision 1.1  2009/09/28 15:13:36  marc
# moved from comoonics here
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/06/30 08:01:25  mark
# initial checkin
#
