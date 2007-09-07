""" Comoonics sysrq representation
This module just represents the sysrq implementation as DataObject

Example Configuration:
    <sysrq settrigger="(true|false)" command="(rebootf|reboot|locks|sigterm|oom_kill|kgdb|help|kill|sak|memory|niceable|shutoff|regs|timers|kbd_xlate|sync|tasks|readonly|voyager|blocked|xmon|log0-log9)"/>
    <sysrq settrigger="(true|false)">
      <command name=".."/>+
    </sysrq>

The commands are mapped to the following sysrq-keys:
rebootf:   b
reboot:    c
locks:     d
sigterm:   e
oom_kill:  f
kgdb:      g
help:      h
kill:      i
sak:       k
memory:    m
niceable:  n
shutoff:   o
regs:      p
timers:    q
kbd_xlate: r
sync:      s
tasks:     t
readonly:  u
voyager:   v
blocked:   w
xmon:      x
log0-log9: 0-9

if settrigger is true the trigger will be set if not and restored afterwords. Is settrigger is false the trigger will
be left as it is.

see http://www.mjmwired.net/kernel/Documentation/sysrq.txt
"""

# here is some internal information
# $Id: ComSysrq.py,v 1.1 2007-09-07 14:44:41 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComSysrq.py,v $

from ComDataObject import DataObject
import ComSystem, ComLog
from ComSystem import ExecLocalException
import os.path
import os

