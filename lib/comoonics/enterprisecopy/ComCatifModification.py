""" Comoonics modification module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComCatifModification.py,v 1.1 2007-09-07 14:35:09 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComCatifModification.py,v $

import os.path
import re

from ComModification import Modification
import ComModification
from comoonics import ComSystem, pexpect
from comoonics.ComSystem import ExecLocalException
from comoonics import ComLog

class CatifModification(Modification):
    """
    abstract base Modfication sharing some common methods with the other Catif..Classes
    """
    logger=ComLog.getLogger("comoonics.enterprisecopy.ComCatifModification.CatifModification")

    type=None
    child=None
    _log=None
    catiflogger=ComLog.getLogger("catiflogger")

    def _createChild(self, _name, _doc):
        _element=_doc.createElement(self.child)
        _element.setAttribute("name", _name)
        return _element

    def _createElement(self, **kwds):
        import xml.dom
        if kwds.has_key(self.type) and kwds.has_key("name"):
            _actions=kwds[self.type]
            del kwds[self.type]
            _destination=kwds["destination"]
            del kwds["destination"]
            if kwds.has_key("doc"):
                _doc=kwds["doc"]
            else:
                _impl=xml.dom.getDOMImplementation()
                _doc=_impl.createDocument(None, Modification.TAGNAME, None)
                _element=_doc.documentElement
                _element.setAttribute("type", self.type)
                _element.setAttribute("name", _destination)

                if kwds.has_key(self.child):
                    _element.appendChild(self._createChild(kwds[self.child], _doc))
                elif kwds.has_key("%ss" %self.child):
                    _list=kwds["%ss" %self.child]
                    for _child in _list:
                        _element.appendChild(self._createChild(_child, _doc))

                for (_name,_value) in kwds.items():
                    _element.setAttribute(_name, _value)
        return (_element, _doc)

    def __init__(self, *params, **kwds):
        """
        Constructors:
        __init__(element, doc)
        __init__(actions=list, destination=directory, [errors=(ignore|raise|*log)], [doc=document])
        __init__(action=what, destination=directory, [errors=(ignore|raise|*log)], [doc=document])
        __init__(element=element, doc=doc)

        @element: the element of the modification
        @doc: the root document
        @actions: list of actions to be done
        @destination: where to put the results
        @errors: how to handle the errors
        """
        if len(params)==2:
            _element=params[0]
            _doc=params[0]
        elif kwds:
            if kwds.has_key("element") and kwds.has_key("doc"):
                _element=kwds["element"]
                _doc=kwds["doc"]
            else:
                (_element, _doc)=self._createElement(**kwds)
        else:
            raise TypeError("__init__() takes exactly 2 arguments or different keys. (%u given)" %len(params))
        Modification.__init__(self, _element, _doc)

    def _cmd(self, __cmd, _log=None):
        if _log:
           _log.write("%s\n" %__cmd)
        self.catiflogger.debug(__cmd)
        #__out=ComSystem.execLocalOutput(__cmd)
        self.__cmd=__cmd
        (__out,__rc)=pexpect.run(__cmd, timeout=-1, withexitstatus=1)
        if _log:
            _log.write("".join(__out))
        if __rc!=0:
            raise ExecLocalException(__cmd, __rc, __out, None)
        self.catiflogger.info("%s: OK(%u)" %(__cmd, __rc))

    def doRealModifications(self):
        """
        calls doCatifAction for every action
        """
        _dest=self.getAttribute("destination", "./")
        self.errors=self.getAttribute("errors", "log")
        _childs=self.getElement().getElementsByTagName(self.child)
        for _child in _childs:
            _name=_child.getAttribute("name")
            _names=list()
            _names.append(_name)
            try:
                if re.findall("\$\(.+\)", _name):
                    _names=re.split("\s+", str(ComSystem.execLocalOutput("echo %s" %_name)[0])[:-1])
                    CatifModification.logger.debug("doRealModifications() _names: %s" %_names)
            except ExecLocalException:
                _names=None
            _log=None
            if self.hasAttribute("log"):
                _log=self.getAttribute("log")
            elif _child.hasAttribute("log"):
                _log=_child.getAttribute("log")
            if not _names:
                continue
            for _name in _names:
                try:
                    if _name and _name != "":
                        self.doCatifAction(_name, _dest, _log)
                except ExecLocalException, _ale:
                    self._handleError(_ale)
                except pexpect.ExceptionPexpect, ep:
                    self._handleError(ep)

    def _handleError(self, _exception):
        if isinstance(_exception, ExecLocalException):
            self.catiflogger.info("%s: Failed[%s]" %(self.__cmd, _exception.rc))
        else:
            self.catiflogger.info("%s: Failed[]" %(self.__cmd))
        if self.errors=="raise":
            raise _exception
        elif self.errors=="ignore":
            ComLog.debugTraceLog(CatifModification.logger)
            pass
        else:
            ComLog.debugTraceLog(CatifModification.logger)
            if self._log:
                self._log.write("Error occured: %s" %_exception)

    def doCatifAction(self, _name, _dest, _log=None):
        """
        abstract method doing things
        """
        pass

class CatiffileModification(CatifModification):
    """
    CatiffileModification derived from Red Hat sysreport module. Can be represented as xml like as follows:
    <modification type="catiffile" name="/tmp/123" errors="ignore">
       <file name="/etc/rc.d"/>
       <file name="/etc/syslog.conf"/>
    </modification>

    """
    logger=ComLog.getLogger("comoonics.enterprisecopy.ComCatifModification.CatiffileModification")
    type="catiffile"
    child="file"

    def __init__(self, *params, **kwds):
        """
        Constructors:
        __init__(element, doc)
        __init__(files=list, destination=directory, errors=[ignore|raise|log])
        __init__(file=list, destination=directory, errors=[ignore|raise|log])
        __init__(element=element, doc=doc)

        @element: the element of the modification
        @doc: the root document
        @files: list of files to be modified
        @destination: where to put the results
        @errors: how to handle the errors
        """
        CatifModification.__init__(self, *params, **kwds)

    def doCatifAction(self, _source, _dest, _log=None):
        cp_args=[  ]
        othercommands=[]
        if not os.path.isfile(_source) and not os.path.islink(_source):
            cp_args.append("-x")
            cp_args.append("-R")
            cp_args.append("--parents")
            othercommands.append("find %s -type b -o -type c -exec rm -f {} 2>/dev/null \;" %os.path.join(_dest, _source))
        else:
            cp_args.append("--parents")
        __cmd = "/bin/bash -c '/bin/cp "+" ".join(cp_args)+" "+_source+" "+_dest+"'"
        self._cmd(__cmd)
        for __cmd in othercommands:
            self._cmd(__cmd, _log)

class CatifexecModification(CatifModification):
    """
    CatiffileModification derived from Red Hat sysreport module. Can be represented as xml like as follows:
    <modification type="catifexec" name="/tmp/123" errors="ignore">
       <command name="/usr/bin/pstree"/>
       <command name="ls -l"/>
    </modification>

    """
    logger=ComLog.getLogger("comoonics.enterprisecopy.ComCatifModification.CatifexecModification")
    type="catifexec"
    child="command"
    def __init__(self, *params, **kwds):
        """
        Constructors:
        __init__(element, doc)
        __init__(commands=list, destination=directory, errors=[ignore|raise|log])
        __init__(command=list, destination=directory, errors=[ignore|raise|log])
        __init__(element=element, doc=doc)

        @element: the element of the modification
        @doc: the root document
        @commands: list of files to be modified
        @destination: where to put the results
        @errors: how to handle the errors
        """
        CatifModification.__init__(self, *params, **kwds)

    def doCatifAction(self, _command, _dest, _log=None):
        import re
        CatifexecModification.logger.debug("doCatifAction command: %s, log path: %s cwd: %s" %(_command, _log, os.getcwd()))
        if not _log:
            _log=os.path.join(_dest, os.path.basename(re.split("\s+", _command)[0]))
        self._log=file(_log, "a+")
        self._cmd(_command, self._log)
        if self._log:
            self._log.close()
            self._log=None

def __test():
    from xml.dom.ext.reader import Sax2
    import tempfile
    import logging
    from comoonics.ComPath import Path
    from ComModification import registerModification
    registerModification("catiffile", CatiffileModification)
    registerModification("catifexec", CatifexecModification)
    ComLog.setLevel(logging.DEBUG)
    __tmpdir=tempfile.mkdtemp()
    print("tmpdir: %s" %__tmpdir)
    __xmls=[
"""
<path name="%s">
   <modification type="catifexec">
      <command name="/usr/bin/pstree"/>
   </modification>
