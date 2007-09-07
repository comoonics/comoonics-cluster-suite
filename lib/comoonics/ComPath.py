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
# $Id: ComPath.py,v 1.1 2007-09-07 14:44:41 marc Exp $
#


__version__ = "$Revision: 1.1 $"
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
        Path.logger.debug("popd: %s" %self.getOldPaths())
        if len(self.getOldPaths()) > 0:
            _path=self.getPath()
            path=self.getOldPaths().pop()
            os.chdir(str(path))
            self.setAttribute("name", path)
            Path.logger.debug("popd: _created: %s" %self.__created)
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
# Revision 1.1  2007-09-07 14:44:41  marc
# initial revision
#