'''
Created on Apr 27, 2009

@author: marc
'''

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

import ConfigParser
import comoonics.cluster
from comoonics.cluster.ComClusterInfo import RedHatClusterInfo

class QueryMap(ConfigParser.ConfigParser):
    '''
    classdocs
    '''

    delimitor=" "

    def __init__(self, _querymapfile=comoonics.cluster.querymapfile, _clusterinfo=None):
        '''
        Constructor
        '''
        ConfigParser.ConfigParser.__init__(self)
        if isinstance(_clusterinfo, RedHatClusterInfo):
            self.mainsection="redhatcluster"
        else:
            self.mainsection="unknown"
        self.read(_querymapfile)
        
    def get(self, section, option):
        if not section:
            section=self.mainsection
        self._defaults["param0"]="%(param0)s"
        self._defaults["param1"]="%(param1)s"
        self._defaults["param2"]="%(param2)s"
        self._defaults["param3"]="%(param3)s"
        self._defaults["param4"]="%(param4)s"
        result=ConfigParser.ConfigParser.get(self, section, option)
        if result.find(self.delimitor) > 0:
            return result.split(self.delimitor)
        else:
            return result
    def array2params(self, _array, suffix="param%s"):
        _params={}
        for _index in range(len(_array)):
            _params[suffix %_index]=_array[_index]
        return _params

    def _interpolate(self, section, option, rawval, _vars):
        # do the string interpolation
        value = rawval
        depth = ConfigParser.MAX_INTERPOLATION_DEPTH
        while depth:                    # Loop through this until it's done
            depth -= 1
            if "%(" in value:
                value = self._KEYCRE.sub(self._interpolation_replace, value)
                try:
                    value = value % _vars
                except KeyError, e:
                    raise ConfigParser.InterpolationMissingOptionError(option, section, rawval, e[0])
            else:
                break
        if not "%(param" in value and "%" in value:
            raise ConfigParser.InterpolationDepthError(option, section, rawval)
        return value
        
###########
# $Log: ComQueryMap.py,v $
# Revision 1.3  2009-09-28 15:10:04  marc
# bugfix with queries and interpretation of querymap strings
#
# Revision 1.2  2009/07/22 08:37:09  marc
# Fedora compliant
#
# Revision 1.1  2009/05/27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
# 