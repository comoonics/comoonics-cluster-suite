#!/usr/bin/python
"""Assistant for the Comoonics desatster recovery DVD


"""

# here is some internal information
# $Id: com-ec-administrator-tui.py,v 1.2 2008-11-06 15:43:56 mark Exp $
#

__version__ = "$Revision: 1.2 $"
__description__="""
Comoonics Assistant to create a Comoonics desaster recovery dvd
"""
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/bin/com-ec-administrator-tui.py,v $

import sys
import logging
from optparse import OptionParser, IndentedHelpFormatter

sys.path.append("../lib")


from comoonics import ComLog, ComSystem
from comoonics.ComExceptions import ComException

from comoonics.assistant.ComAssistantTui import AssistantTui, CancelException
from comoonics.assistant.ComECAssistantController import ECAssistantController
from comoonics.assistant.ComConfigurationManagerTui import ConfigurationManagerTui
from comoonics.assistant.ComConfigurationManager import ConfigurationManager


#default settings
# TODO
# The initial xml document must be created through an inital setup like method.
# -> e.g. an installation assistant.
# We'd need a generic localclone xml generator.
# infos needed at the moment:
# do we use partitions within lvm or not ?
# Simple solution: We could add several xml and corresponding template files and create symlinks 
# by the use of a setup assistant. :-)

 
CONFIGURATION_PATH="/etc/comoonics/enterprisecopy/xml-dr"
XSL_PATH="/opt/atix/comoonics-cs/xsl"

WARNING_MESSAGE="Warning Message"

NAME_LIVECD_EXTRAS="Backup temp path"

def setDebug(option, opt, value, parser):
	ComLog.setLevel(logging.DEBUG)
	setattr(parser.values, option.dest, True)

def setSimulate(option, opt, value, parser):
	ComSystem.__EXEC_REALLY_DO="simulate"
	setattr(parser.values, option.dest, True)

def setAsk(option, opt, value, parser):
	ComSystem.__EXEC_REALLY_DO="ask"
	setattr(parser.values, option.dest, True)
	
def setReally(option, opt, value, parser):
	setattr(parser.values, option.dest, False)
	
def setFast(option, opt, value, parser):
	setattr(parser.values, option.dest, False)

def setConfigPath(option, opt, value, parser):
	print "setConfigPath %s" %value
	print option
	print opt
	print parser
	CONFIGURATION_PATH=value

	
def exit(value, text=""):
	print text
	sys.exit(value)

ComLog.setLevel(logging.INFO)
log=ComLog.getLogger("comoonics-assistant")

parser = OptionParser(description=__doc__, version=__version__)

# Default Options
parser.add_option("-D", "--debug", dest="debug", default=False, action="callback", callback=setDebug, help="Debug")
parser.add_option("-s", "--simulate", dest="debug", default=False, action="callback", callback=setSimulate, help="Simulate")
parser.add_option("-a", "--ask", dest="debug", default=False, action="callback", callback=setAsk, help="Ask")
parser.add_option("-X", "--xml", dest="really", default=True, action="callback", callback=setReally)
parser.add_option("-F", "--fast", dest="scan", default=True, action="callback", callback=setFast)
parser.add_option("-p", "--path", dest="configpath", help="Set path for configuration files",
				  action="store", default=CONFIGURATION_PATH, type="string")
#

(options, args) = parser.parse_args()

# start the configuration manager

manager=ConfigurationManager(options.configpath)
manager.scanConfigs()
manager.scanConfigTemplates()
manager.scanConfigInfodefs()
    
tui = ConfigurationManagerTui(manager)
result = tui.run()

if result == None: exit(0)

name, type, direction = result

log.debug("result: name: %s type: %s direction %s" %(name, type, direction))

store = manager.getConfigStore().getConfigTypeStoreByName(type)
configset = store.getConfigset(name)
infodefset = store.getConfigInfodefset()

configfile=configset.getConfiguration(direction).getConfigFile()
infodef=infodefset.getConfiguration(direction).getConfigFile()

log.debug(direction)
log.debug("config: %s", configfile)
log.debug("infodef: %s", infodef)

ac_main=ECAssistantController(configfile, infodef, xsl_file=True, scan=options.scan)
ac_2 = None
aclist=[ac_main]

warning="This will start the %s process. All data on the selected target will be destroyed" %direction
tuititle="Comoonics EC - %s %s" %(direction.capitalize(), name)

if direction == "backup":
	# we want to configure the backup 
	# FIXME add a cmdline switch
	#  - make things generic 
	try:
		rst_configfile=configset.getConfiguration("restore").getConfigFile()
		rst_infodef=infodefset.getConfiguration("restore").getConfigFile()
		ac_2 = ECAssistantController(rst_configfile, rst_infodef)
		aclist.append(ac_2)
	except Exception:
		log.warning("no restore configuration found")
	
tui = AssistantTui(aclist, tuititle)

if tui.run(warning):
	if ac_2: 
		ac_2.writeXMLFile(rst_configfile)
	ac_main.run(options.really)
else:
	print "Exiting on user request ..."



#if tui.run(WARNING_MESSAGE): 
#	# we need the path where all extras will be:
#	if tui.getInfoDict().has_key(NAME_LIVECD_EXTRAS):
#		extras_path=tui.getInfoDict().get(NAME_LIVECD_EXTRAS).getValue()
#		log.debug("drrestore file: %s/%s" %(extras_path, DRRESTORE_XML_NAME))
#		ac_drrestore.writeXMLFile("%s/%s" %(extras_path, DRRESTORE_XML_NAME))
#	else:
#		log.debug("key %s not found" %NAME_LIVECD_EXTRAS)
# 	if not options.livecd_only:	ac_drbackup.run(options.really)
# 	if not options.tar_only: ac_mkrestorecd.run(options.really)
#else:
#	print "Exiting ..."