</path>
""" %__tmpdir,
"""
<path name="%s">
   <modification type="catiffile">
      <file name="/etc/*-release"/>
      <file name="$(/bin/ls -d /var/log/Xorg.*.log /var/log/XFree86.*.log 2>/dev/null)"/>
   </modification>
</path>
""" %__tmpdir,
"""
<path name="%s">
   <modification type="catiffile">
      <file name="/etc/ld.so.conf.d"/>
      <file name="/etc/ld.so.conf.dadf"/>
   </modification>
</path>
""" %__tmpdir,
"""
<path name="%s">
   <modification type="catiffile" errors="ignore">
      <file name="/etc/rc.d"/>
      <file name="/etc/syslog.conf"/>
   </modification>
   <modification type="catifexec">
      <command name="hostname"/>
   </modification>
   <modification type="catifexec">
      <command name="/bin/bash -c 'echo lspci; echo; lspci; echo; echo lspci -n; echo; lspci -n; echo; echo lspci -nv; echo; lspci -nv; echo; echo lspci -nvv; echo; /sbin/lspci -nvv'" log="lspci"/>
   </modification>
</path>
""" %__tmpdir
    ]
    # create Reader object
    reader = Sax2.Reader()

    for _xml in __xmls:
        _doc = reader.fromString(_xml)
        _path=Path(_doc.documentElement, _doc)
        _path.mkdir()
        _path.pushd()
        for _modification in _doc.documentElement.getElementsByTagName("modification"):
            _modification=ComModification.getModification(_modification, _doc)
            _modification.doModification()
        _path.popd()

if __name__=="__main__":
    __test()

# $Log: ComCatifModification.py,v $
# Revision 1.1  2007-09-07 14:35:09  marc
# initial revision
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.2  2006/07/07 11:35:36  mark
# changed to inherit FileModification
#
# Revision 1.1  2006/06/30 07:56:12  mark
# initial revision
#
