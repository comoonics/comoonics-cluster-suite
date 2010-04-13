"""Comoonics bootdisk module

TODO
    create abstraction for bootloader install
here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComBootDisk.py,v 1.5 2010-04-13 13:26:51 marc Exp $
#


__version__ = "$Revision: 1.5 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/storage/ComBootDisk.py,v $

import os
import re

from comoonics import ComSystem
from ComDisk import HostDisk
from comoonics.ComExceptions import ComException

class BootDisk(HostDisk):
    def __init__(self, element, doc):
        HostDisk.__init__(self, element, doc)

    def installBootloader(self, loader="grub"):
        if loader!="grub":
            raise ComException(loader+" not supportet yet")
        self.installBootloaderGrub()


    def scanBootloaderGrub(self):
        #scans bootdisk for a possible grub installation
        #returns (hd0,x) when succeeded
        import tempfile
        __tmp=tempfile.NamedTemporaryFile()

        # This is not working with all devices (e.g. cciss, mpath)
        # So I removed the part.
        #__exp=re.compile("[0-9]*")
        #__dev=__exp.sub("",self.getDeviceName())
        __dev=self.getDeviceName()
        __cmd="""/sbin/grub --batch 2>/dev/null <<EOF | egrep "(hd[0-9]+,[0-9]+)" 1>"""+__tmp.name+"""
        device (hd0) """+__dev+"""
        find /grub/stage2
        quit
        EOF
        """
        # TODO this will not work
        if ComSystem.execLocal( __cmd, """(hd0,1)
""" ):
            raise ComException("cannot find grub on "+__dev)

        __part=__tmp.readline()
        self.log.debug("Found grub loader on " + __part)
        return __part


    def installBootloaderGrub(self):
        # To DO
        # Add some checks if grub install was successfull.

        __part=self.scanBootloaderGrub()
        # This is not working with all devices (e.g. cciss, mpath)
        # So I removed the part.
        #__exp=re.compile("[0-9]*")
        #__dev=__exp.sub("",self.getDeviceName())
        __dev=self.getDeviceName()
        __cmd="""grub --batch 2>/dev/null <<EOF | grep "succeeded" > /dev/null
        device (hd0) """+__dev+"""
        root """ +__part+ """
        setup (hd0)
        quit
        EOF
        """
        if ComSystem.execLocal( __cmd ):
            raise ComException("cannot install grub on "+__dev)

# $Log: ComBootDisk.py,v $
# Revision 1.5  2010-04-13 13:26:51  marc
# - removed os.tempnam
#
# Revision 1.4  2010/03/08 12:30:48  marc
# version for comoonics4.6-rc1
#
# Revision 1.3  2010/02/10 12:49:07  mark
# added .storage path in includes
#
# Revision 1.2  2010/02/09 21:48:51  mark
# added .storage path in includes
#
# Revision 1.1  2009/09/28 15:13:36  marc
# moved from comoonics here
#
# Revision 1.2  2007/02/27 15:55:01  mark
# added support for dm_multipath
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#
# Revision 1.3  2006/06/28 17:23:19  mark
# modified to use DataObject
#
# Revision 1.2  2006/06/23 12:00:28  mark
# moved Log to bottom
#
# Revision 1.1  2006/06/23 07:56:24  mark
# initial checkin (stable)
#
