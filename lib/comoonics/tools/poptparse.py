"""A powerful, extensible, and easy-to-use option parser.

By Greg Ward <gward@python.net>

Originally distributed as Optik.

For support, use the optik-users@lists.sourceforge.net mailing list
(http://lists.sourceforge.net/lists/listinfo/optik-users).

Simple usage example:

   from optparse import OptionParser

   parser = OptionParser()
   parser.add_option("-f", "--file", dest="filename",
                     help="write report to FILE", metavar="FILE")
   parser.add_option("-q", "--quiet",
                     action="store_false", dest="verbose", default=True,
                     help="don't print status messages to stdout")

   (options, args) = parser.parse_args()
"""

# $Id:  $
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

__version__ = "$Revision: $"
# $Source: $

'''
Created on 25.03.2011

@author: marc
'''

from optparse import Option, OptionParser, OptionError
import sys
import os.path

class PersistentOption(Option):
#    def _check_recurring(self):
#        if hasattr(self, "recurring") and type(getattr(self, "recurring")) == bool:
#            return True
#        else:
#            raise OptionError(
#                    "recurring is expected as boolean. Got %s"
#                    % self.recurring)
#    def __init__(self, *opts, **attrs):
#        PersistentOption.__init__(self, *opts, **attrs)
#        self.ATTRS.append("recurring")
#        self.CHECK_METHODS.append(self._check_recurring)

    def check_value(self, opt, value):
        if self.action == "store_true" or self.action =="store_false" and isinstance(value, basestring):
            value=bool(value)
        return Option.check_value(self, opt, value)
#    def isRecurring(self):
#        return self.recurring

class PersistentOptionParser(OptionParser):
    def __init__(self,
                 usage=None,
                 option_list=None,
                 option_class=PersistentOption,
                 version=None,
                 conflict_handler="error",
                 description=None,
                 formatter=None,
                 add_help_option=True,
                 prog=None,
                 globaldefaultsfile=None,
                 localdefaultsfile=None,
                 localdefaultsenvkey=None):
        '''
        Constructor
        '''
        OptionParser.__init__(self, usage=usage, option_list=option_list, option_class=option_class, version=version, 
                              conflict_handler=conflict_handler, description=description, formatter=formatter, 
                              add_help_option=add_help_option, prog=prog)
        self.defaultfiles=list()
        self.setGlobalDefaultsFilename(globaldefaultsfile)
        self.setLocalDefaultsFilename(localdefaultsfile, localdefaultsenvkey)
        if self.prog is None:
            self.prog=os.path.basename(sys.argv[0])

        
    def setGlobalDefaultsFilename(self, filename):
        self._setDefaultsFilename(filename, 0)
        
    def setLocalDefaultsFilename(self, filename, envkey=None):
        self._setDefaultsFilename(filename)
        if envkey and os.environ.has_key(envkey):
            self._setDefaultsFilename(os.environ[envkey])
        
    def get_default_values(self):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(self.defaultfiles)
        try:
            if config.has_section(self.prog):
                for key in config.options(self.prog):
                    self.defaults[key]=config.get(self.prog, key)
        except KeyError:
            pass
        return OptionParser.get_default_values(self)
        
    def _setDefaultsFilename(self, filename, index=None):
        if filename and os.path.isfile(filename):
            if index==None:
                self.defaultfiles.append(filename)
            else:
                self.defaultfiles.insert(index, filename)

make_option = PersistentOption
###############
# $Log:$