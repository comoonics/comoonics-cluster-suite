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
Created on 31.03.2011

@author: marc
'''

import copy
           
class Package(object):
    HASHKEYS=["name", "architecture", "version", "subversion"]
    PACKAGE_PROPERTY_NAMES=["name", "architecture", "version", "subversion"]
    DEFAULT_HASHLEVEL=4
    UPDATE_METHODS={"architecture": "update_architecture", "version": "update_version", "subversion": "update_subversion"}
    def __init__(self, *args, **valuekeys):
        self.sources=0
        self.index=0
        self.hashlevel=self.DEFAULT_HASHLEVEL
        self.hashfunction=self._genhash
        if valuekeys and len(valuekeys.keys()):
            for key in valuekeys.keys():
                setattr(self, key, valuekeys[key])
        elif args and len(args)==1 and isinstance(args[0], dict):
            self.__dict__=copy.copy(args[0])
        elif args and (len(args)==4 or len(args)==6):
            i=0
            for name in [ "name", "version", "subversion", "architecture"]:
                setattr(self,name,args[i])
                i+=1
            if len(args)>4:
                # allsources need to be set before because otherwise it can not be implicitly referred to in self.sources=.. (setattr..)
                self.allsources=args[i+1]
                self.sources=args[i]
        else:
            raise TypeError("Could not create package object because wrong usage of constructor.")
        if not hasattr(self, "sources"):
            self.sources=0x0
        if not hasattr(self, "allsources"):
            self.allsources=list()

    def getPackagePropertyNames(self):
        return self.PACKAGE_PROPERTY_NAMES
    
    """
    The idea is to extend the attributes so that multiple packages with different versions/subversions and different sources can be 
    grouped together. For this the attributes must be extended to lists to hold the differences..
    For this updatemethods might be used.
    Nevertheless this implementation for now is postponed as having one package eachs should be enough information.
    """
    def getUpdateAttributeMethod(self, attrname):
        #FIXME: never tested never implemented!!
        if self.UPDATE_METHODS.has_key(attrname):
            updatemethod=self.UPDATE_METHODS[attrname]
            method=getattr(self, updatemethod, "update_attribute")
            return method

    """
    Should be implemented with the updatemethods specified in the UPDATE_METHODS dependent on each attribute to be used.
    """
    def update(self, package):
        #FIXME: never tested never implemented!!
        pass

    def addsource(self, sources):
        index=-1
        if isinstance(sources, list):
            for source in sources:
                self.addsource(source)
        elif isinstance(sources,basestring):
            try:
                index=self.allsources.index(sources)
            except ValueError:
                index=len(self.allsources)
                self.allsources.append(sources)
            self.sources|=1<<index
        elif sources:
            self.sources|=sources
        return sources

    def delsource(self, source):
        index=self.allsources.index(source)
        self.sources^=1<<index
        return source            

    def resolvesources(self):
        sources=list()
        for i in range(len(self.allsources)):
            if self.sources & 1<<i:
                sources.append(self.allsources[i])
        return sources

    def cmp(self, pkg2, deep=False):
        if not deep:
            return cmp(hash(self), hash(pkg2))
        else:
            if hash(self) != hash(pkg2):
                return cmp(hash(self), hash(pkg2))
            else:
                return cmp(self.sources, pkg2.sources)

    def copy(self):
        return Package(self.__dict__)

    def findhash(self, package, includesources=False):
        hashlevel=self.hashlevel
        for hashlevel in range(self.hashlevel, len(self.HASHKEYS)):
            if self.hashfunction(hashlevel)!=package.hashfunction(hashlevel) or (includesources and self.sources & package.sources==0):
                return hashlevel
        return hashlevel+1

    def hashstring(self, hashlevel=0):
        if hashlevel==0:
            hashlevel=getattr(self, "hashlevel", self.DEFAULT_HASHLEVEL)
        hashkey=""
        for key in self.HASHKEYS[:hashlevel]:
            hashkey+=getattr(self, key, "")
        return hashkey

    def _genhash(self, hashlevel=0):
        hashkey=hash(self.hashstring(hashlevel))
        setattr(self, "hash", hashkey)
        return hashkey
    
    def __setattr__(self, name, value):
        if name == "sources" and isinstance(value, list):
            if not hasattr(self, "allsources"):
                self.allsources=value
            for source in value:
                self.addsource(source)
        else:
            object.__setattr__(self, name, value)
    
    def __hash__(self):
        return getattr(self, "hash", self.hashfunction())

    def __cmp__(self, otherpackage):
        return self.cmp(otherpackage)
    
    def __str__(self):
        return getattr(self, "name", "unknown")+"-"+getattr(self, "version", "0.0")+"-"+getattr(self, "subversion", "")+"."+getattr(self, "architecture", "noarch")
    
    def __repr__(self):
        return "Package(name=\"%s\", architecture=\"%s\", version=\"%s\", subversion=\"%s\", sources=%s, allsources=%s, hashlevel=%u, index=%u)" %(getattr(self, "name"), getattr(self, "architecture"), getattr(self, "version"), getattr(self, "subversion"), self.resolvesources(), self.allsources, getattr(self, "hashlevel"), getattr(self, "index", 0))

class Packages:
    def __init__(self, *args, **kwds):
        self.packages=dict()
        self.sources=list()
        self.numpackages=0
        if args:
            if isinstance(args[0], dict):
                self.packages=copy.deepcopy(args[0])
            elif len(args)==1 and isinstance(args[0], list):
                self.sources=args[0]
            else:
                first=False
                for package in args:
                    self.packages[hash(package)]=package
                    if not first:
                        self.sources=package.allsources
                        first=True
        if kwds:
            for key in kwds.keys():
                self.packages[key]=kwds[key]

    def copy(self):
        return Packages(self.packages)

    def add(self, package, sources=None, includesources=False):
        if not sources:
            sources=package.sources
        try:
            package2=self[hash(package)]
            maxhashlevel=len(package2.HASHKEYS)
            hashlevel=package2.hashlevel
            if hashlevel < maxhashlevel:
                del self.packages[package2]
                hashlevel=package2.findhash(package, includesources=includesources)
                package2.hashlevel=hashlevel
                package2.hash=package2.hashfunction()
            package.hashlevel=package2.hashlevel
            package.hash=package.hashfunction()
            if hash(package2) == hash(package):
                package2.update(package)
                package2.addsource(sources)
#                self.packages[hash(package2)]=package2
            else:
                package.addsource(sources)
                self.add(package)
                self.add(package2)
        except KeyError:
            self[hash(package)]=package
            package.allsources=self.sources
            package.addsource(sources)
        
    def remove(self, package):
        key=hash(package)
        if self.packages.has_key(key):
            package2=self.packages[key]
            package2.sources^=package.sources
            if package2.sources==0:
                del self.packages[key]
        else:
            raise KeyError(key)
        
    def differences(self):
        if len(self.sources) == 1:
            return copy.copy(self)
        else:
            differences=Packages()
            differences.sources=self.sources
            allsources=(1<<len(self.sources))-1
            for package in self.packages.values():
                if package.sources < allsources:
                    package.hash=None
                    package.hashlevel=package.DEFAULT_HASHLEVEL
                    differences.add(package, includesources=True)
            return differences

    def keys(self):
        return self.packages.keys()
    
    def values(self):
        return self.packages.values()
    
    def items(self):
        return self.packages.items()

    def iterkeys(self):
        return self.packages.iterkeys()

    def iterrange(self, fromnum, tonum, iterable=None):
        import itertools
        import types
        if not iterable:
            iterable=self.values()
        elif type(iterable) is types.FunctionType or type(iterable) is types.MethodType or \
            type(iterable) is types.BuiltinFunctionType or type(iterable) is types.BuiltinMethodType:
            iterable=iterable()
        if fromnum<=0 and tonum<=0:
            return iterable
        else:
            return itertools.islice(iterable, fromnum, tonum)

    def sort(self):
        sorted=copy.copy(self.packages.values())
        sorted.sort(lambda pkg1, pkg2: cmp(pkg1.hashstring().lower(), pkg2.hashstring().lower()))
        return sorted

    def cmp(self, packages, deep=False):
        if len(self)!=len(packages):
            return False
        for package in self.packages.values():
            if not package in packages:
                return False
            elif not package.cmp(packages[package], True):
                return False
        return True

    def __len__(self):
        return len(self.packages)
    
    def __iter__(self):
        return self.packages.__iter__()

    def __eq__(self, packages):
        return self.cmp(packages)==0

    def __contains__(self, package):
        try:
            package2=self.packages[hash(package)]
            return package.cmp(package2, True)==0
        except KeyError:
            return False
    
    def __getitem__(self, key):
        return self.packages[key]
    
    def __setitem__(self, key, package):
        if self.packages.has_key(hash(package)):
            self.packages[hash(package)].sources|=package.sources
        else:
            self.packages[hash(package)]=package
            package.index=self.numpackages
            self.numpackages+=1
            
    def __delitem__(self, key):
        if isinstance(key, Package):
            self.remove(key)
            self.numpackages-=1
        else:
            self.remove(self.packages[key])
        
    def __str__(self):
        return ",\n".join(map(str, self.packages.values()))
    
    def __repr__(self):
        return "Packages(\n\t"+",\n\t".join(map(repr, self.packages.values()))+"\n)"

class PackagesIterator(object):
    def __init__(self, *args, **kwds):
        '''
        Constructor
        '''
        self.validattributes=list()
        self.packages=None
        self.frompackage=0
        self.topackage=0
        self.packagefilter=None
        self.packagehashfilter=None
        self.iter=None
        if args:
            self.packages=args[0]

    def filter(self, package, myfilter=None):
        if not myfilter:
            myfilter=getattr(self, "packagefilter")
        if not myfilter:
            return True
        if isinstance(myfilter, basestring):
            pass

    def filterhash(self, package, myfilter=None):
        if not myfilter:
            myfilter=getattr(self, "packagehashfilter")
        if not myfilter:
            return True
        if isinstance(myfilter, basestring):
            pass

    def iterate(self, **kwds):
        self._setupkwds(**kwds)
        return getattr(self, "packages").iterrange(getattr(self, "frompackage"), getattr(self, "topackage"), getattr(self, "iter"))

    def _setupkwds(self, **kwds):
        for attributename in self.validattributes:
            value=kwds.get(attributename, getattr(self, attributename))
            setattr(self, attributename, value)

    def __iter__(self, **kwds):
        return self.iterate(**kwds)
          
    def __setattr__(self, name, value):
        if name != "validattributes" and not name in self.validattributes:
            self.validattributes.append(name)
        self.__dict__[name]=value
        
###############
# $Log:$