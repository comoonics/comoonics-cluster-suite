"""
Generic ComAssitant TUI
"""

from snack import *
import logging
import sys

from comoonics import ComLog, odict
from comoonics.ComExceptions import ComException
from ComConfigurationManager import ConfigurationManager

class CancelException(ComException):pass


class ConfigurationManagerTui(object):
    OK=0
    NEXT=1
    MODIFY=2
    SAVE=3
    RUN=4
    CANCEL=-1
    
    def __init__(self, controller):
        """
        @param: controller, a list of AssistantControllers
        """
        self.controller=controller
        self.screen = SnackScreen()
        self.confignames=self.controller.getCompleteConfigSetNames()
            
    
    def run(self, warning=None):
        ''' @returns [name, type, direction] '''
        #items=["a", "b"]
        result=None
        while True:
            self.confignames=self.controller.getCompleteConfigSetNames()
            names=self.confignames.keys()
            names.sort()
            if len(names) != 0: 
                _res=ListboxChoiceWindow(self.screen, "Configuration Sets", "Select configuration set", names, buttons = ('Next', 'New', 'Rename', 'Delete', 'Cancel'), width = 40, scroll = 1, height = -1, default = None, help = None)
            else:
                _res=[ButtonChoiceWindow(self.screen, "Configuration Sets", "No Configuration sets defined", buttons = ['New', 'Cancel'], width = 40, help = None)]

            if _res[0] == "cancel": break
            if _res[0] == "new":
                self._run_create()
            if _res[0] == "rename":
                _name=names[_res[1]]
                _type=self.confignames.get(_name)
                _newname=self._run_rename(_name)
                if _newname:
                    self.controller.renameConfigSet(_name, _type, _newname)
            if _res[0] == "delete":
                self._run_delete(names[_res[1]])
            if _res[0] == "next":
                _name=names[_res[1]]
                _type=self.confignames.get(_name)
                set = self.controller.getConfigStore().getConfigTypeStoreByName(_type).getConfigset(_name)
                direction = self._run_direction(_name, set.getDirections(ordered=True))
                if direction == None: continue
                result=[_name,_type,direction]
                break
        self.cleanup()
        return result
         
    def _run_direction(self, name, directions):
        _res=ListboxChoiceWindow(self.screen, "Mode Selection", "You selected %s\nWhat do you want to do ?" %name, directions, buttons = ('Next', 'Cancel'), width = 40, scroll = 0, height = -1, default = None, help = None)
        if _res[0] != "next": return
        direction = directions[_res[1]]
        return direction
    
    def _run_delete(self, name):
        if self._run_warning("This will delete configset %s" %name) == self.OK:
            self.controller.deleteConfigSet(name, self.confignames[name])
        
    def _run_create(self):
        templatetypes=self.controller.getCompleteConfigTemplateSetNames()
        if len(templatetypes) != 0: 
            _res=ListboxChoiceWindow(self.screen, "Configuration Types", "Select type of new configuration set", templatetypes, buttons = ('Create', 'Cancel'), width = 40, scroll = 1, height = -1, default = None, help = None)
        else:
            _res=[ ButtonChoiceWindow(self.screen, "Error", "No valid configurationset templates defined", buttons = [ 'Cancel' ]) ]
        if _res[0]!="create": return 
        type=templatetypes[_res[1]]
        _res=EntryWindow(self.screen, "New Configuration", "Name of the new configuration set", ['Name'], allowCancel = 1, width = 40, entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None)
        if _res[0]!="ok": return
        name=_res[1][0]
        self.controller.createConfigSet(name, type)
        
    def _run_rename(self, oldname=""):
        _res=EntryWindow(self.screen, "Rename configuration set", "Enter new name of the configuration set\nOld name: %s" %oldname, ['New name:'], allowCancel = 1, width = 40, entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None)
        if _res[0]!="ok": return
        name=_res[1][0]
        return name
    
    def _run_warning(self, warning):
        _rec=ButtonChoiceWindow(self.screen, "Are you sure ?", warning, buttons = [ 'Ok', 'Back' ]) 
        if _rec == "ok":
            return self.OK
        else:
            return self.CANCEL
         
    
    def _exit(self, val):
        self.cleanup()
        raise CancelException()
        
        
    def getEntryWindow(self, screen):
        w = EntryWindow(screen ,"Com-ec Assistant", "text", ("a", "b", "c", "d", "e", "f", "g"), buttons = [ 'Ok', 'Scan', 'Cancel' ])
        w.run()
        
        
    def cleanup(self):
        self.screen.finish()
    
def ButtonWindow(screen, title, text, allowCancel = 1, width = 40,
        entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None):
    """
    EntryWindow(screen, title, text, prompts, allowCancel = 1, width = 40,
        entryWidth = 20, buttons = [ 'Ok', 'Cancel' ], help = None):
    """
    bb = ButtonBar(screen, buttons);
    t = TextboxReflowed(width, text)

    g = GridFormHelp(screen, title, help, 1, 3)
    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(bb, 0, 1, growx = 1)

    result = g.runOnce()
 
    return [bb.buttonPressed(result)]

    
def test():
    ComLog.setLevel(logging.DEBUG)
    manager=ConfigurationManager("/tmp/cmtest")
    manager.scanConfigs()
    manager.scanConfigTemplates()
    manager.scanConfigInfodefs()
    
    tui = ConfigurationManagerTui(manager)
    result = tui.run()
#    at.cleanup()
#    ac.printDocument()
    if result==None: return None
    set=manager.getConfigStore().getConfigTypeStoreByName(result.get("type")).getConfigset(result.get("name"))
    infodef=manager.getConfigStore().getConfigTypeStoreByName(result.get("type")).getConfigInfodefset()
    return [set, infodef, direction]
    
if __name__=="__main__":
    print test()
        