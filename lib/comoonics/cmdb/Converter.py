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

from Packages import Package, PackagesIterator

_converters_registry=dict()

def registerConverter(_class):
    _converters_registry["%s/%s" %(_class.converterformat, _class.outputformat.__name__)]=_class

def getConverters():
    return _converters_registry.values()

def getConverterkeys():
    return _converters_registry.keys()

def getConverter(type):
    return _converters_registry.get(type)

class PackagesConverter(PackagesIterator):
    '''
    classdocs
    '''

    converterformat=None
    outputformat=None

    def __init__(self, packages=None):
        '''
        Constructor
        '''
        PackagesIterator.__init__(self, packages)
        self.installedstring="installed"
        self.notinstalledstring="not installed"
        self.columnnames=list()

    def getnumcols(self):
        return len(self.columnnames)
        
    def convert(self, **kwds):
        isfirst=True
        if not self.iter and self.packages:
            self.iter=self.packages.sort
        for package in self.iterate(**kwds):
            if isfirst:
                self.addcolumnnames(package)
                isfirst=False
            if (getattr(self, "packagehashfilter") and self.filterhash(package, getattr(self, "packagehashfilter"))) or (getattr(self, "packagefilter") and self.filter(package, getattr(self, "packagefilter"))) or (not getattr(self, "packagefilter") and not getattr(self, "packagehashfilter")):
                self.add(package)

    def addcolumnnames(self, package):
        pass

    def add(self, package):
        pass
    
    def getvalue(self):
        pass
    
    def getallvalues(self):
        return { "value": self.getvalue(), "colnames": getattr(self, "columnnames")}
    
class TableConverter(PackagesConverter):
    converterformat="diffs"
    outputformat=list
    def __init__(self, packages=None):
        PackagesConverter.__init__(self, packages)
        self.rows=list()
    
    def addcolumnnames(self, package):
        self.columnnames=list(Package.PACKAGE_PROPERTY_NAMES)
        self.columnnames.extend(package.allsources)
    
    def add(self, package):
        # add properties
        row=map(lambda propertyname, properties=package: getattr(properties, propertyname), Package.PACKAGE_PROPERTY_NAMES)
        for index in range(len(package.allsources)):
            # if the package is not installed at this source
            if package.sources & 1<<index == 0:
                row.append(getattr(self, "notinstalledstring"))
            else:
                row.append(getattr(self, "installedstring"))
        self.rows.append(row)
        return row
        
    def getvalue(self):
        return self.rows
registerConverter(TableConverter)

