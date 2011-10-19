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
Created on 20.04.2011

@author: marc
'''

import re
import itertools
import logging

class StraceLineParser():
    logger=logging.getLogger("comoonics.analysis.StraceAnalyser.StraceLineParser")
    parsers=[re.compile('^(?P<pid>\d+)\s+(?P<timebetween>\d+\.\d+)\s+(?P<call>\S+)\((?P<params>.*)\)\s*=\s*(?P<result>.+)\s+\<(?P<timespend>\d+\.\d+)\>.*$'),
             re.compile('^(?P<pid>\d+)\s+(?P<timebetween>\d+\.\d+)\s+(?P<call>\S+)\((?P<params>.*)\)\s*=\s*(?P<result>.+)\s*$')
             ]
    """
    Parses a line of the strace output file and returns a dict of found attributes.
    """
    def __init__(self):
        self.lineno=0
    
    def attrs(self, line):
        for parser in self.parsers:
            result=parser.match(line)
            if result:
                result=result.groupdict()
                result["_number"]=self.lineno
                self.lineno+=1
                return result
        se=SyntaxError("Could not parse line number %u, %s" %(self.lineno, line))
        se.lineno=self.lineno
        raise se
    
    def parseLine(self, line):
        return self.attrs(line)

class StraceEntry(object):
    logger=logging.getLogger("comoonics.analysis.StraceAnalyser.StraceEntry")
    _attrsconverters={"timebetween": float, "timespend": float}
    """
    Represents and entry in the strace file
    """
    def __init__(self, **kwds):
        self._seperator=","
        for key in kwds.keys():
            setattr(self, key, kwds[key])
    
    def __filterattrs(self, attr):
        return not attr[0].startswith("_")
     
    def __str__(self):
        return ", ".join(map(lambda (name, value): name+": "+str(value), itertools.ifilter(self.__filterattrs, self.__dict__.items())))
                         
    def __repr__(self):
        return "StraceEntry(%s)" %", ".join(map(lambda (name, value): name+"="+repr(value), itertools.ifilter(self.__filterattrs, self.__dict__.items())))
    
    def __getconverter__(self, name):
        return self._attrsconverters.get(name, None)
    def __convert(self, name, value):
        if self.__getconverter__(name):
            return self.__getconverter__(name)(value)
        else:
            return value
    def __setattr__(self, name, value):
        if name != "_seperator":
            if isinstance(value, basestring):
                value=value.strip()
                if value.find(self._seperator)>=0:
                    value=value.split(self._seperator)
                    for i in range(len(value)):
                        value[i]=self.__convert(name, value[i].strip())
                else:
                    value=self.__convert(name, value)
        self.__dict__[name]=value

#    def __getattr__(self, name):
#        if not self.__dict__.has_key(name):
#            print "Entry: %s does not have key %s." %(self, name)
#            import traceback
#            traceback.print_stack()
#        return object.__getattribute__(self, name)

    def __eq__(self, other):
        if not other:
            return False
        for key in self.__dict__:
            if not key.startswith("_") and getattr(other, key, None) != getattr(self, key, None):
                return False
        return True

class StraceParser(object):
    logger=logging.getLogger("comoonics.analysis.StraceAnalyser.StraceParser")
    '''
    Parses an strace file and can be queried for some figures
    '''
    def __init__(self, stracefile):
        '''
        Constructor
        '''
        if stracefile:
            self.stracefile=stracefile
        if isinstance(self.stracefile, basestring):
            self.stracefile=open(self.stracefile, "r")
        self.parser=StraceLineParser()
                    
    def nextEntry(self):
        line=self.stracefile.next()
        if line:
            try:
                return StraceEntry(**self.parser.parseLine(line))
            except SyntaxError, se:
                self.logger.debug("Could not parse line. Error: %s, line: %s" %(se, line))
                return None
        else:
            return None
        
    def next(self):
        return self.nextEntry()
    
    def __iter__(self):
        return self
    
class StraceAnalyser(object):
    logger=logging.getLogger("comoonics.analysis.StraceAnalyser.StraceAnalyser")
    def __init__(self, stracefile):
        self.stracefile=stracefile
        
    def iter(self, filterfunc=None, iter=None):
        if not filterfunc:
            filterfunc=lambda x: True
        if not iter:
            iter=itertools.ifilter(filterfunc, StraceParser(self.stracefile))
        return iter
    
    def avg(self, attrname, filterfunc=None, iter=None, **kwds):
        avg=0
        count=0
        for entry in self.iter(filterfunc, iter):
            if hasattr(entry, attrname):
                avg=(avg+float(getattr(entry, attrname, 0)))
                count+=1
            
        return avg / float(count)

    def avg_call(self, attrname, filterfunc=None, iter=None, **kwds):
        return self._avg_attr(attrname, "call", filterfunc, iter)
            
    def _avg_attr(self, attrname, filterattr, filterfunc=None, iter=None, **kwds):
        avg={}
        counts={}
        entry=None
        for entry in self.iter(filterfunc, iter):
            if hasattr(entry, attrname):
                avg[getattr(entry, filterattr)]=avg.get(getattr(entry, filterattr), 0)+float(getattr(entry, attrname, 0))
                counts[getattr(entry, filterattr)]=counts.get(getattr(entry, filterattr), 0)+1
        for filterattr2 in counts.keys():
            avg[filterattr2]=avg.get(filterattr2)/float(counts.get(filterattr2))
        return avg
            
    def min(self, attrname, filterfunc=None, iter=None, **kwds):
        min=None
        for entry in self.iter(filterfunc, iter):
            if hasattr(entry, attrname):
                val=float(getattr(entry, attrname, 0))
                if min==None:
                    min=entry
                elif val<float(getattr(min, attrname, 0)):
                    min=entry
        return min 
            
    def max(self, attrname, filterfunc=None, iter=None, **kwds):
        max=None
        for entry in self.iter(filterfunc, iter):
            if hasattr(entry, attrname):
                val=float(getattr(entry, attrname, 0))
                if max==None:
                    max=entry
                elif float(getattr(max, attrname))<val:
                    max=entry
        return max 
    
    def count(self, filterfunc=None, iter=None, **kwds):
        count=0
        for entry in self.iter(filterfunc, iter):
            count+=1
        return count

    def attributevalues(self, attrname, filterfunc=None, iter=None, **kwds):
        values=list()
        for entry in self.iter(filterfunc, iter):
            if hasattr(entry, attrname):
                value=getattr(entry, attrname)
                if not value in values:
                    values.append(value)
        return values
    
    def calls(self, filterfunc=None, iter=None, **kwds):
        return self.attributevalues("call", filterfunc, iter)
    
    def min_hotspots(self, attrname, hotspots=5, filterfunc=None, iter=None, **kwds):
        import heapq
        return heapq.nsmallest(hotspots, itertools.ifilter(lambda entry: hasattr(entry, attrname), self.iter(filterfunc, iter)), lambda entry: getattr(entry, attrname))

    def max_hotspots(self, attrname, hotspots=5, filterfunc=None, iter=None, **kwds):
        import heapq
        return heapq.nlargest(hotspots, itertools.ifilter(lambda entry: hasattr(entry, attrname), self.iter(filterfunc, iter)), lambda entry: getattr(entry, attrname))

def formatResults(allresults, formats=None):
    logger=logging.getLogger("comoonics.analysis.StraceAnalyser.formatResults")
    logger.debug("allresults: %s" %allresults)
    for stracefile in allresults:
        print "--------------------------------------------------------"
        if isinstance(stracefile, basestring):
            print "File: %s" %stracefile
        results=allresults[stracefile]
        for feature in results:
            for value in results[feature]:
                result=results[feature][value]
                format=None
                if formats:
                    if formats.has_key(feature):
                        format=formats[feature]
                        if type(format)==dict:
                            if format.has_key(value):
                                format=format[value]
                            else:
                                format=None
                if not format:
                    if isinstance(result, basestring):
                        format="%(feature)s(%(attributename)s): %(result)s"
                    elif isinstance(result, float):
                        format="%(feature)s(%(attributename)s): %(result)1.7f"
                    else:
                        format="%(feature)s(%(attributename)s): %(result)s"
                if isinstance(result, StraceEntry):
                    params=dict(result.__dict__)
                else:
                    params=dict()
                params["feature"]=feature
                params["attributename"]=value
                if type(result)==list and type(format)==tuple:
                    print format[0] %(params)
                    print format[2].join(map(lambda entry: format[1] %str(entry), result))
                elif type(result)==dict and type(format)==tuple:
                    print format[0] %(params)
                    print format[2].join(map(lambda attrname: format[1] %(attrname, result[attrname]), result))
                else:
                    params["result"]=result
                    print format %(params)
###############
# $Log:$