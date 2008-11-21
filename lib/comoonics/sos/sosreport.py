import sys
import os
import os.path
from time import time

# RHEL3 doesn't have a logging module
try:
   import logging
except ImportError:
    import sos.rhel3_logging
    logging = sos.rhel3_logging

import gettext
from threading import Semaphore

from xmlreport import XmlReport

import sos
import sos.helpers

__version__ = 1.8

__breakHits__ = 0  # Use this to track how many times we enter the exit routine

def textcolor(text, fg, raw=0):
    colors = {  "black":"30", "red":"31", "green":"32", "brown":"33", "blue":"34",
              "purple":"35", "cyan":"36", "lgray":"37", "gray":"1;30", "lred":"1;31",
              "lgreen":"1;32", "yellow":"1;33", "lblue":"1;34", "pink":"1;35",
              "lcyan":"1;36", "white":"1;37" }
    opencol = "\033["
    closecol = "m"
    clear = opencol + "0" + closecol
    f = opencol + colors[fg] + closecol
    return "%s%s%s" % (f, text, clear)

class progressBar:
    def __init__(self, minValue = 0, maxValue = 10, totalWidth=40):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done
        self.time_start = time()
        self.eta = 0
        self.last_amount_update = time()
        self.update()

    def updateAmount(self, newAmount = 0, finished = False):
        if newAmount < self.min:
            newAmount = self.min
        if newAmount > self.max:
            newAmount = self.max - 1
        if self.amount != newAmount:
            self.last_amount_update = time()
            self.amount = newAmount
            last_update_relative = round(self.last_amount_update - self.time_start)
            self.eta = round(last_update_relative * self.max / self.amount)

        # generate ETA
        timeElapsed = round(time() - self.time_start)
        last_update_relative = round(self.last_amount_update - self.time_start)
        if timeElapsed >= 10 and self.amount > 0:
            try:
                percentDone = round(timeElapsed * 100 / self.eta)
            except:
                percentDone = 0
            if percentDone >= 100 and not finished:
                percentDone = 99
            if percentDone > 100:
                percentDone = 100
                ETA = timeElapsed
            elif self.eta < timeElapsed:
                ETA = timeElapsed
            else:
                ETA = self.eta
            ETA = "[%02d:%02d/%02d:%02d]" % (int(timeElapsed/60), timeElapsed % 60, int(ETA/60), ETA % 60)
        else:
            ETA = "[%02d:%02d/--:--]" % (int(timeElapsed/60), timeElapsed % 60)
            if self.amount < self.max:
                percentDone = 0
            else:
                percentDone = 100

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        self.progBar = ""
        for inc in range(0,allFull):
            if inc == int(allFull / 2):
                self.progBar = self.progBar + textcolor("%d%%" % percentDone, "green")
            elif inc < numHashes:
                self.progBar = self.progBar + textcolor('#', "gray")
            else:
                self.progBar = self.progBar + ' '
        self.progBar = " Progress [" + self.progBar + "]" + ETA

    def incAmount(self, toInc = 1):
        self.updateAmount(self.amount+toInc)

    def finished(self):
        self.updateAmount(self.max, finished = True)
        sys.stdout.write(self.progBar + '\n')
        sys.stdout.flush()

    def update(self):
        self.updateAmount(self.amount)
        sys.stdout.write(self.progBar + '\r')
        sys.stdout.flush()

class SosReportException(Exception):
    pass