class Sysrq(DataObject):
    logger=ComLog.getLogger("comoonics.ComSysrq.Sysrq")
    TAGNAME="sysrq"
    CMD_MAPPINGS={
        "rebootf": "b",
        "reboot": "c",
        "locks": "d",
        "sigterm": "e",
        "oom_kill": "f",
        "kgdb": "g",
        "help": "h",
        "kill": "i",
        "sak": "k",
        "memory": "m",
        "niceable": "n",
        "shutoff": "o",
        "regs": "p",
        "timers": "q",
        "kbd_xlate": "r",
        "sync": "s",
        "tasks": "t",
        "readonly": "u",
        "voyager": "v",
        "blocked": "w",
        "xmon": "x",
        "log0": "0",
        "log1": "1",
        "log2": "2",
        "log3": "3",
        "log4": "4",
        "log5": "5",
        "log6": "6",
        "log7": "7",
        "log8": "8",
        "log9": "9",
        }
    CMD_HELP={
        "rebootf": "Will immediately reboot the system without syncing or unmounting your disks.",
        "reboot": "Will perform a kexec reboot in order to take a crashdump.",
        "locks": "Shows all locks that are held.",
        "sigterm": "Send a SIGTERM to all processes, except for init.",
        "oom_kill": "Will call oom_kill to kill a memory hog process.",
        "kgdb": "Used by kgdb on ppc and sh platforms.",
        "help": "Will display help (actually any other key than those listed above will display help. but 'h' is easy to remember :-)",
        "kill": "Send a SIGKILL to all processes, except for init.",
        "sak": """Secure Access Key (SAK) Kills all programs on the current virtual console.
NOTE: See important comments below in SAK section.""",
        "memory": "Will dump current memory info to your console.",
        "niceable": "Used to make RT tasks nice-able",
        "shutoff": "Will shut your system off (if configured and supported).",
        "regs": "Will dump the current registers and flags to your console.",
        "timers": "Will dump a list of all running timers.",
        "kbd_xlate": "Turns off keyboard raw mode and sets it to XLATE.",
        "sync": "Will attempt to sync all mounted filesystems.",
        "tasks": "Will dump a list of current tasks and their information to your console.",
        "readonly": "Will attempt to remount all mounted filesystems read-only.",
        "voyager": "Dumps Voyager SMP processor info to your console.",
        "blocked": "Dumps tasks that are in uninterruptable (blocked) state.",
        "xmon": "Used by xmon interface on ppc/powerpc platforms.",
        "log0": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log1": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log2": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log3": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log4": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log5": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log6": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log7": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log8": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        "log9": """Sets the console log level, controlling which kernel messages
will be printed to your console. ('0', for example would make
it so that only emergency messages like PANICs or OOPSes would
make it to your console.)""",
        }
    TRIGGER_FILE="/proc/sysrq-trigger"
    TRIGGER_SET_FILE="/proc/sys/kernel/sysrq"

    def _createCommand(_name, _doc):
        _element=_doc.createElement("command")
        _element.setAttribute("name", _name)
        return _element
    _createCommand=staticmethod(_createCommand)

    def _createElement(command=None, settrigger=True):
        import xml.dom
        _impl=xml.dom.getDOMImplementation()
        _doc=_impl.createDocument(None, Sysrq.TAGNAME, None)
        _element=_doc.documentElement
        if command and type(command)==list:
            for _cmd in command:
                _element.appendChild(Sysrq._createCommand(_cmd, _doc))
        elif command:
            _element.setAttribute("command", command)
        if settrigger:
            _element.setAttribute("settrigger", "true")
        elif settrigger==False:
            _element.setAttribute("settrigger", "false")
        else:
            _element.setAttribute("settrigger", "true")
        return (_element, _doc)
    _createElement=staticmethod(_createElement)

    def __init__(self, *params, **kwds):
        """
        __init__(self, element, doc)
        __init__(self, doc=doc, element=element)
        __init__(self, command=cmd, [settrigger=*True|False])
        __init__(self, commands=list<cmd>, [settrigger=*True|False])
        __init__(self, [settrigger=*True|False])
        @element: the element of the modification
        @doc: the root document
        @command: sysrq command to be executed
        @commands: list of sysrq commands to be executed
        @settrigger: set the trigger or not
        """
        Sysrq.logger.debug("__init__(params: %s, kwds: %s" %(params, kwds))
        if len(params)==0 and len(kwds)==0:
            (element, doc)=Sysrq._createElement()
        elif params and len(params)==2:
            element=params[0]
            doc=params[1]
        elif kwds and kwds.has_key("element") and kwds.has_key("doc"):
            element=kwds["element"]
            doc=kwds["doc"]
        elif kwds and kwds.has_key("command"):
            (element, doc)=Sysrq._createElement(kwds.get("command"), kwds.get("settrigger", True))
        elif kwds and kwds.has_key("commands"):
            (element, doc)=Sysrq._createElement(kwds.get("commands"), kwds.get("settrigger", True))
        else:
            raise TypeError("__init__() takes exactly 2 arguments or different keys. (%u given)" %len(params))
        super(Sysrq, self).__init__(element, doc)

    def getCommands(self):
        _cmds=list()
        if self.hasAttribute("command"):
            _cmds.append(self.getAttribute("command"))
        else:
            for _cmdelement in self.getElement().getElementsByTagName("command"):
                _cmds.append(_cmdelement.getAttribute("name"))
        return _cmds

    def getCmdKey(self, _command):
        return Sysrq.CMD_MAPPINGS[_command]

    def doCommands(self):
        for command in self.getCommands():
            ComSystem.execMethod(self.doCommand, command)

    def doCommand(self, _command):
        trigger=file(Sysrq.TRIGGER_FILE,"w")
        trigger.write(self.getCmdKey(_command))
        trigger.close()

    def setTrigger(self):
        if self.getAttribute("settrigger", "false")=="true":
            trigger=file(Sysrq.TRIGGER_SET_FILE,"r+")
            self.oldtrigger=trigger.read(50)
            trigger.write("1")
            trigger.close()
    def restoreTrigger(self):
        if self.oldtrigger:
            trigger=file(Sysrq.TRIGGER_SET_FILE,"w")
            trigger.write(self.oldtrigger)
            trigger.close()

def main():
    import logging
    ComLog.setLevel(logging.DEBUG)
    _validcommands=[
        "locks",
        "help",
        "memory",
        "regs",
        "timers",
        "sync",
        "tasks",
        "voyager",
        "blocked",
        "xmon",
        "log0",
        "log1",
        "log2",
        "log3",
        "log4",
        "log5",
        "log6",
        "log7",
        "log8",
        "log9",
                    ]
    _validcommands.sort()
    _sysrq=Sysrq(commands=_validcommands, settrigger=True)
    _sysrq2=Sysrq()
    print "Sysrq: %s"%_sysrq
    print "setTrigger()"
    _sysrq.setTrigger()
    print "doCommands(%s)"%_sysrq.getCommands()
    _sysrq.doCommands()
    print "sysrq.doCommand(help)"
    _sysrq2.doCommand("help")
    print "restoreTrigger()"
    _sysrq.restoreTrigger()

if __name__=="__main__":
    main()

#####################
# $Log: ComSysrq.py,v $
# Revision 1.1  2007-09-07 14:44:41  marc
# initial revision
#