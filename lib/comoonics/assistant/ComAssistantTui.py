"""
Generic ComAssitant TUI
"""

from snack import *
import logging
import sys

from comoonics import ComLog, odict
from ComAssistantInfo import *
from ComECAssistantController import *
from comoonics.ComExceptions import ComException

class CancelException(ComException):pass

class AssistantInfoRadioBar(Grid):
    def __init__(self, screen, info):
        """
        @param buttonarray is an array in the form ([radiobutton, widget], ...)
        """
        self.group = RadioGroup()
        self.list = []
        self.item = 0
        self.info=info
        
        Grid.__init__(self, 1, len(info.getSuggestions())+6)
        
        self.setField(Textbox(20, 1, "Default:"), 0, 0,padding = (0, 0, 0, 0), anchorLeft = 1)
        db = self.group.add(info.getDefault(), info.getDefault(), \
                            info.getValue() == info.getDefault())
        
        #print >> sys.stderr, "default: %s, value %s" %(info.getDefault(), info.getValue())

        db.setCallback(self._hasManualToggled)    
        self.setField(db, 0, 1, (0, 0, 0, 0), anchorLeft = 1, growx = 1)
        #self.setField(dt, 1, self.item)
        self.setField(Textbox(20, 1, "Detected:"), 0, 2,padding = (0, 0, 0, 0), anchorLeft = 1)
       
        self.item = self.item + 3
        self.list.append(db)
        for value in info.getSuggestions():
            b = self.group.add(value, value, info.getValue() == value )
            b.setCallback(self._hasManualToggled) 
            self.setField(b, 0, self.item, (0, 0, 1, 0), anchorLeft = 1, growx = 1)
            #self.setField(t, 1, self.item)
            self.item = self.item + 1
        
        self.setField(Textbox(20, 1, "Manual:"), 0, self.item ,padding = (0, 0, 0, 0), anchorLeft = 1)
        self.item = self.item + 1
        self.dm = self.group.add("edit", "manual", info.getValue() == info.getManual())
        self.dm.setCallback(self._hasManualToggled)
        self.manualentry = Entry(15, info.getManual())
        self.manualentry.setFlags(FLAG_DISABLED, sense=not(self.dm.selected()))
        self.setField(self.dm, 0, self.item, (0, 0, 1, 0), anchorLeft = 1, growx = 1)
        self.setField(self.manualentry, 0, self.item+1, (0, 0, 1, 0), anchorLeft = 1)
        self._hasManualToggled()

    def _hasManualToggled(self):
        self.manualentry.setFlags(FLAG_DISABLED, sense=self.dm.selected())
            
    def getSelection(self): 
        #print >> sys.stderr, "getSelection" 
        if self.group.getSelection() == "manual":
            self.info.setManual(self.manualentry.value())
            return self.manualentry.value()
        return self.group.getSelection()


