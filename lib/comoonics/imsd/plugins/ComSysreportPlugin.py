"""Comoonics Sysreport Plugin interface for fenceacksv

"""

import time
from ComPlugin import Plugin
from comoonics.tools.ComSysreport import Sysreport
from comoonics.tools.ComSystemInformation import SystemInformation

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
    def __init__(self, templatedir=TEMPLATE_DIR, tmpdir=None, tarfile=None):
        super(SysreportPlugin, self).__init__("sysreport")
        self.tmpdir=tmpdir
        self.tarfile=tarfile
        self.templatedir=templatedir
        self.sysreport=None
        self.addCommand("sysreport", self.doSysreport)
        self.addCommand("sysreportshowparts", self.doSysreportShowParts)

    def getTmpdir(self):
        return getattr(self, "tmpdir", self.TMPDIR %time.strftime(self.TIMEFORMAT))
    def getTarfile(self):
        return getattr(self, "tarfile", "/tmp/sysreport-%s.tar.gz" %time.strftime(self.TIMEFORMAT))

    def setupSysreport(self, shell=None):
        if not shell:
            print >>self.stdout,  "Setting up systeminformation"
            _sysinfo=SystemInformation()
            print >>self.stdout,  "OK"
        else:
            _sysinfo=shell.sysinfo
        if not self.sysreport:
            print >>self.stdout,  "Setting up sysreport.."
            self.sysreport=Sysreport(_sysinfo, self.tmpdir, None, self.templatedir)
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
        saveset=True
        headset=True
        shell=None
        parts=None
        if params and len(params)>0:
            self.tarfile=params[-1]
            parts=params[:-1]
        elif kwds:
            self.tarfile=kwds.get("tarfile", self.getTarfile())
            self.tmpdir=kwds.get("tmpdir", self.getTmpdir())
            parts=kwds.get("part", None)
            headset=not kwds.has_key("noheadset")
            saveset=not kwds.has_key("nosaveset")
            shell=kwds.get("shell", None)
        self.setupSysreport(shell)
        self.sysreport.destination=self.getTmpdir()
        self.sysreport.tarfile=self.getTarfile()
        self.sysreport.doSets(parts, headset, saveset)

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

    _validcommands=["sysreportshowparts"]
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