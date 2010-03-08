""" Comoonics sysrq modification module

<modification type="sysrq">
    <sysrq settrigger="(true|false)">
      <command name=".."/>+
    </sysrq>
</modification>
<modification type="sysrq">
    <sysrq settrigger="(true|false)" command=""/>
</modification>
"""


# here is some internal information
# $Id: ComSysrqModification.py,v 1.2 2010-03-08 12:30:48 marc Exp $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/enterprisecopy/ComSysrqModification.py,v $

from ComModification import Modification
import ComModification
from comoonics import ComLog
from comoonics.ComSysrq import Sysrq

class SysrqModification(Modification):
    logger=ComLog.getLogger("comoonics.enterprisecopy.ComSysrq.SysrqModification")

    type=None
    child=None
    _log=None

    def _createElement(**kwds):
        import xml.dom
        _impl=xml.dom.getDOMImplementation()
        _doc=_impl.createDocument(None, Modification.TAGNAME, None)
        _element=_doc.documentElement
        _element.setAttribute("type", "sysrq")
        if kwds.has_key("command"):
            _element.appendChild(Sysrq._createElement(kwds.get("command"), kwds.get("settrigger")))
        elif kwds.has_key("commands"):
            _element.appendChild(Sysrq._createElement(kwds.get("commands"), kwds.get("settrigger")))
        return (_element, _doc)
    _createElement=staticmethod(_createElement)

    def __init__(self, *params, **kwds):
        """
        Constructors:
        __init__(element, doc)
        __init__(self, command=cmd, [settrigger=*True|False])
        __init__(self, commands=list<cmd>, [settrigger=*True|False])
        __init__(element=element, doc=doc)

        @element: the element of the modification
        @doc: the root document
        @command: sysrq command to be executed
        @commands: list of sysrq commands to be executed
        @settrigger: set the trigger or not
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
        self.sysrqs=list()
        for _sysrq in self.getElement().getElementsByTagName(Sysrq.TAGNAME):
            self.sysrqs.append(Sysrq(_sysrq, _doc))

    def doRealModifications(self):
        """
        calls doCatifAction for every action
        """
        for _sysrq in self.sysrqs:
            _sysrq.doCommands()

# $Log: ComSysrqModification.py,v $
# Revision 1.2  2010-03-08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.1  2007/09/07 14:42:09  marc
# initial revision
#
