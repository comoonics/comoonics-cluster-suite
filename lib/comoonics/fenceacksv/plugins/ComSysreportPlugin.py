"""Comoonics Sysreport Plugin interface for fenceacksv

"""

import time
from ComPlugin import Plugin
from comoonics.ComSysreport import Sysreport
from comoonics.tools.ComSystemInformation import SystemInformation
from comoonics.ComPath import Path

# here is some internal information
# $Id: ComSysreportPlugin.py,v 1.1 2007-09-07 14:42:28 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/fenceacksv/plugins/ComSysreportPlugin.py,v $

class SysreportPlugin(Plugin):
    """
The sysreport plugin creates gives the functionality to create a sysreport as plugin. You can either create a
sysreport or just execute differents part of the sysreport.
    """
    TEMPLATE_DIR="/usr/share/sysreport/templates"
    TIMEFORMAT="%Y%m%d-%H%M%S"
    TMPDIR="/var/spool/sysreport-%s"
    def __init__(self, templatedir=TEMPLATE_DIR):
        super(SysreportPlugin, self).__init__("sysreport")
        self.tmpdir=self._getTmpdir()
        self.tarfile=self._getTarfile()
        self.templatedir=templatedir
        self.sysreport=None
        self.addCommand("sysreport", self.doSysreport)
        self.addCommand("sysreportshowparts", self.doSysreportShowParts)

    def _getTmpdir(self):
        _tmpdir=self.TMPDIR %time.strftime(self.TIMEFORMAT)
        return Path(_tmpdir)
    def _getTarfile(self):
        return "/tmp/sysreport-%s.tar.gz" %time.strftime(self.TIMEFORMAT)

    def setupSysreport(self, shell=None):
        if not shell:
            print >>self.stdout,  "Setting up systeminformation"
            _sysinfo=SystemInformation()
            print >>self.stdout,  "OK"
        else:
            _sysinfo=shell.sysinfo
        if not self.sysreport:
            print >>self.stdout,  "Setting up sysreport.."
            self.sysreport=Sysreport(_sysinfo, self.tmpdir.getPath(), None, self.templatedir)
            print >>self.stdout,  "OK"

    def doSysreport(self, *params, **kwds):
        """
Does the sysreport after the following syntax:
sysreport [part=..]+ [tarfile=..] [tmpdir=..] [nosaveset] [noheadset]
sysreport [part]+ [tarfile]
Whereas the parameters are to be interpreted as follows:
part: is the part of the sysreport you want to execute (see sysreport-show-parts)
tarfile: is the tarfile the report should be stored in.
tmpdir: is the path where temporary files will be stored.
        """
        SysreportPlugin.logger.debug("doSysreport(params: %s, kwds: %s)" %(params, kwds))
        _tarfile=self.tarfile
        _tmpdir=self._getTmpdir().getPath()
        _saveset=True
        _headset=True
        _shell=None
        _parts=None
        if params and len(params)>0:
            _tarfile=params[-1]
            _parts=params[:-1]
        elif kwds:
            _tarfile=kwds.get("tarfile", _tarfile)
            _tmpdir=kwds.get("tmpdir", _tmpdir)
            _parts=kwds.get("part", None)
            _headset=not kwds.has_key("noheadset")
            _saveset=not kwds.has_key("nosaveset")
            _shell=kwds.get("shell", None)
        self.setupSysreport(kwds.get("shell", None))
        self.sysreport.destination=_tmpdir
        self.sysreport.tarfile=_tarfile
        self.sysreport.doSets(_parts, _headset, _saveset)

    def doSysreportShowParts(self, *params, **kwds):
        """
Shows the parts that a sysreport can execute. You can select each of those.
        """
        SysreportPlugin.logger.debug("doSysreportParts(params: %s, kwds: %s)" %(params, kwds))
        _shell=None
        if kwds:
            _shell=kwds.get("shell", None)
        self.setupSysreport(_shell)
        print >>self.stdout,  "The following parts can be called."
        print >>self.stdout,  ", ".join(self.sysreport.getSetNames())

def _test():
    from comoonics import ComSystem, ComLog
    import logging
    ComSystem.__EXEC_REALLY_DO=""
    ComLog.setLevel(logging.DEBUG)

    _validcommands=["sysreport-show-parts"]
    _plugin=SysreportPlugin("../../../../sysreport")
    print "Help of plugin %s: " %_plugin.getName()
    print _plugin.help()
    print "Short help: %s" %_plugin.help_short()
    for _command in _plugin.getCommands():
        print "Help of command %s:" %_command
        print _plugin.help(_command)
    for _command in _validcommands:
        print "doCommand %s:" %_command
        _plugin.doCommand(_command)

if __name__=="__main__":
    _test()

########################
# $Log: ComSysreportPlugin.py,v $
# Revision 1.1  2007-09-07 14:42:28  marc
# initial revision
#