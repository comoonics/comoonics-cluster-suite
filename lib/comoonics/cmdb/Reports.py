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
import sys

_reports_registry=dict()

def registerReport(_class):
    _reports_registry["%s/%s" %(_class.reportformat, _class.outputformat)]=_class

def getReports():
    return _reports_registry.values()

def getReportkeys():
    return _reports_registry.keys()

def getReport(type):
    return _reports_registry.get(type)

class ReportPackages(PackagesIterator):
    reportformat="diffs"
    outputformat="text/plain"
    def __init__(self, packages=None):
        PackagesIterator.__init__(self, packages)
        self.outputchannel=sys.stdout
        self.withheader=True
        self.withfooter=True
        self.coldelimiter=""
        self.colwidths=None
        self.colwidth=30
        self.linesep="\n"
        self.linechar="-"
        self.linesize=0
        self.notinstalledstring="not installed"
        self.installedstring="installed"
        self.master=None
        self.colformater="%s"
        if self.packages and not self.iter:
            self.iter=self.packages.sort
    
    def line(self):
        if self.linechar:
            self.outputchannel.write(self.linechar*self.linesize)
            self.outputchannel.write(self.linesep)
    
    def header(self):
        if not self.colwidths:
            self.colwidths=self.setupcolwidths(self.colwidth)
        header=self.coldelimiter.join(map(lambda pname: (self.colformater %pname).center(self.colwidths[Package.PACKAGE_PROPERTY_NAMES.index(pname)]), Package.PACKAGE_PROPERTY_NAMES))+self.coldelimiter
        if len(self.packages.sources)>1:
            header+=self.coldelimiter.join(map(lambda source: (self.colformater %source).center(self.colwidths[len(Package.PACKAGE_PROPERTY_NAMES)+self.packages.sources.index(source)]), self.packages.sources))
        header+=self.linesep
        self.outputchannel.write(header)
        self.linesize=len(header)
        self.line()
    
    def footer(self):
        self.line()
    
    def format(self, package):
        self.outputchannel.write(self.coldelimiter.join(map(lambda propertyname, properties=package: self.colformater %getattr(properties, propertyname).ljust(self.colwidths[Package.PACKAGE_PROPERTY_NAMES.index(propertyname)]), Package.PACKAGE_PROPERTY_NAMES)))
        self.outputchannel.write(self.coldelimiter)
        if len(package.allsources)>1:
            for index in range(len(package.allsources)):
                if package.sources & 1<<index == 0:
                    self.outputchannel.write((self.colformater %self.notinstalledstring).ljust(self.colwidths[len(Package.PACKAGE_PROPERTY_NAMES)+index]))
                else:
                    self.outputchannel.write((self.colformater %self.installedstring).ljust(self.colwidths[len(Package.PACKAGE_PROPERTY_NAMES)+index]))
                self.outputchannel.write(self.coldelimiter)
        self.outputchannel.write(self.linesep)
                
    def filter(self, package, myfilter=None):
        if not myfilter:
            myfilter=self.packagefilter
        if not myfilter:
            return True
        if isinstance(myfilter, basestring):
            pass

    def filterhash(self, package, myfilter=None):
        if not myfilter:
            myfilter=self.packagehashfilter
        if not myfilter:
            return True
        if isinstance(myfilter, basestring):
            pass

    def getnumcols(self):
        return len(Package.PACKAGE_PROPERTY_NAMES)+len(self.packages.sources)
    
    def setupcolwidths(self, colwidth=30):
        colwidths=map(lambda x: colwidth, range(self.getnumcols()))
        return colwidths
    
    def report(self, **kwds):
        self._setupkwds(**kwds)
        if not self.iter and self.packages:
            self.iter=self.packages.sort
        if self.withheader:
            self.header()
        for package in self.iterate(**kwds):
            if (self.packagehashfilter and self.filterhash(package, self.packagehashfilter)) or (self.packagefilter and self.filter(package, self.packagefilter)) or (not self.packagefilter and not self.packagehashfilter):
                self.format(package)
        if self.withfooter:
            self.footer()
registerReport(ReportPackages)

class CSVReportPackages(ReportPackages):
    reportformat="diffs"
    outputformat="text/csv"
    def __init__(self, packages=None, coldelimiter=",", colformater="\"%s\""):
        ReportPackages.__init__(self, packages)
        self.coldelimiter=coldelimiter
        self.linechar=None
        self.colwidth=0
        self.colformater=colformater
registerReport(CSVReportPackages)

