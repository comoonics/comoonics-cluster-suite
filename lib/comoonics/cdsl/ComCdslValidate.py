"""Comoonics cdsl validate module


Checks directories inside CDSL Link, which must be defined in a given cdslRepository, 
for existing cdsls. Append cdsls which are found to cdslRepository. Includes a special 
version of os.walk() (see L{os} for details), which skips submounts but follows symbolic links.
"""

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

__version__ = "$Revision: 1.10 $"

import os

class CdslValidate(object):
    def createDefaultRepository(clusterInfo, **keys):
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        repository=keys.get("repository", None)
        if repository:
            keys["resource"]=keys.get("resource", repository.getResource())
            keys["root"]=keys.get("root", repository.root)
            keys["mountpoint"]=keys.get("mountpoint", repository.getMountpoint())
            keys["cdsltree"]=keys.get("cdsltree", repository.getTreePath())
            keys["cdsltreeshared"]=keys.get("cdsltreeshared", repository.getSharedTreepath())
            keys["cdsllink"]=keys.get("cdsllink", repository.getLinkPath())
            keys["defaultdir"]=keys.get("defaultdir", repository.getDefaultDir())
            keys["maxnodeidnum"]=keys.get("maxnodeidnum", repository.getMaxnodeidnum())
            keys["nodeprefix"]=keys.get("nodeprefix", repository.getNodePrefix())
            keys["usenodeids"]=keys.get("usenodeids", repository.getUseNodeids())
            keys["expandstring"]=keys.get("expandstring", repository.getExpandString())
        return ComoonicsCdslRepository(clusterinfo=clusterInfo, **keys)
    createDefaultRepository=staticmethod(createDefaultRepository)

    def backupFileName(filename, idx=0):
        """
        Will create a backup filename of the given file.
        Usually this means move the file from filename => filename.cdslvalidate.%(date)
        """
        from datetime import datetime
        
        backupfilename="%s.cdslvalidate.%s.%u" %(filename, datetime.now().strftime("%Y%m%d-%H%M%S"), idx)
        if os.path.exists(backupfilename):
            idx=idx+1
            return CdslValidate.backupFileName(filename,idx)
        else:
            return backupfilename
    backupFileName=staticmethod(backupFileName)

    def backupFile(filename, backupfile=None):
        import shutil
        #from comoonics import ComSystem
        if not backupfile:
            backupfile=CdslValidate.backupFileName(filename)
        shutil.copyfile(filename, backupfile)
        # ComSystem.execLocalOutput("cp %s %s" %(filename, backupfile))
    backupFile=staticmethod(backupFile)

    def __init__(self, cdslRepository, clusterInfo, **keys):
        """
        Class that controlls the validation and repair of cdsls. All methods are consolidated under this
        class.
        """
        self.backupfiles=list()
        from comoonics import ComLog
        from xml.sax import SAXParseException
        self.logger=ComLog.getLogger("comoonics.cdsl.ComCdslValidate.CdslValidate")
        self.clusterinfo=clusterInfo
        self.cdslrepository=cdslRepository
        try:
            self.cdslrepository.lockresourceRO()
            self.cdslrepository.refresh()
        except (AttributeError, IOError, OSError, SAXParseException), error:
            if self.cdslrepository:
                self.cdslrepository.unlockresource()
                resource=os.path.join(self.cdslrepository.workingdir, self.cdslrepository.resource)
            else:
                resource=os.path.normpath(os.path.join(keys["root"], keys["mountpoint"], keys["resource"]))
            self.logger.error("Could not find read cdsl repository from %s. Trying to reconstruct." %resource)
            if os.path.exists(resource):
                _backupfile=CdslValidate.backupFileName(resource)
                self.logger.error("Backing up old repository from %s to %s" %(resource, _backupfile))
                CdslValidate.backupFile(resource, _backupfile)
                self.backupfiles.append(_backupfile)
                os.remove(resource)
            self.cdslrepository=CdslValidate.createDefaultRepository(clusterInfo, repository=self.cdslrepository, **keys)

    def walkdir(self, top=".", names=None, recursive=True, onerror=None, filter=None):
        """Directory tree generator.
    
        Modified version of os.walk(). See L{os} for details of usage.
        In contrast to os.path.walk it does not stop when hitting a symbolic 
        link, but does stop when hitting a underlying mountpoint (replaced 
        i{if not islink(path):} with i{if not ismount(path):}). Needs import 
        from error, listdir of Module L{os} to get needed globals (added i{from 
        os import error, listdir}). Removed import from method islink(). Uses method 
        ismount which is defined in this module.
        """
        from comoonics.cdsl.ComCdslRepository import CdslNotFoundException
        from comoonics.cdsl import ismount, dirtrim
        from comoonics.cdsl.ComCdsl import Cdsl    
        if not filter:
            filter=os.path.islink    

        # We may not have read permission for top, in which case we can't
        # get a list of the files the directory contains.  os.path.walk
        # always suppressed the exception then, rather than blow up for a
        # minor reason when (say) a thousand readable directories are still
        # left to visit.  That logic is copied here.
        try:
            if isinstance(top, Cdsl):
                top=top.src
            if not names:
                names = os.listdir(top)
            if isinstance(names, basestring):
                names = [ names, ]

            for name in names:
                # Only links are cdsls so far
                cdsllink=os.path.normpath(os.path.join(self.cdslrepository.workingdir, top, name))
                if not filter(cdsllink) and not os.path.isdir(cdsllink):
                    continue
                cdsl=None
                if self.cdslrepository.isExpandedDir(name):
                    continue
                cdslsrc=os.path.join(dirtrim(top), name)
                try:
                    cdsl=self.cdslrepository.getCdsl(cdslsrc)
                except CdslNotFoundException:
                    try:
                        cdsl=self.cdslrepository.guessonerror(cdslsrc, self.clusterinfo)
                    except CdslNotFoundException:
                        self.logger.debug("Path %s does not exists and cannot be guessed. Skipping it." %cdslsrc)
                if cdsl:
                    yield cdsl
                if recursive and os.path.isdir(cdslsrc) and not ismount(cdslsrc):
                    for cdsl2 in self.walkdir(cdslsrc, onerror):
                        yield cdsl2
        except os.error, err:
            if onerror is not None:
                onerror(err)
            return

    def walk(self, **keys):
        from comoonics.ComPath import Path
        from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
        # Note that listdir and error are globals in this module due
        # to earlier import-*.
        cwd=Path()
        cwd.pushd(os.path.join(self.cdslrepository.workingdir, self.cdslrepository.getLinkPath()))
        if not keys.get("onfilesystem", False):
            for cdsl in self.cdslrepository.walkCdsls(keys.get("clusterinfo"), keys.get("cdsls", []), ComoonicsCdslRepository.guessonerror):
                yield cdsl
        else:
            _pathhead, _pathtail=os.path.split(keys.get("path", "."))
            if not _pathhead and not _pathtail or _pathtail==".":
                _pathhead=_pathtail
                _pathtail=None
            for cdsl in self.walkdir(_pathhead, _pathtail, keys.get("recursive", True)):
                yield cdsl
