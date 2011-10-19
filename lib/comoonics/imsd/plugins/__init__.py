"""

Comoonics fenceacksv plugins

Provides plugins to be executed in the fenceacksv

"""

__plugins=dict()

from ComPlugin import Plugin
from ComSysrqPlugin import SysrqPlugin
from ComSysreportPlugin import SysreportPlugin

def getPlugins():
    """ returns all registered plugins """
    return __plugins.values()

def getPluginnames():
    """ returns the names of all registered plugins """
    return __plugins.keys()

def getPlugin(_name):
    """ returns the named plugin """
    return __plugins[_name]

def getRegistry():
    """ returns the registry itself """
    return __plugins

def addPlugin(_plugin):
    """ adds a given plugin to the registry """
    __plugins[_plugin.getName()]=_plugin

try:
    addPlugin(SysrqPlugin())
except:
    pass
try:
    addPlugin(SysreportPlugin())
except:
    pass

################
# $Log: __init__.py,v $
# Revision 1.1  2007-09-07 14:42:28  marc
# initial revision
#