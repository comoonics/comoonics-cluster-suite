
"""Comoonics Exceptions module

here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComExceptions.py,v 1.9 2010-05-27 08:50:40 marc Exp $
#
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


__version__ = "$$"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComExceptions.py,v $

class ComException(Exception):
    def __init__(self, value=""):
        Exception.__init__(self)
        if value != "":
            self.value = value
        else:
            self.value = self.__class__.__name__

    def __str__(self):
        if isinstance(self.value, unicode):
            # Don't throw a new exception if value.decode is not valid
            try:
                self.value=self.value.decode()
            except Exception:
                pass
            return repr(self.value)
        else:
            return self.value

# $Log: ComExceptions.py,v $
# Revision 1.9  2010-05-27 08:50:40  marc
# added return value even if it is not unicode.
#
# Revision 1.8  2010/02/05 12:20:57  marc
# - bugfix for recursive instantiation
#
# Revision 1.7  2009/09/28 15:12:42  marc
# moved to storage and scsi packages
#
# Revision 1.6  2009/07/22 08:37:40  marc
# fedora compliant
#
# Revision 1.5  2008/02/28 14:20:11  marc
# - added tests
#
# Revision 1.4  2007/02/27 15:55:26  mark
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