class AssistantTui(object):
    OK=0
    NEXT=1
    MODIFY=2
    SAVE=3
    RUN=4
    CANCEL=-1
    
    def __init__(self, controller, title="Com-EC Assistant"):
        """
        @param: controller, a list of AssistantControllers
        """
        self.title=title
        self.controller=controller
        self.infodict=self._build_infodict()
        self.screen = SnackScreen()
        
    def getInfoList(self):
        return self.infodict.values()
    
    def getInfoDict(self):
        return self.infodict
         
    def run(self, warning=None):
        step=self.OK
        try: 
            while True:
                _ret = self._run_confirmation()
                if _ret == self.SAVE:
                    self._run_save()
                if _ret == self.MODIFY:
                    self._run_collector()
                if _ret == self.RUN:
                    if warning:
                        _rc = self._run_warning(warning)
                        if _rc == self.CANCEL:
                            continue
                    self.cleanup()
                    return True                 
        except CancelException:
            self.cleanup()
            return False
        
    def _build_infodict(self):
        _dict=odict.Odict()
        for _controller in self.controller:
            _tdict=_controller.getInfoDict()
            for _key in _tdict.iterkeys():
                if not _dict.has_key(_key):
                    _dict[_key]=_tdict.get(_key)
                else:
                    _tdict.get(_key).setValue(_dict.get(_key).getValue())
        return _dict
         
    def _run_warning(self, warning):
        _rec=ButtonChoiceWindow(self.screen, "Are you sure ?", warning, buttons = [ 'Ok', 'Back' ]) 
        if _rec == "ok":
            return self.OK
        else:
            return self.CANCEL
         
    def _run_confirmation(self):
        _button = ConfirmationWindow(self.screen, self.title, self.getInfoList())
        if _button == "start": 
            return self.RUN
        if _button == "modify":
            return self.MODIFY
        if _button == "save":
            return self.SAVE
        if _button == "exit":
            raise CancelException()
        
    def _run_collector(self, page=0):
        _list=self.getInfoList()
        i=page
        while i < len(_list):
            _info=_list[i]
            if i == 0:
                _buttons=[ 'Next', 'Return' ]
            else:
                _buttons=[ 'Next', 'Previous', 'Return' ]
            _button, _value = AssistantWindow(self.screen, self.title, _info, buttons=_buttons)
            if _button == "next":
                i=i+1
                self._set_info_value(_info.getName(), _value)
            if _button == "previous":
                i=i-1
                self._set_info_value(_info.getName(), _value)
            if _button == "return":
                return self.CANCEL
        return self.NEXT
        
    def _run_save(self):
        try:
            for _controller in self.controller:
                _controller.save()
            _msg="Save complete"
        except Exception, e:
            _msg="An error occured:%s" %e
        ButtonChoiceWindow(self.screen, "Save", _msg, buttons = [ 'Ok' ]) 

        
        
    def _set_info_value(self, key, value):
        for _controller in self.controller:
            if _controller.getInfoDict().has_key(key):
                _controller.getInfoDict().get(key).setValue(value)
    
    def _exit(self, val):
        self.cleanup()
        raise CancelException()
        
        
    def getEntryWindow(self, screen):
        w = EntryWindow(screen ,self.title, "text", ("a", "b", "c", "d", "e", "f", "g"), buttons = [ 'Ok', 'Scan', 'Cancel' ])
        w.run()
        
        
    def cleanup(self):
        self.screen.finish()


    

def AssistantWindow(screen, title, info, width = 40, buttons = [ 'Next', 'Previous', 'Return' ], help = None):
    """
    EntryWindow():
    """
    bb = ButtonBar(screen, buttons);
    rb = AssistantInfoRadioBar(screen, info)
    t = TextboxReflowed(width, info.getComment())
   
    g = GridFormHelp(screen, title, help, 1, 4)

    g.add(Label(info.getName()), 0, 0, padding = (0, 0, 1, 0), anchorLeft = 0)
    g.add(t, 0, 1, padding = (0, 0, 0, 1))
    g.add(bb, 0, 3, growx = 1)
    g.add(rb, 0, 2, padding = (0, 0, 0, 1))

    result = g.runOnce()

    return (bb.buttonPressed(result), rb.getSelection())

def ConfirmationWindow(screen, title, infolist, width = 40, buttons = [ 'Start', 'Modify', 'Save', 'Exit' ], help = None):

    bb = ButtonBar(screen, buttons);
    ig=Grid(2, len(infolist))
    i=0
    for _info in infolist:
        ig.setField(Label("%s: " %_info.getName()), 0, i, padding = (0, 0, 1, 0), anchorLeft = 1)
        ig.setField(Label("%s" %_info.getValue()), 1, i, padding = (0, 0, 1, 0), anchorLeft = 1)
        i=i+1                               
    
    g = GridFormHelp(screen, title, help, 1, 3)

    g.add(Textbox(20, 1, "Current settings:"), 0, 0,padding = (0, 0, 0, 1), anchorLeft = 1)
    g.add(ig, 0, 1, padding = (0, 0, 0, 1))
    g.add(bb, 0, 2, growx = 1)
 
    result = g.runOnce()

    return (bb.buttonPressed(result))
   
    
    
def test():
    ComLog.setLevel(logging.DEBUG)
    ac=ECAssistantController("./localclone.xml", "./infodef.xml", "/opt/atix/comoonics-cs/xsl/localclone.xsl", scan=True)
    ac2=ECAssistantController("./createlivecd.xml", "./createlivecd.infodef.xml", scan=True)

    at = AssistantTui([ac2, ac])
    result = at.run()
#    at.cleanup()
#    ac.printDocument()
    
if __name__=="__main__":
    test()
        