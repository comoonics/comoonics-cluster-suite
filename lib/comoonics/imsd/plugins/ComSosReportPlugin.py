"""
Com.oonics SOSReport plugin for fenceacksv
"""

from ComPlugin import Plugin

# here is some internal information
# $Id: ComSosReportPlugin.py,v 1.1 2009-09-28 15:27:30 marc Exp $
#

from optparse import OptionParser, Option

try:
    from comoonics.sos.sosreport import SosReport
except ImportError, ie:
    from sos.sosreport import SosReport

class SosOption (Option):
    """Allow to specify comma delimited list of plugins"""
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            try: lvalue = value.split(",")
            except: pass
            else: values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

class OptionParser_extended(OptionParser):
    def print_help(self):
        OptionParser.print_help(self)
        print
        print "Some examples:"
        print
        print " enable cluster plugin only and collect dlm lockdumps:"
        print "   # sosreport -o cluster -k cluster.lockdump"
        print 
        print " disable memory and samba plugins, turn off rpm -Va collection:"
        print "   # sosreport -n memory,samba -k rpm.rpmva=off"
        print 

class SosReportPlugin(Plugin):
    """
    Plugin for fenceacksv to use the sosreport from redhat
    """
    def __init__(self):
        super(SosReportPlugin, self).__init__("sosreport")
        self._sosreport=SosReport()
        self.addCommand("listplugins", self.doListPlugins)
        self.addCommand("main", self.doMain)
        from optparse import OptionParser, Option
        
        self.cmdParser = OptionParser_extended(option_class=SosOption)
        self.cmdParser.add_option("-l", "--list-plugins", action="store_true", \
                                 dest="listPlugins", default=False, \
                                 help="list plugins and available plugin options")
        self.cmdParser.add_option("-n", "--skip-plugins", action="extend", \
                                 dest="noplugins", type="string", \
                                 help="skip these plugins", default = [])
        self.cmdParser.add_option("-e", "--enable-plugins", action="extend", \
                                 dest="enableplugins", type="string", \
                                 help="enable these plugins", default = [])
        self.cmdParser.add_option("-o", "--only-plugins", action="extend", \
                                 dest="onlyplugins", type="string", \
                                 help="enable these plugins only", default = [])
        self.cmdParser.add_option("-k", action="extend", \
                                 dest="plugopts", type="string", \
                                 help="plugin options in plugname.option=value format (see -l)")
        self.cmdParser.add_option("-a", "--alloptions", action="store_true", \
                                 dest="usealloptions", default=False, \
                                 help="enable all options for loaded plugins")
        self.cmdParser.add_option("-u", "--upload", action="store_true", \
                                 dest="upload", default=False, \
                                 help="upload the report to Red Hat support")
        self.cmdParser.add_option("--batch", action="store_true", \
                                 dest="batch", default=False, \
                                 help="do not ask any question (batch mode)")
        self.cmdParser.add_option("--no-colors", action="store_true", \
                                 dest="nocolors", default=False, \
                                 help="do not use terminal colors for text")
        self.cmdParser.add_option("-v", "--verbose", action="count", \
                                 dest="verbosity", \
                                 help="increase verbosity")
        self.cmdParser.add_option("--debug", action="count", \
                                 dest="debug", \
                                 help="enabling debugging")
        self.cmdParser.add_option("--no-progressbar", action="store_false", \
                                 dest="progressbar", default=True, \
                                 help="do not display a progress bar.")
        self.cmdParser.add_option("--no-multithread", action="store_true", \
                                 dest="nomultithread", \
                                 help="disable multi-threaded gathering mode (slower)", default=False)
    def doListPlugins(self, *params, **kwds):
        """
        Lists all available plugins.
        """
        _params=list(params)
        (__cmdLineOpts__, __cmdLineArgs__)=self.cmdParser.parse_args(_params)
        self._sosreport.listPlugins()
        
    def doMain(self, *params, **kwds):
        _params=list(params)
        (__cmdLineOpts__, __cmdLineArgs__)=self.cmdParser.parse_args(_params)
        self._sosreport.main()
        
    def help(self, _command=None):
        if not _command:
            return self.cmdParser.format_help()
        else:
            return super(SosReportPlugin, self).help(_command)
        
def _test():
    try:
        from comoonics.sos.sosreport import SosReportException
    except ImportError:
        from sos.sosreport import SosReportException
    _plugin=SosReportPlugin()
    _plugin._sosreport.checkrootuid=False
    _plugin._sosreport.pluginpaths={"../../sos/plugins_test": "comoonics.sos.plugins_test"}
    print "Help of plugin %s: " %_plugin.getName()
    print _plugin.help()
    for _command in _plugin.getCommands():
        print "Help of command %s:" %_command
        print _plugin.help(_command)
        #_plugin.doCommand(_command, ["param1", "param2"])
        try:
            _plugin.doCommand(_command, "param1", "param2")
        except SosReportException, se:
            print "Error: %s" %se
    print "Finished testing of plugin %s" %_plugin

if __name__=="__main__":
    _test()

#################
# $Log: ComSosReportPlugin.py,v $
# Revision 1.1  2009-09-28 15:27:30  marc
# *** empty log message ***
#