class TableMasterConverter(TableConverter):
    converterformat="masterdiffs"
    outputformat=list
    PACKAGE_PROPERTIES_GENERAL=["name", "architecture"]
    def __init__(self, packages=None, master=None):
        TableConverter.__init__(self, packages)
        self.master=master
        self.masterstr="master: %s" 
        self.sourcestr="source: %s"
        self.sourcenamestr="name"
         
    def addcolumnnames(self, package):
        self.columnnames.append(getattr(self, "sourcestr") %getattr(self, "sourcenamestr"))
        self.columnnames.extend(filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))
        self.columnnames.extend(map(lambda pname: getattr(self, "masterstr") %pname, filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        self.columnnames.extend(map(lambda pname: getattr(self, "sourcestr") %pname, filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        
    def add(self, package):
        masterinstalled=False
        # set masterpackage if this one is installed on the master
        masteridx=getattr(self, "packages").sources.index(getattr(self, "master"))
        if package.sources & 1<<masteridx > 0:
            masterinstalled=True
        for sourceidx in range(len(self.packages.sources)):
            # if this is the sourceindex for the master skip
            if sourceidx == masteridx:
                continue
            # this package is not installed on this node and not on the master (skip it)
            elif 1<<sourceidx & package.sources == 0 and not masterinstalled:
                continue
            # if this package is not installed on this node but on the master list it
            elif 1<<sourceidx & package.sources == 0 and masterinstalled:
                self._addpackage(package, sourceidx, masterinstalled)
            # if this package is installed but not on the master list also
            elif 1<<sourceidx & package.sources > 0 and not masterinstalled:
                self._addpackage(package, sourceidx, masterinstalled)

    def _addpackage(self, package, sourceidx, masterinstalled):
        row=list()
        row.append(self.packages.sources[sourceidx])
        row.extend(map(lambda pname: getattr(package, pname), 
                       filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        if masterinstalled:
            row.extend(map(lambda pname: getattr(package, pname), 
                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
            row.extend(map(lambda pname: getattr(self, "notinstalledstring"), 
                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        else:
            row.extend(map(lambda pname: getattr(self, "notinstalledstring"), 
                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
            row.extend(map(lambda pname: getattr(package, pname, getattr(self, "notinstalledstring")), 
                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        self.rows.append(row)
        return row
registerConverter(TableMasterConverter)
    
class DictConverter(PackagesConverter):
    converterformat="diffs"
    outputformat=dict
    def __init__(self, packages=None):
        PackagesConverter.__init__(self, packages)
        self.rows=list()
    
    def addcolumnnames(self, package):
        self.columnnames=list(Package.PACKAGE_PROPERTY_NAMES)
        self.columnnames.extend(package.allsources)
    
    def add(self, package):
        # add properties
        row=dict()
        for propertyname in Package.PACKAGE_PROPERTY_NAMES:
            row[propertyname]=getattr(package, propertyname)
        for index in range(len(package.allsources)):
            # if the package is not installed at this source
            if package.sources & 1<<index == 0:
                row[package.allsources[index]]=getattr(self, "notinstalledstring")
            else:
                row[package.allsources[index]]=getattr(self, "installedstring")
        getattr(self, "rows").append(row)
        return row
        
    def getvalue(self):
        return getattr(self, "rows")
registerConverter(DictConverter)

class DictMasterConverter(DictConverter):
    converterformat="masterdiffs"
    outputformat=dict
    PACKAGE_PROPERTIES_GENERAL=["name", "architecture"]
    def __init__(self, packages, master=None):
        DictConverter.__init__(self, packages)
        self.master=master
        self.masterstr="master: %s"
        self.sourcestr="source: %s"
        self.sourcenamestr="name"
        
    def addcolumnnames(self, package):
        self.columnnames.append(getattr(self, "sourcestr") %getattr(self, "sourcenamestr"))
        self.columnnames.extend(filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))
        self.columnnames.extend(map(lambda pname: getattr(self, "masterstr") %pname, filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        self.columnnames.extend(map(lambda pname: getattr(self, "sourcestr") %pname, filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        
    def add(self, package):
        masterinstalled=False
        # set masterpackage if this one is installed on the master
        masteridx=getattr(self, "packages").sources.index(getattr(self, "master"))
        if package.sources & 1<<masteridx > 0:
            masterinstalled=True
        for sourceidx in range(len(self.packages.sources)):
            # if this is the sourceindex for the master skip
            if sourceidx == masteridx:
                continue
            # this package is not installed on this node and not on the master (skip it)
            elif 1<<sourceidx & package.sources == 0 and not masterinstalled:
                continue
            # if this package is not installed on this node but on the master list it
            elif 1<<sourceidx & package.sources == 0 and masterinstalled:
                self._addpackage(package, sourceidx, masterinstalled)
            # if this package is installed but not on the master list also
            elif 1<<sourceidx & package.sources > 0 and not masterinstalled:
                self._addpackage(package, sourceidx, masterinstalled)

    def _addpackage(self, package, sourceidx, masterinstalled):
        row=dict()
        row[self.columnnames[0]]=self.packages.sources[sourceidx]
        for pname in filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES):
            row[pname]=getattr(package, pname)
        for pname in filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES):
            if masterinstalled:
                row[getattr(self, "masterstr") %pname]=getattr(package, pname)
                row[getattr(self, "sourcestr") %pname]=getattr(self, "notinstalledstring")
            else:
                row[getattr(self, "sourcestr") %pname]=getattr(package, pname)
                row[getattr(self, "masterstr") %pname]=getattr(self, "notinstalledstring")
        getattr(self, "rows").append(row)
        return row
registerConverter(DictMasterConverter)

class DictConverterColAdd(DictConverter):
    converterformat="coladddiffs"
    outputformat=dict
    def __init__(self, packages=None, colname="id", idcolvalues=["id1", "id2"]):
        DictConverter.__init__(self, packages)
        self.idcolname=colname
        self.idcolvalues=idcolvalues
        self.numpackages=0

    def addcolumnnames(self, package):
        DictConverter.addcolumnnames(self, package)
        getattr(self, "columnnames").append(getattr(self, "idcolname"))

    def add(self, package):
        row=DictConverter.add(self, package)
        row[getattr(self, "idcolname")]=getattr(self, "idcolvalues")[getattr(self, "numpackages")%len(getattr(self, "idcolvalues"))]
        setattr(self, "numpackages", getattr(self,"numpackages")+1)
registerConverter(DictConverterColAdd)

class DictMasterConverterColAdd(DictMasterConverter):
    converterformat="coladdmasterdiffs"
    outputformat=dict
    def __init__(self, packages=None, master=None, colname="id", idcolvalues=["id1", "id2"]):
        DictMasterConverter.__init__(self, packages, master)
        self.idcolname=colname
        self.idcolvalues=idcolvalues
        self.numpackages=0

    def addcolumnnames(self, package):
        DictMasterConverter.addcolumnnames(self, package)
        getattr(self, "columnnames").append(getattr(self, "idcolname"))

    def _addpackage(self, package, sourceidx, masterinstalled):
        row=DictMasterConverter._addpackage(self, package, sourceidx, masterinstalled)
        row[getattr(self, "idcolname")]=getattr(self, "idcolvalues")[getattr(self, "numpackages")%len(getattr(self, "idcolvalues"))]
        setattr(self, "numpackages", getattr(self,"numpackages")+1)
registerConverter(DictMasterConverterColAdd)
    
###############
# $Log:$