
"""Comoonics Exceptions module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComExceptions.py,v 1.2 2006-06-23 11:52:40 mark Exp $
#


__version__ = "$$"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComExceptions.py,v $

import exceptions

import ComLog

class ComException(Exception):
     def __init__(self, value):
         self.value = value
         ComLog.getLogger("ComException").exception(value)

     def __str__(self):
         return repr(self.value)


# $Log: ComExceptions.py,v $
# Revision 1.2  2006-06-23 11:52:40  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
