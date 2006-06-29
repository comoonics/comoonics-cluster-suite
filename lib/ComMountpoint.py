"""Comoonics mountpoint module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComMountpoint.py,v 1.1 2006-06-29 08:16:33 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComMountpoint.py,v $


import xml.dom
from ComDevice import Device



class MountPoint(DataObject):
    TAGNAME="mountpoint"
    def __init__(self, element, doc):
        DataObject.__init__(self, element, doc)

    def getOptionsString(self):
        __opts="-o "
        __attr=self.getElement().getElementsByTagName("option")
        if not (__attr.length):
            return __opts + "defaults"
        for i in range(__attr.length): 
            __opts+=__attr.item(i).getAttribute("name")
            if __attr.item(i).hasAttribute("value"):
                __opts+="="
                __opts+=__attr.item(i).getAttribute("value")
            if i+1 < __attr.length:
                __opts+=","
        return __opts
        
# $Log: ComMountpoint.py,v $
# Revision 1.1  2006-06-29 08:16:33  mark
# initial checkin
#