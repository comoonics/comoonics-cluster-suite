""" Comoonics path representation
This module just represents the path implementation as DataObject

Example Configuration:
        <path name="/var/log/messages" id="path1">
            <modification type="message">
Hello world
            </modification>
        </path>
        <path refid="path1">
            <modificaiton type="message">
hello world2
        </path>
"""

# here is some internal information
# $Id: ComPath.py,v 1.4 2009-07-22 08:38:00 marc Exp $
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


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComPath.py,v $

from ComDataObject import DataObject
import ComSystem, ComLog
from ComSystem import ExecLocalException
import os.path
import os

createddirs=dict()

class Path(DataObject):
    oldpaths=list()
    logger=ComLog.getLogger("comoonics.ComPath.Path")
    TAGNAME="path"
    def _createElement(self, path):
        import xml.dom
        _impl=xml.dom.getDOMImplementation()
        _doc=_impl.createDocument(None, Path.TAGNAME, None)
        _element=_doc.documentElement
        _element.setAttribute("name", path)
        return (_element, _doc)
    def __init__(self, *params, **kwds):
        """
        The following path constructors are allowed
        __init__(path)
        __init__(element, doc)
        __init__(element=.., doc=..)
        __init__(path=..)
        """
        # Case path is given
        if params and len(params)==1:
            (element, doc)=self._createElement(params[0])
        elif params and len(params)==2:
            (element, doc)=params
        elif kwds and kwds.has_key("element", "doc"):
            element=kwds["element"]
            doc=kwds["doc"]
        elif kwds and kwds.has_key("path"):
            (element, doc)=self._createElement(kwds["path"])
        else:
            raise TypeError("__init__() takes exactly 2 arguments or different keys. (%u given)" %len(params))

        super(Path, self).__init__(element, doc)
        self.setPath(self.getPath())
        self.__created=createddirs
        if not self.__created.has_key(self.getPath()):
            self.__created[self.getPath()]=False
    def getPath(self):
        return self.getAttribute("name")
    def setPath(self, path):
        try:
            if ComSystem.isSimulate():
                self.setAttribute("name", path)
            else:
                self.setAttribute("name",str(ComSystem.execLocalOutput("echo %s" %path)[0])[:-1])
        except ExecLocalException:
            self.setAttribute("name", path)
    def getOldPaths(self):
        return self.oldpaths
    def pushd(self, path=None):
        if not path:
            path=self.getPath()
        _cwd=os.getcwd()
        os.chdir(str(path))
        self.oldpaths.append(_cwd)
        self.setAttribute("name", path)
        if not self.__created.has_key(self.getPath()):
            self.__created[self.getPath()]=False
    def popd(self):
        path=None
        #Path.logger.debug("popd: %s" %self.getOldPaths())
        if len(self.getOldPaths()) > 0:
            _path=self.getPath()
            path=self.getOldPaths().pop()
            os.chdir(str(path))
            self.setAttribute("name", path)
#            Path.logger.debug("popd: _created: %s" %self.__created)
        return path

    def remove(self, path=None, force=False):
        if not path:
            path=self.getPath()

        if path and ((self.__created.has_key(path) and self.__created[path] and self.getAttribute("remove", "false") == "true") or force):
            Path.logger.debug("remove %s, %s" %(path, self.__created))
            out=ComSystem.execLocalOutput("rm -rf %s" %str(path), True)
            if self.__created.has_key(path):
                del self.__created[path]
    def exists(self, path=None):
        if not path:
            path=self.getPath()
        return os.path.exists(str(path)) and os.path.isdir(str(path))
    def mkdir(self, path=None):
        if not path:
            path=self.getPath()
        if not self.exists(path):
            os.mkdir(str(path))
            self.__created[path]=True
    def __str__(self):
        return "currentpath: %s, oldpaths: %s" %(self.getPath(), self.getOldPaths())

################
# $Log: ComPath.py,v $
# Revision 1.4  2009-07-22 08:38:00  marc
# fedora compliant
#
# Revision 1.3  2009/06/10 15:20:08  marc
# removed some debugs.
#
# Revision 1.2  2008/03/12 09:35:25  marc
# made Path simulation save and added a comment.
#
# Revision 1.1  2007/09/07 14:44:41  marc
# initial revision
#