#!/usr/bin/python
"""analysis.ComoonicsWriters

analysis writer baseclasses for other writers

"""

# here is some internal information
# $Id $
#

import logging
import sys
from ComObjects import BaseObject

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComWriters.py,v $

class DictWriter(object):
    logger=logging.getLogger("comoonics.ComGFS.DictWriter")
    NAME=None
    def __init__(self, _out=sys.stdout):
        self.out=_out
        self.print_only_value=True
        self.prefix=None
        self.prefix_delim="."
        self.writehead=True
        self.writetail=False
        self.writebegin=False
        self.writeend=False        
        self.only_values=False
        self.filteredKeys=None

    def write(self, _dict, _tabs=0, _head=True, _tail=True, _actkey=None):
        if self.writehead and _head:
            self.writeHead(_dict, _tabs)
        else:
            _tabs=_tabs-1
        _keys=None
        if self.filteredKeys:
            if not _actkey and type(_dict)==dict:
                _actkey="default"
            elif not _actkey:
                if self.filteredKeys.has_key(_dict.__class__.__name__):
                    _actkey=_dict.__class__.__name__
                else:
                    _actkey="default"
            if self.filteredKeys.has_key(_actkey):
                self.logger.debug("Setting filteredKeys %s" %_actkey)
                _keys=self.filteredKeys[_actkey]
        if not _keys and type(_dict)==dict:
            _keys=_dict.keys()
            _keys.sort()
        elif not _keys and isinstance(_dict, BaseObject):
            _keys=_dict.__dict__.keys()
            _keys.sort()
        elif not _keys:
            _keys=list()
            self._write(_dict, _tabs)
        for key in _keys:
            if type(_dict)==dict and not _dict.has_key(key):
                self.filterDictValue(key)
                continue
            elif not hasattr(_dict, key):
                self.filterDictValue(key)
                continue
            if type(_dict)==dict:
                value=_dict[key]
            elif isinstance(_dict, BaseObject):
                value=getattr(_dict, key)
            else:
                raise TypeError(_dict)
            if key.find("__")>=0 and key.startswith("_"):
                continue
            if isinstance(value, basestring) or type(value)==int or type(value)==float or type(value)==long or type(value)==bool:
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeKeyValue(key, value, _tabs+1)
            elif type(value)==dict or isinstance(value, BaseObject):
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeDictValue(key, value, _tabs+1)
            elif type(value)==list or type(value)==tuple:
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeTupleValue(key, value, _tabs+1)
        if self.writetail and _tail:
            self.writeTail(_dict, _tabs)

    def formatPrefix(self, _dict):
        buf=""
        if self.prefix:
            buf="%s%s" %(self.getPrefix(_dict), self.prefix_delim)
        return buf

    # Methods to be overwritten defaults to just output

    def filterDictValue(self, key):
        pass

    def getPrefix(self, _dict):
        if _dict.has_key(self.prefix):
            return _dict[self.prefix]
        else:
            return self.prefix

    def writeHead(self, _dict, _tabs=0):
        if type(_dict)==dict and not self.only_values:
            if _dict.has_key("__name__") and _dict.has_key("__info__"):
                self._write("%s(%s)\n" %(_dict["__name__"], _dict["__info__"]), _tabs)
            elif _dict.has_key("__name__"):
                self._write("%s\n" %(_dict["__name__"]), _tabs)
        elif isinstance(_dict, BaseObject) and not self.only_values:
            if hasattr(_dict, "__info__"):
                self._write("%s(%s)\n" %(_dict.__class__.__name__, _dict.__info__), _tabs)
            else:
                self._write("%s\n" %(_dict.__class__.__name__), _tabs)

    def writeKeyValue(self, _key, _value, _tabs=0):
        if not self.only_values and (not self.print_only_value or _value):
            self._write("%s = %s\n" %(_key, str(_value)), _tabs)
        elif self.only_values:
            self._write("%s\n" %(str(_value)))

    def writeDictValue(self, _key, _dict, _tabs=0):
        #self._write("dict<%s>\n" %_key, _tabs)
        self.write(_dict, _tabs)

    def writeTupleValue(self, _key, _tuple, _tabs=0):
        if _key.startswith("_") and not _key.startswith("__"):
            for _value in _tuple:
                self.write(_value, _tabs)
        elif not _key.startswith("__"):
#            self._write(_key+"\n")
#           self.write(_value, _tabs)
            self.writeKeyValue(_key, ",".join(_tuple), _tabs)

    def writeTail(self, _dict, _tabs=0):
        pass

    def writeBegin(self):
        pass

    def writeEnd(self):
        pass

    def _write(self, _str, _tabs=0):
        self.out.write("\t"*_tabs+_str.expandtabs())
    
    def isSupported(self):
        return False

###################
# $Log: ComWriters.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#