#        self.cdslrepository.workingdir.popd()
        cwd.popd()
                                  
    def validate(self, **keys):
        """
        Method to search filesystem at cdsl link, which is defined in given cdslRepository, for cdsls.
        Adds found cdsls to cdslRepository.
        @param cdslRepository: Includes needed informations about cdsls like cdsl_link
        @type cdslRepository: L{CdslRepository}
        @param clusterInfo: Includes needed information about cluster like nodenames and -ids
        @type clusterInfo: L{ClusterInfo}
        @param onlyvalidate: only validate but not change if True else also change the database. Default False
        @type onlyvalidate: Boolean, default True
        @param onlyrepo: Only test cdsls in repo if they exist or not.
        @type onlyrepo: Boolean, default True 
        @return: Returns two lists. The first list are all files added to the repository and second all that 
            have to be|have been removed.
        @rtype: list<L{Cdsl}>, list<L{Cdsl}>  
        """
        _added=list()
        _removed=list()
    
        for _cdsl in self.walk(path=keys.get("filesystempath", "."), clusterinfo=self.clusterinfo, onfilesystem=keys.get("onfilesystem", False), cdsls=keys.get("cdsls", []), recursive=keys.get("recursive", True)):
            self.logger.info("validate %s." %_cdsl)
            __added, __removed = self.cdslrepository.update(_cdsl, self.clusterinfo, not keys.get("update", False))
            if __added or __removed:
                _backupfile=CdslValidate.backupFileName(os.path.join(self.cdslrepository.workingdir, self.cdslrepository.resource))
                self.backupfiles.append(_backupfile)
                self.backupFile(os.path.join(self.cdslrepository.workingdir, self.cdslrepository.resource), _backupfile)
            if __added:
                self.logger.info("+ %s" %__added)
                _added.append(__added)
            if __removed:
                self.logger.info("- %s" %__removed)
                _removed.append(__removed)
        return _added, _removed

##############
# $Log: ComCdslValidate.py,v $
# Revision 1.10  2010-05-27 08:47:24  marc
# - CdslValidate:
#   - createDefaultRepository: new method to reconstruct repository if not existant or currupt
#   - backupFileName: new method, generate backupfilename to given filename
#   - backupFile: new method, backup the given file
#   - __init__: reconstruct and backup repository if it does not exist or is currupt
#   - walkdir: added filter as parameter that filters possible cdsl (symlinks).
#   - walk: adapted to new Path API
#   - validate: backup repository before applying changes.
#
# Revision 1.9  2010/02/07 20:01:26  marc
# First candidate for new version.
#
# Revision 1.8  2009/07/22 08:37:09  marc
# Fedora compliant
#
# Revision 1.7  2009/06/10 14:53:06  marc
# - first stable version
# - fixed many bugs
# - rewrote nearly everything
# - extensive tests
#