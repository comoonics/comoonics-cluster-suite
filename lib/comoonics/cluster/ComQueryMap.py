'''
Created on Apr 27, 2009

@author: marc
'''

import ConfigParser
import comoonics.cluster
from comoonics.cluster.ComClusterInfo import RedHatClusterInfo

class QueryMap(ConfigParser.ConfigParser):
    '''
    classdocs
    '''

    def __init__(self, _querymapfile=comoonics.cluster.querymapfile, _clusterinfo=None):
        '''
        Constructor
        '''
        ConfigParser.ConfigParser.__init__(self)
        if isinstance(_clusterinfo, RedHatClusterInfo):
            self.mainsection="redhatcluster"
        else:
            self.mainsection="unknown"
        
    def get(self, section, option):
        if not section:
            section=self.mainsection
        self._defaults["param0"]="%(param0)s"
        return ConfigParser.ConfigParser.get(self, section, option)
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
# Revision 1.1  2009-05-27 18:31:59  marc
# - prepared and added querymap concept
# - reviewed and changed code to work with unittests and being more modular
# 