class SosReport(object):
    # pylint: disable-msg = R0912
    # pylint: disable-msg = R0914
    # pylint: disable-msg = R0915
    # for debugging
    """
    This is the top-level class that gathers and processes all sosreport information
    """
    __raisePlugins__ = 0

    # dictionary of attribute of class and keyname of returned dict
    __commons_attrs = {'dstroot': 'dstroot', 'cmddir': 'cmddir', 'logdir': 'logdir', 'rptdir': 'rptdir',
                       'soslog': 'soslog', 'policy': 'policy', 'verbosity' : 'verbosity',
                       'xmlreport' : 'xmlreport', 'options': 'cmdlineopts', 'config':'config' }
    # Only needed if started not with commandlineoptions but with keywords of other source
    # Then we need to build commandlineoptions from the given keywords. Here are all attributes and cmdlineoptionsnames specified.
    __kwd_attrs= {"listPlugins": "listPlugins", "noplugins": "noplugins", "enabledplugins": "enableplugins", "onlyplugins": "onlyplugins", 
                  "plugopts": "plugopts", "usealloptions": "usealloptions", "upload": "upload", "batch": "batch", "nocolors": "nocolors", 
                  "verbosity": "verbose", "debug": "debug", 
                  "progressbar": "progressbar", "nomultithread": "nomultithread"}
    
    # to being able to overwrite filenames
    LOGFILENAME="sos.log"
    CONFFILENAME="/etc/sos.conf"
    PLUGINPATH_SUFFIX="/sos/plugins"
    LOCALE_DIR="/usr/share/locale"

    def __init__(self, *params, **kwds):
        self.listplugins=False
        self.noplugins=[]
        self.enabledplugins=[]
        self.onlyplugins=[]
        self.plugopts=None
        self.usealloptions=False
        self.upload=False
        self.batch=False
        self.nocolors=False
        self.verbosity=0
        self.debug=0
        self.progressbar=True
        self.nomultithread=False
        self.checkrootuid=True
        self.autoloadplugins=True
        self.pluginnamesspaces=dict()
        
        self.loadedplugins = []
        self.skippedplugins = []
        self.alloptions = []

        self.plugins=list()
        self.plugin_names=list()
        
        import ConfigParser
        self.config = ConfigParser.ConfigParser()
        try: self.config.readfp(open(self.CONFFILENAME))
        except IOError: pass

        # generically set attributes from outside
        # The first param if there is supposed to be Values from optparse
        if len(params) > 0:
            self._fromOptparseValues(params[0])
        elif kwds:
            self._fromKwds(kwds)
        
        # perhaps we should automatically locate the policy module??
        import sos.policyredhat
        self.policy = sos.policyredhat.SosPolicy()

        # find the plugins path
        self.pluginpaths=dict()
        paths = sys.path
        for path in paths:
            if path.strip()[-len("site-packages"):] == "site-packages":
                self.appendPluginsPath(path + self.PLUGINPATH_SUFFIX)

        self.setupPathEnvironment()
        self.xmlreport = XmlReport()
        
        self.setupi18n()
        self.setupLogging()
        
        # Make policy aware of the commons
        self.policy.setCommons(self.getCommons())

    def _createCmdLineOpts(self):
        from optparse import Values
        _values=Values()
        for (_key1, _key2) in self.__kwd_attrs.items():
            setattr(_values, _key2, getattr(self, _key1, getattr(self, _key2, None)))
        return _values
    
    def _fromOptparseValues(self, values):
        self._fromKwds(values.__dict__)

    def _fromKwds(self, kwds):
        for (_key1, _key2) in self.__kwd_attrs.items():
            if kwds.has_key(_key1):
                _key=_key1
            elif kwds.has_key(_key2):
                _key=_key2
            else:
                continue
            setattr(self, _key1, kwds[_key])
        for (_key, _value) in kwds.items():
            if not _key in self.__kwd_attrs:
                setattr(self, _key, _value)

    def setupPathEnvironment(self):
        # Set up common info and create destinations
        self.dstroot = sos.helpers.sosFindTmpDir()
        if not self.dstroot:
            raise IOError("Could not create temporary directory %s." %self.dstroot)
        self.cmddir = os.path.join(self.dstroot, "sos_commands")
        self.logdir = os.path.join(self.dstroot, "sos_logs")
        self.rptdir = os.path.join(self.dstroot, "sos_reports")
        os.mkdir(self.cmddir, 0755)
        os.mkdir(self.logdir, 0755)
        os.mkdir(self.rptdir, 0755)
                
    def appendPluginsPath(self, _path, _namespace="sos.plugins"):
        self.pluginpaths[_path]=_namespace

    def setupi18n(self):
        import gettext
        # initialize i18n language localization
        gettext.install('sos', self.LOCALE_DIR, unicode=False)

    def setupLogging(self):
        # initialize logging
        self.soslog = logging.getLogger('sos')
        self.soslog.setLevel(logging.DEBUG)

        logging.VERBOSE  = logging.INFO - 1
        logging.VERBOSE2 = logging.INFO - 2
        logging.VERBOSE3 = logging.INFO - 3
        logging.addLevelName(logging.VERBOSE, "verbose")
        logging.addLevelName(logging.VERBOSE2,"verbose2")
        logging.addLevelName(logging.VERBOSE3,"verbose3")

        # if stdin is not a tty, disable colors and don't ask questions
        if not sys.stdin.isatty():
            self.nocolors = True
            self.batch = True

        # log to a file
        flog = logging.FileHandler(self.logdir + self.LOGFILENAME)
        flog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        flog.setLevel(logging.VERBOSE3)
        self.soslog.addHandler(flog)

        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler(sys.stderr)
        if self.verbosity > 0 or self.debug > 0:
            if self.verbosity > 0:
                console.setLevel(logging.INFO - self.verbosity)
            if self.debug > 0:
                console.setLevel(logging.DEBUG - self.debug + 1)
            self.progressbar = False
        else:
            console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('%(message)s'))
        self.soslog.addHandler(console)

    def loadplugins(self):
        # generate list of available plugins
        for pluginpath in self.pluginpaths.keys():
            if not os.path.isdir(pluginpath):
                continue
            _plugins = os.listdir(pluginpath)
            for _plug in _plugins:
                if not _plug[-3:] == '.py' or _plug[:-3] == "__init__":
                    continue
                self.pluginnamesspaces[_plug]=self.pluginpaths[pluginpath]
                self.plugins.append(_plug)
        self.plugins.sort()

        # validate and load plugins
        for plug in self.plugins:
            plugbase =  plug[:-3]
            try:
                if self.validatePlugin(plug):
                    pluginClass = sos.helpers.importPlugin(".".join([self.pluginnamesspaces[plug], plugbase]), plugbase)
                else:
                    self.soslog.warning(_("plugin %s does not validate, skipping") % plug)
                    self.skippedplugins.append((plugbase, pluginClass(plugbase, self)))
                    continue
                self.plugin_names.append(plugbase)
                # plug-in is valid, let's decide whether run it or not
                if plugbase in self.noplugins:
                    self.soslog.log(logging.VERBOSE, _("plugin %s skipped (--skip-plugins)") % plugbase)
                    self.skippedplugins.append((plugbase, pluginClass(plugbase, self)))
                    continue
                if not pluginClass:
                    self.soslog.log(logging.VERBOSE, _("skipping unknown %s.") % plug)
                    continue
                if not pluginClass(plugbase, self.getCommons()).checkenabled() and not plugbase in self.enabledplugins and not plugbase in self.onlyplugins:
                    self.soslog.log(logging.VERBOSE, _("plugin %s is inactive (use -e or -o to enable).") % plug)
                    self.skippedplugins.append((plugbase, pluginClass(plugbase, self)))
                    continue
                if not pluginClass(plugbase, self.getCommons()).defaultenabled() and not plugbase in self.enabledplugins and not plugbase in self.onlyplugins:
                    self.soslog.log(logging.VERBOSE, "plugin %s not loaded by default (use -e or -o to enable)." % plug)
                    self.skippedplugins.append((plugbase, pluginClass(plugbase, self)))
                    continue
                if self.onlyplugins and not plugbase in self.onlyplugins:
                    self.soslog.log(logging.VERBOSE, _("plugin %s not specified in --only-plugins list") % plug)
                    self.skippedplugins.append((plugbase, pluginClass(plugbase, self)))
                    continue
                self.loadedplugins.append((plugbase, pluginClass(plugbase, self.getCommons())))
            except:
                self.soslog.warning(_("plugin %s does not install, skipping") % plug)
                import traceback
                from StringIO import StringIO
                buf=StringIO()
                traceback.print_exc(None, buf)
                self.soslog.log(logging.DEBUG, buf.getvalue())
                if self.__raisePlugins__:
                    raise
                
    def validatePlugin(self, plugin):
        for pluginpath in self.pluginpaths.keys():
            if self.policy.validatePlugin(pluginpath + plugin):
                return True
        return False
    
    def getCommons(self):
        _commons=dict()

        # Needed for the plugins if not it should get away.
        for (_attr, _key) in self.__commons_attrs.items():
            _commons[_key]=getattr(self, _attr, None)
        _commons["cmdlineopts"]=self._createCmdLineOpts()
        return _commons

    def setupOptions(self):
        # First, gather and process options
        # using the options specified in the command line (if any)
        if self.usealloptions:
            for plugname, plug in self.loadedplugins:
                for name, parms in zip(plug.optNames, plug.optParms):
                    if type(parms["enabled"])==bool:
                        parms["enabled"] = True
        # read plugin tunables from configuration file
        if self.config.has_section("tunables"):
            if not self.plugopts:
                self.plugopts = []

            for opt, val in self.config.items("tunables"):
                self.plugopts.append(opt + "=" + val)

        if self.plugopts:
            opts = {}
            for opt in self.plugopts:
                # split up "general.syslogsize=5"
                try:
                    opt, val = opt.split("=")
                except:
                    val=True
                else:
                    if val.lower() in ["off", "disable", "disabled", "false"]:
                        val = False
                    else:
                        # try to convert string "val" to int()
                        try:    val = int(val)
                        except: pass

                # split up "general.syslogsize"
                try:
                    plug, opt = opt.split(".")
                except:
                    plug = opt
                    opt = True

                try: opts[plug]
                except KeyError: opts[plug] = []
                opts[plug].append( (opt,val) )

            for plugname, plug in self.loadedplugins:
                if opts.has_key(plugname):
                    for opt,val in opts[plugname]:
                        self.soslog.log(logging.VERBOSE, 'setting option "%s" for plugin (%s) to "%s"' % (plugname,opt,val))
                        if not plug.setOption(opt,val):
                            self.soslog.error('no such option "%s" for plugin (%s)' % (opt,plugname))
                            raise SosReportException('no such option "%s" for plugin (%s)' % (opt,plugname))
                    del opts[plugname]
            for plugname in opts.keys():
                self.soslog.error('unable to set option for disabled or non-existing plugin (%s)' % (plugname))
                raise SosReportException('unable to set option for disabled or non-existing plugin (%s)' % (plugname))
            del opt,opts,val

        # error if the user references a plugin which does not exist
        unk_plugs =  [plugname.split(".")[0] for plugname in self.onlyplugins    if not plugname.split(".")[0] in self.plugin_names]
        unk_plugs += [plugname.split(".")[0] for plugname in self.noplugins      if not plugname.split(".")[0] in self.plugin_names]
        unk_plugs += [plugname.split(".")[0] for plugname in self.enabledplugins if not plugname.split(".")[0] in self.plugin_names]
        if len(unk_plugs):
            for plugname in unk_plugs:
                self.soslog.error('a non-existing plugin (%s) was specified in the command line' % (plugname))
            raise SosReportException("Non existend plugins were specified at runtime: %s" %(unk_plugs))
        del unk_plugs

        for plugname, plug in self.loadedplugins:
            self.soslog.log(logging.VERBOSE3, _("processing options from plugin: %s") % plugname)
            names, parms = plug.getAllOptions()
            for optname, optparm  in zip(names, parms):
                self.alloptions.append((plug, plugname, optname, optparm))

        # when --listplugins is specified we do a dry-run
        # which tells the user which plugins are going to be enabled
        # and with what options.

    def listPlugins(self):
        if not len(self.loadedplugins) and not len(self.skippedplugins):
            self.soslog.error(_("no valid plugins found"))
            raise SosReportException(_("no valid plugins found"))

        # FIXME: make -l output more concise
        if len(self.loadedplugins):
            print _("The following plugins are currently enabled:")
            print
            for (plugname,plug) in self.loadedplugins:
                print " %-25s  %s" % (textcolor(plugname,"lblue"),plug.get_description())
        else:
            print _("No plugin enabled.")
        print

        if len(self.skippedplugins):
            print _("The following plugins are currently disabled:")
            print
            for (plugname,plugclass) in self.skippedplugins:
                print " %-25s  %s" % (textcolor(plugname,"cyan"),plugclass.get_description())
        print

        if len(self.alloptions):
            print _("The following plugin options are available:")
            print
            for (plug, plugname, optname, optparm)  in self.alloptions:
                # format and colorize option value based on its type (int or bool)
                if type(optparm["enabled"])==bool:
                    if optparm["enabled"]==True:
                        tmpopt = textcolor("on","lred")
                    else:
                        tmpopt = textcolor("off","red")
                elif type(optparm["enabled"])==int:
                    if optparm["enabled"] > 0:
                        tmpopt = textcolor(optparm["enabled"],"lred")
                    else:
                        tmpopt = textcolor(optparm["enabled"],"red")
                else:
                    tmpopt = optparm["enabled"]

                print " %-21s %-5s %s" % (plugname + "." + optname, tmpopt, optparm["desc"])
                del tmpopt
        else:
            print _("No plugin options available.")

        print

    def diagnosePlugins(self):
        # TODO: Move this in methods
        # Call the diagnose() method for each plugin
        tmpcount = 0
        for plugname, plug in self.loadedplugins:
            self.soslog.log(logging.VERBOSE2, "Performing sanity check for plugin %s" % plugname)
            try:
                plug.diagnose()
            except:
                if self.__raisePlugins__:
                    raise
            tmpcount += len(plug.diagnose_msgs)
        if tmpcount > 0:
            print _("One or more plugins have detected a problem in your configuration.")
            print _("Please review the following messages:")
            print

            fp = open(rptdir + "/diagnose.txt", "w")
            for plugname, plug in self.loadedplugins:
                for tmpcount2 in range(0,len(plug.diagnose_msgs)):
                    if tmpcount2 == 0:
                        self.soslog.warning( textcolor("%s:" % plugname, "red") )
                    self.soslog.warning("    * %s" % plug.diagnose_msgs[tmpcount2])
                    fp.write("%s: %s\n" % (plugname, plug.diagnose_msgs[tmpcount2]) )
            fp.close()

            print
            if not __cmdLineOpts__.batch:
                try:
                    while True:
                        yorno = raw_input( _("Are you sure you would like to continue (y/n) ? ") )
                        if yorno == _("y") or yorno == _("Y"):
                            print
                            break
                        elif yorno == _("n") or yorno == _("N"):
                            return
                    del yorno
                except KeyboardInterrupt:
                    print
                    return


    def helloMsg(self):
        msg = _("""This utility will collect some detailed  information about the
hardware and  setup of your  Red Hat Enterprise Linux  system.
The information is collected and an archive is  packaged under
/tmp, which you can send to a support representative.
Red Hat will use this information for diagnostic purposes ONLY
and it will be considered confidential information.

This process may take a while to complete.
No changes will be made to your system.

""")
        if self.batch:
            print msg
        else:
            msg += _("""Press ENTER to continue, or CTRL-C to quit.\n""")
            try:    raw_input(msg)
            except: print ; return
        del msg
        
    def setupPlugins(self):
        # Call the setup() method for each plugin
        for plugname, plug in self.loadedplugins:
            self.soslog.log(logging.VERBOSE2, "Preloading files and commands to be gathered by plugin %s" % plugname)
            try:
                plug.setup()
            except KeyboardInterrupt:
                raise
            except:
                if self.__raisePlugins__:
                    raise

    def startPluginsCopyFiles(self, pbar):
        # Call the collect method for each plugin
        plugrunning = Semaphore(2)
        for plugname, plug in self.loadedplugins:
            self.soslog.log(logging.VERBOSE, "executing plugin %s" % plugname)
            try:
                if not self.nomultithread:
                    plug.copyStuff(threaded = True, semaphore = plugrunning)
                else:
                    plug.copyStuff()
                    if self.progressbar:
                        pbar.incAmount(plug.eta_weight)
                        pbar.update()
            except KeyboardInterrupt:
                raise
            except:
                if self.__raisePlugins__:
                    raise
        del plugrunning

    def setupProgressBar(self):
        # Setup the progress bar
        # gather information useful for generating ETA
        eta_weight = len(self.loadedplugins)
        for plugname, plug in self.loadedplugins:
            eta_weight += plug.eta_weight
        pbar = progressBar(minValue = 0, maxValue = eta_weight)
        # pbar.max = number_of_plugins + weight (default 1 per plugin)
        return pbar

    def waitForPlugins(self, pbar):
        finishedplugins = []
        while len(self.loadedplugins) > 0:
            plugname, plug = self.loadedplugins.pop(0)
            if not plug.wait(0.5):
                finishedplugins.append((plugname,plug))
                self.soslog.log(logging.DEBUG, "plugin %s has returned" % plugname)
                if self.progressbar:
                    pbar.incAmount(plug.eta_weight)
            else:
                self.soslog.log(logging.DEBUG, "plugin %s still hasn't returned" % plugname)
                self.loadedplugins.append((plugname,plug))
                if self.progressbar:
                    pbar.update()
        self.loadedplugins = finishedplugins
        del finishedplugins

    def saveCopiedFiles(self):
        for plugname, plug in self.loadedplugins:
            for oneFile in plug.copiedFiles:
                try:
                    self.xmlreport.add_file(oneFile["srcpath"], os.stat(oneFile["srcpath"]))
                except:
                    pass

    def analysePlugins(self, pbar):
        # Call the analyze method for each plugin
        for plugname, plug in self.loadedplugins:
            self.soslog.log(logging.VERBOSE2, "Analyzing results of plugin %s" % plugname,)
            try:
                plug.analyze()
            except:
                # catch exceptions in analyse() and keep working
                pass
            if self.progressbar:
                pbar.incAmount()
                pbar.update()

    def generateReportHeader(self, rfd):
        rfd.write("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
        <head>
    <link rel="stylesheet" type="text/css" media="screen" href="donot.css" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Sos System Report</title>
        </head>

        <body>
    """)

    def generateReportPluginNames(self, rfd, plugNames):
        # Create a table of links to the module info
        rfd.write("<hr/><h3>Loaded Plugins:</h3>")
        rfd.write("<table><tr>\n")
        rr = 0
        for i in range(len(plugNames)):
            rfd.write('<td><a href="#%s">%s</a></td>\n' % (plugNames[i], plugNames[i]))
            rr = divmod(i, 4)[1]
            if (rr == 3):
                rfd.write('</tr>')
        if not (rr == 3):
            rfd.write('</tr>')
        rfd.write('</table>\n')

    def generateReportAlerts(self, rfd, allAlerts):
        rfd.write('<hr/><h3>Alerts:</h3>')
        rfd.write('<ul>')
        for alert in allAlerts:
            rfd.write('<li>%s</li>' % alert)
        rfd.write('</ul>')
        
    def generateReportPluginReports(self, rfd):
        # Call the report method for each plugin
        for plugname, plug in self.loadedplugins:
            try:
                html = plug.report()
            except:
                if self.__raisePlugins__:
                    raise
                else:
                    rfd.write(html)

    def generateReportFooter(self, rfd):
        rfd.write("</body></html>")

    def generateReport(self):
        # Make a pass to gather Alerts and a list of module names
        allAlerts = []
        plugNames = []
        for plugname, plug in self.loadedplugins:
            for alert in plug.alerts:
                allAlerts.append('<a href="#%s">%s</a>: %s' % (plugname, plugname, alert))
            plugNames.append(plugname)

        # Generate the header for the html output file
        rfd = open(self.rptdir + "/" + "sosreport.html", "w")
        self.generateReportHeader(rfd)        
        self.generateReportPluginNames(rfd, plugNames)
        self.generateReportAlerts(rfd, allAlerts)
        self.generateReportPluginReports(rfd)
        self.generateReportFooter(rfd)
        rfd.close()

    def postprocPlugins(self):
        # Call the postproc method for each plugin
        for plugname, plug in self.loadedplugins:
            try:
                plug.postproc()
            except:
                if self.__raisePlugins__:
                    raise


    def main(self):
        print
        self.soslog.info ( _("sosreport (version %s)") % __version__)
        print

        if self.autoloadplugins:
            self.loadplugins()
        self.setupOptions()
        
        if self.listplugins:
            self.listPlugins()
            return

        # to go anywhere further than listing the plugins we will need root permissions.
        #
        if self.checkrootuid and os.getuid() != 0:
            print _('sosreport requires root permissions to run.')
            raise SosReportException(_('sosreport requires root permissions to run.'))

        # we don't need to keep in memory plugins we are not going to use
        del self.skippedplugins

        if not len(self.loadedplugins):
            self.soslog.error(_("no valid plugins were enabled"))
            raise SosReportException(_("no valid plugins were enabled"))

        self.helloMsg()

        self.diagnosePlugins()

        self.policy.preWork()

        self.setupPlugins()

        if self.progressbar:
            pbar=self.setupProgressBar()
        else:
            pbar=None
            
        if self.nomultithread:
            self.soslog.log(logging.VERBOSE, "using single-threading")
        else:
            self.soslog.log(logging.VERBOSE, "using multi-threading")

        self.startPluginsCopyFiles(pbar)
        
        # Wait for all the collection threads to exit
        if not self.nomultithread:
            self.waitForPlugins(pbar)

        self.saveCopiedFiles()
        self.xmlreport.serialize_to_file(self.rptdir + "/sosreport.xml")

        self.analysePlugins(pbar)
        
        if self.progressbar:
            pbar.finished()
            sys.stdout.write("\n")

        self.generateReport()
        
        self.postprocPlugins()

        # package up the results for the support organization
        self.policy.packageResults()

        # delete gathered files
        self.policy.cleanDstroot()

        # automated submission will go here
        if not self.upload:
            self.policy.displayResults()
        else:
            self.policy.uploadResults()

        # Close all log files and perform any cleanup
        #logging.shutdown()

if __name__ == '__main__':    
    _sosreport=SosReport(debug=1, verbose=3, batch=True, progressbar=False, nomultithread=True, plugopts=["null.initd=1"])
    _sosreport.checkrootuid=False
    _sosreport.pluginpaths={"./plugins_test": "plugins_test"}
    _sosreport.main()
    print "Output stored to %s" %_sosreport.policy.report_file