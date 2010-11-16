""" Comoonics generic file modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFileModification.py,v 1.5 2010-11-16 11:30:40 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComFileModification.py,v $

from ComModification import Modification
from comoonics.storage.ComFile import File

class FileModification(Modification):
    """ generic FileModification Modification"""
    def __init__(self, element, doc):
        Modification.__init__(self, element, doc)
        
    def doRealModifications(self):
        files=self.createFileList(self.getElement(), self.getDocument())
        for i in range(len(files)):
            self.doModifications(files[i])
    
    def doModifications(self, file, save=True):
        pass
            
    # privat methods

    def createFileList(self, element, doc):
        """ creates the filelist and globs them if necessary """
        from comoonics.storage.ComFile import GlobNotSupportedException
        files=list()
        elements=element.getElementsByTagName("file")
        if elements and len(elements) > 0:
            for i in range(len(elements)):
                try:
                    _elements=File.globFilename(elements[i].getAttribute(File.ATTRNAME), doc)
                    if _elements:
                        files.extend(_elements)
                except GlobNotSupportedException:
                    files.append(elements[i])
        return files

# $Log: ComFileModification.py,v $
# Revision 1.5  2010-11-16 11:30:40  marc
# fixed bug with globs being applied on implicit skripts
#
# Revision 1.4  2010/09/21 14:11:29  marc
# work with list of files containing globs
#
# Revision 1.3  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.2  2010/02/09 21:48:24  mark
# added .storage path in includes
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.1  2006/07/07 11:33:24  mark
# initial release
#