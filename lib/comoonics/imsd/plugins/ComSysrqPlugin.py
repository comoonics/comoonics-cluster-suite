"""Comoonics Sysrq Plugin interface for fenceacksv

"""

from ComPlugin import Plugin
from comoonics.ComSysrq import Sysrq

# here is some internal information
# $Id: ComSysrqPlugin.py,v 1.1 2007-09-07 14:42:28 marc Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/fenceacksv/plugins/ComSysrqPlugin.py,v $

class SysrqPlugin(Plugin):
    """
Linux Magic System Request Key Hacks
Documentation for sysrq.c
Last update: 2007-MAR-14

*  What is the magic SysRq key?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is a 'magical' key combo you can hit which the kernel will respond to
regardless of whatever else it is doing, unless it is completely locked up.

*  Okay, so what can I use them for?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Well, un'R'aw is very handy when your X server or a svgalib program crashes.

sa'K' (Secure Access Key) is useful when you want to be sure there is no
trojan program running at console which could grab your password
when you would try to login. It will kill all programs on given console,
thus letting you make sure that the login prompt you see is actually
the one from init, not some trojan program.
IMPORTANT: In its true form it is not a true SAK like the one in a :IMPORTANT
IMPORTANT: c2 compliant system, and it should not be mistaken as   :IMPORTANT
IMPORTANT: such.                                                   :IMPORTANT
       It seems others find it useful as (System Attention Key) which is
useful when you want to exit a program that will not let you switch consoles.
(For example, X or a svgalib program.)

re'B'oot is good when you're unable to shut down. But you should also 'S'ync
and 'U'mount first.

'C'rashdump can be used to manually trigger a crashdump when the system is hung.
The kernel needs to have been built with CONFIG_KEXEC enabled.

'S'ync is great when your system is locked up, it allows you to sync your
disks and will certainly lessen the chance of data loss and fscking. Note
that the sync hasn't taken place until you see the "OK" and "Done" appear
on the screen. (If the kernel is really in strife, you may not ever get the
OK or Done message...)

'U'mount is basically useful in the same ways as 'S'ync. I generally 'S'ync,
'U'mount, then re'B'oot when my system locks. It's saved me many a fsck.
Again, the unmount (remount read-only) hasn't taken place until you see the
"OK" and "Done" message appear on the screen.

The loglevels '0'-'9' are useful when your console is being flooded with
kernel messages you do not want to see. Selecting '0' will prevent all but
the most urgent kernel messages from reaching your console. (They will
still be logged if syslogd/klogd are alive, though.)

t'E'rm and k'I'll are useful if you have some sort of runaway process you
are unable to kill any other way, especially if it's spawning other
processes.

    """
    def __init__(self):
        super(SysrqPlugin, self).__init__("sysrq")
        self._sysrq=Sysrq()
        for _commandname in Sysrq.CMD_MAPPINGS:
            self.addCommand(_commandname, self._sysrq.doCommand, self._sysrq.CMD_HELP[_commandname], _commandname)
    def doPre(self, _name, *params, **kwds):
        self._sysrq.setTrigger()
    def doPost(self, _name, *params, **kwds):
        self._sysrq.restoreTrigger()

########################
# $Log: ComSysrqPlugin.py,v $
# Revision 1.1  2007-09-07 14:42:28  marc
# initial revision
#