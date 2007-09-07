"""Comoonics Plugin interface for fenceacksv

"""

import inspect
import sys
from comoonics import ComLog

# here is some internal information
# $Id: ComPlugin.py,v 1.1 2007-09-07 14:42:28 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/fenceacksv/plugins/ComPlugin.py,v $

class Method(object):
    def __init__(self, methodref, help=None, *params, **kwds):
        self.methodref=methodref
        self.methodhelp=help
        self.params=params
        self.kwds=kwds
    def do(self, *params, **kwds):
        _params=self.params+params
        _kwds=dict()
        _kwds.update(self.kwds)
        _kwds.update(kwds)
        return self.methodref(*_params, **_kwds)
    def help(self):
        if self.methodhelp:
            return self.methodhelp
        else:
            return inspect.getdoc(self.methodref)
    def __str__(self):
        buf="Method %s(params: %s, kwds: %s)" %(self.methodref.__name__, self.params, self.kwds)

class Plugin(object):
    """
    Plugin Interface
    """
    logger=ComLog.getLogger("comoonics.fenceacksv.plugins.ComPlugin.Plugin")
    def __init__(self, _name=None, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr):
        self._commands=dict()
        self._commands_help=dict()
        self.stdout=stdout
        self.stdin=stdin
        self.stderr=stderr
        self.name=_name
    def getName(self):
        return self.name
    def addCommand(self, _name, methodref, *params, **kwds):
        self._commands[_name]=Method(methodref, *params, **kwds)
    def getCommands(self):
        return self._commands.keys()
    def hasCommand(self, _name):
        return self._commands.has_key(_name)
    def getCommand(self, _name):
        """
        returns a Methodtype
        """
        if isinstance(self._commands[_name], Method):
            return self._commands[_name]
        else:
            return Method(self._commands[_name])
    def doCommand(self, _name, *params, **kwds):
        self.doPre(_name, *params, **kwds)
        _ret=self.getCommand(_name).do(*params, **kwds)
        self.doPost(_name, *params, **kwds)
        return _ret

    def doPre(self, _name, *params, **kwds):
        pass
    def doPost(self, _name, *params, **kwds):
        pass
    def help_short(self):
        buf=inspect.getdoc(self)
        if not buf:
            buf=""
        return buf

    def help(self, _command=None):
        """
        Help about this plugin
        """
        Plugin.logger.debug("help(%s)" %_command)
        if not _command or _command =="" or _command=="help":
            buf=inspect.getdoc(self)
            if not buf:
                buf=""
            buf+="\nCommands:\n"+", ".join(self.getCommands())
            return buf
        else:
            if self._commands_help.has_key(_command):
                return self._commands_help[_command]
            else:
                return self.getCommand(_command).help()

class DummyPlugin(Plugin):
    """
    just a dummy plugin that does nothing
    """
    def __init__(self):
        super(DummyPlugin, self).__init__("dummy")
        self.addCommand("dummy", self.dummy, None, "static")
        self.addCommand("dummy2", self.dummy)

    def dummy(self, *params):
        """
        dummy(): test method help
        """
        _params=list()
        for i in range(len(params)):
            _params.append("%s" %params[i])
        print >>self.stdout, "dummy called params: %s!!" %','.join(_params)
        return 0

def _test():
    _plugin=DummyPlugin()
    print "Help of plugin %s: " %_plugin.getName()
    print _plugin.help()
    for _command in _plugin.getCommands():
        print "Help of command %s:" %_command
        print _plugin.help(_command)
        _plugin.doCommand(_command, ["param1", "param2"])
        _plugin.doCommand(_command, "param1", "param2")

if __name__=="__main__":
    _test()
##############
# $Log $