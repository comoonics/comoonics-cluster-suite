
"""Comoonics Exceptions module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComExceptions.py,v 1.4 2007-02-27 15:55:26 mark Exp $
#


__version__ = "$$"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComExceptions.py,v $

import exceptions

import ComLog

class ComException(Exception):
     def __init__(self, value=""):
         if value != "":
             self.value = value
         else:
             self.value = self.__class__.__name__
         # ComLog.getLogger("ComException").exception(value)

     def __str__(self):
         if isinstance(self.value, unicode):
             # Don't throw a new exception if value.decode is not valid
             try:
                 self.value=self.value.decode()
             except Exception:
                 pass
         return repr(self.value)


# $Log: ComExceptions.py,v $
# Revision 1.4  2007-02-27 15:55:26  mark
# minor bugfixes
#
# Revision 1.3  2007/02/09 11:34:10  marc
# better handling of empty strings
#
# Revision 1.2  2006/07/26 10:06:47  marc
# no logging any more
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/06/23 11:52:40  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