class MasterReportPackages(ReportPackages):
    PACKAGE_PROPERTIES_GENERAL=["name", "architecture"]
    reportformat="masterdiffs"
    outputformat="text/plain"
    def __init__(self, packages=None, master=None):
        ReportPackages.__init__(self, packages)
        self.masterstr="master: %s"
        self.sourcestr="source: %s"
        self.sourcenamestr="name"
        self.master=master

    def getnumcols(self):
        p1=len(Package.PACKAGE_PROPERTY_NAMES)
        p2=len(self.PACKAGE_PROPERTIES_GENERAL)
        # 2xproperties that differe + properties who are common + source
        return (p1-p2)*2+p1+1

    def header(self):
        if not self.colwidths:
            self.colwidths=self.setupcolwidths(self.colwidth)
        header=(self.colformater %(self.sourcestr %self.sourcenamestr)).center(self.colwidths[0])+self.coldelimiter
        header+=self.coldelimiter.join(map(lambda pname: self.colformater %pname.center(self.colwidths[1+self.PACKAGE_PROPERTIES_GENERAL.index(pname)]), 
                                           filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        header+=self.coldelimiter
        header+=self.coldelimiter.join(map(lambda pname: (self.colformater %(self.masterstr %pname)).center(self.colwidths[1+len(self.PACKAGE_PROPERTIES_GENERAL)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        header+=self.coldelimiter
        header+=self.coldelimiter.join(map(lambda pname: (self.colformater %(self.sourcestr %pname)).center(self.colwidths[1+len(Package.PACKAGE_PROPERTY_NAMES)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                           filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES)))
        self.outputchannel.write(header)
        self.outputchannel.write(self.linesep)
        self.linesize=len(header)
        self.line()
        
    def format(self, package):
        masterinstalled=False
        # set masterpackage if this one is installed on the master
        masteridx=self.packages.sources.index(self.master)
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
                self.writePackage(package, sourceidx, masterinstalled)
            # if this package is installed but not on the master list also
            elif 1<<sourceidx & package.sources > 0 and not masterinstalled:
                self.writePackage(package, sourceidx, masterinstalled)

    def writePackage(self, package, sourceidx, masterinstalled):
        self.outputchannel.write((self.colformater %self.packages.sources[sourceidx]).ljust(self.colwidths[0])+self.coldelimiter)
        self.outputchannel.write(self.coldelimiter.join(map(lambda pname: (self.colformater %getattr(package, pname)).ljust(self.colwidths[1+self.PACKAGE_PROPERTIES_GENERAL.index(pname)]), 
                                                            filter(lambda package: package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))))
        self.outputchannel.write(self.coldelimiter)
        if masterinstalled:
            self.outputchannel.write(self.coldelimiter.join(map(lambda pname: (self.colformater %getattr(package, pname)).ljust(self.colwidths[1+len(Package.PACKAGE_PROPERTY_NAMES)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                                                filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))))
            self.outputchannel.write(self.coldelimiter)
            self.outputchannel.write(self.coldelimiter.join(map(lambda pname: (self.colformater %self.notinstalledstring).ljust(self.colwidths[1+len(Package.PACKAGE_PROPERTY_NAMES)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                                                filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))))
        else:
            self.outputchannel.write(self.coldelimiter.join(map(lambda pname: (self.colformater %self.notinstalledstring).ljust(self.colwidths[1+len(Package.PACKAGE_PROPERTY_NAMES)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                                                filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))))
            self.outputchannel.write(self.coldelimiter)
            
            self.outputchannel.write(self.coldelimiter.join(map(lambda pname: (self.colformater %getattr(package, pname, self.notinstalledstring)).ljust(self.colwidths[1+len(Package.PACKAGE_PROPERTY_NAMES)+Package.PACKAGE_PROPERTY_NAMES.index(pname)]), 
                                                                filter(lambda package: not package in self.PACKAGE_PROPERTIES_GENERAL, Package.PACKAGE_PROPERTY_NAMES))))
        self.outputchannel.write(self.linesep)
registerReport(MasterReportPackages)

class CSVMasterReportPackages(MasterReportPackages):
    reportformat="masterdiffs"
    outputformat="text/csv"
    def __init__(self, packages=None, master=None, coldelimiter=",", colformater="\"%s\""):
        MasterReportPackages.__init__(self, packages, master)
        self.coldelimiter=coldelimiter
        self.linechar=None
        self.colwidth=0
        self.colformater=colformater
registerReport(CSVMasterReportPackages)
        
###############
# $Log:$