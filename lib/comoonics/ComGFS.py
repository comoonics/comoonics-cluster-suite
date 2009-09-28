#!/usr/bin/python
"""Comoonics GFS module

provides analysis functions and the like for gfs

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComGFS.py,v $

import os
import os.path
import re
import sys
import logging
import fcntl
import struct
import array
from exceptions import OSError, IndexError, ValueError

from comoonics import ComSystem

class GFSError(OSError):
    def __init__(self, msg):
        self.value=msg
    def __str__(self):
        return "%s: %s" %(self.value, os.strerror(os.error))

class GFS(object):
    """
    GFS Class as base class for any GFS Filesystem
    """

    logger=logging.getLogger("comoonics.ComGFS.GFS")

    DEV_PATH="/dev"

    PROC_FS="/proc/fs/gfs"
    PROC_MOUNTS="/proc/mounts"

    LIST_CMD="list"
    LIST_SIZE=1048576
    LIST_MATCH=re.compile("(\S+)\s(\S+)\s(\S+):(\S+)\.(\S+)", re.I)

    LOCKDUMP_CMD="lockdump %s"
    LOCKDUMP_SIZE=4194304

    GFS_TYPE="gfs"

    GFS_SUPER_IOCTL=18221

    GFS_TOOL="/sbin/gfs_tool"
    COUNTERS_CMD="counters"
    COUNTERS_MATCH_NUMBER=re.compile("^\s*(?P<key>.+)\s(?P<value>\d+)$")
    COUNTERS_MATCH_PERCENTAGE=re.compile("^\s*(?P<key>.+)\s(?P<value>[0-9.]+)%$")

    def __init__(self, *_params, **_keys):
        self.glockwriter=getLockdumpWriter()
        self.counterswriter=getCountersWriter()
        self.pids=dict()
        self.cookie=None
        self.filename=None
        self.device=None
        _mountpoint=None
        if _keys.has_key("filename"):
            self.filename=_keys["filename"]
        elif _keys.has_key("file"):
            self.filename=_keys["file"]
        elif _keys.has_key("mountpoint"):
            _mountpoint=_keys["mountpoint"]
        elif _keys.has_key("mp"):
            _mountpoint=_keys["mp"]
        elif _keys.has_key("device"):
            _mountpoint=_keys["device"]
        elif _keys.has_key("dev"):
            _mountpoint=_keys["dev"]

        if len(_params)>0 and _params[0]:
            if os.path.isfile(_params[0]):
                self.filename=_params[0]
            else:
                _mountpoint=_params[0]

        if _mountpoint and not self.getDevCookie(_mountpoint):
            raise GFSError, "Cannot find cookie for mountpoint %s" %_mountpoint
        if hasattr(self, "mountpoint"):
            self.counterswriter.prefix=self.mountpoint

    def getDevCookie(self, mountpoint):
        if not self.getDeviceFromMountpoint(mountpoint):
            raise GFSError, "Cannot find devicename for mountpoint %s" %mountpoint
        if not self.getList():
            raise GFSError, "Cannot find or resolv filesystem for mountpoint %s" %mountpoint

        if hasattr(self, "cookie"):
            return self.cookie
        else:
            return None

    def getDeviceFromMountpoint(self, mountpoint):
        _mounts=open(self.PROC_MOUNTS)
        for _mount in _mounts:
            (_from, _to, _type, _opts, _x, _y)=_mount.split(" ")
            if mountpoint==_to and _type==self.GFS_TYPE:
                self.device=_from
                self.mountpoint=_to
                self.opts=_opts
            elif mountpoint==_from and _type==self.GFS_TYPE:
                self.device=_from
                self.mountpoint=_to
                self.opts=_opts
        return self.device

    def compareDevices(dev1, dev2):
        """ Compares two devices by major and minor and returns True/False """
        _stat1=os.stat(dev1)
        _stat2=os.stat(dev2)
        return _stat1.st_rdev == _stat2.st_rdev
    compareDevices=staticmethod(compareDevices)

    def _cmdPROC_FS(cmd, return_size, returnfsnoread=False):
        _fd=os.open(GFS.PROC_FS, os.O_RDWR)
        if _fd < 0:
            raise GFSError, "Cannot open %s" %(GFS.PROC_FS)

        if (os.write(_fd, cmd) != len(cmd)):
            raise OSError, "Cannot write command %s" %(cmd)

        if returnfsnoread:
            return _fd
        else:
            _buf=os.read(_fd, return_size)
            os.close(_fd)
            return _buf
    _cmdPROC_FS=staticmethod(_cmdPROC_FS)

    def getList(self):
        """
        Borrowed from gfs_tools/utils.c
        """
        _list=GFS._cmdPROC_FS(self.LIST_CMD, self.LIST_SIZE)
        for _listline in _list.splitlines():
            _re=GFS.LIST_MATCH.match(_listline)
            (_cookie, _device, _cluster, _locktable, _journal)=_re.groups()
            if GFS.compareDevices(os.path.join(GFS.DEV_PATH, _device), self.device):
                self.cookie=_cookie
                self.cluster=_cluster
                self.locktable=_locktable
                self.journal=_journal

        return _list

    def counters(self):
        #buf=array.array("c")
        #buf.fromstring(struct.pack("I", 1))
        #buf.fromstring("get_counter")
        #buf.fromstring(4096*" ")
        #buf.fromstring(struct.pack("I", 4096))
        # FIXME: As ioctls don't work jet we'll do it with gfs_tool directly should be ported back sometime
        #        But Mr. Hl. said pragamtic!!
        #buf=struct.pack("I12s513sI", 1, "get_counters", 512*" ", 512)
        #self.logger.debug("size of buf: %u" %len(buf))
        #fd=os.open(self.mountpoint, os.O_RDONLY)
        #if fcntl.ioctl(fd, GFS.GFS_SUPER_IOCTL, buf) != 0:
        #    self.logger.error("Could not get counters on filesystem %s" %self.mountpoint)
        #    return -1
        #os.close(fd)
        #return buf
        (_rc,_output)=ComSystem.execLocalGetResult("%s %s %s" %(GFS.GFS_TOOL, GFS.COUNTERS_CMD, self.mountpoint))
        _counters=dict()
        if _rc != 0:
            return _counters
        for _line in _output:
            _line=_line.strip()
            if not _line or _line=="":
                continue
            _re=GFS.COUNTERS_MATCH_NUMBER.match(_line)
            if _re:
                _counters[_re.group("key")]=int(_re.group("value"))
            else:
                _re=GFS.COUNTERS_MATCH_PERCENTAGE.match(_line)
                if _re:
                    _counters[_re.group("key")]=float(_re.group("value"))
                else:
                    self.logger.debug("Could not match line \"%s\"" %_line)
        return _counters

    def countersValues(self):
        _counters=self.counters()
        (_rc,_output)=ComSystem.execLocalGetResult("date +\"%F-%H-%M-%S\"")
        _time=_output
        _output=_output[0].splitlines()[0]

        buf=_output+","
        for _value in _counters.values():
            buf+=str(_value)+","
        return buf[:-1]

    def countersFormat(self):
        _counters=self.counters()
        self.counterswriter.write(_counters)
        return ""

    def lockdump(self, size=LOCKDUMP_SIZE):
        return self._cmdPROC_FS(GFS.LOCKDUMP_CMD %(self.cookie), GFS.LOCKDUMP_SIZE)

    def lockdumpFormat(self, size=LOCKDUMP_SIZE):
        if self.cookie:
            _fd=GFS._cmdPROC_FS(GFS.LOCKDUMP_CMD %(self.cookie), size, True)
        elif self.filename:
            _fd=os.open(self.filename, os.O_RDONLY)
            if size == GFS.LOCKDUMP_SIZE:
                size=1024
        else:
            _fd=sys.stdin.fileno()
            if size == GFS.LOCKDUMP_SIZE:
                size=1024
        _glock=None
        _actdict=None
        _dump=""
        _lines=os.read(_fd, size)
        try:
            self.locks=0
            while _lines:
                _buf=""
                for _line in _lines.splitlines(True):
                    if not _line.endswith("\n"):
                        _buf=_line
                        GFS.logger.debug("Saving buffer: \"%s\"" %_buf)
                    else:
                        _line=_line.strip()
                        #_line=_line[:-1]
                        if not _line or _line=="":
                            continue
                        GFS.logger.debug("Read line: %s" %_line)
                        _matched=False
                        _re=GFS.GLOCK_MATCH.match(_line)
                        if _re:
                            _matched=True
                            if _glock:
                                self.locks+=1
                                self.glockwriter.write(_glock)
                            _glock=GLock()
                            for _name, _value in _re.groupdict().items():
                                setattr(_glock, _name, _value)
                            _glock.__name__="Glock"
                            _glock.__info__=",".join(_re.groupdict().values())
                            _actdict=_glock

                        _re=GFS.GLOCK_KEYVALUE_MATCH.match(_line)
                        if not _matched and _re:
                            _matched=True
                            if _re.group("key")=="owner" and int(_re.group("value")) > 0:
                                if not self.pids.has_key(_glock.glockid):
                                    self.pids[_glock.glockid]=list()
                                self.pids[_glock.glockid].append(_re.group("value"))
                            if isinstance(_actdict, GLock) or isinstance(_actdict, Holder):
                                setattr(_actdict, _re.group("key").strip(), _re.group("value").strip())
                            else:
                                _actdict[_re.group("key").strip()]=_re.group("value").strip()

                        _re=GFS.GLOCK_SUBTREE_MATCH.match(_line)
                        if not _matched and _re:
                            _matched=True
                            if _re.group("key").strip()=="Holder":
                                _subtree=Holder()
                            else:
                                _subtree=Waiter()
                            if not hasattr(_glock, _re.group("key").strip()):
                                setattr(_glock, _re.group("key").strip(), list())
                            getattr(_glock, _re.group("key").strip()).append(_subtree)
                            setattr(_subtree, "__name__", _re.group("key").strip())
                            _actdict=_subtree
                        _re=GFS.GLOCK_SUBTREE_MATCH_ONELINE.match(_line)
                        if not _matched and _re:
                            _matched=True
                            _subtree=dict()
                            if not hasattr(_glock, _re.group("key").strip()):
                                setattr(_glock, _re.group("key").strip(), list())
                            getattr(_glock, _re.group("key").strip()).append(_subtree)
                            _subtree["__name__"]=_re.group("key").strip()
                            _subtree[_re.group("value")]=_re.group("value").strip()
                            _actdict=_subtree
                        if not _matched:
                            print("Could not match line: %s" %(_line))

                _lines=_buf
                _lines+=os.read(_fd, size)
        except OSError:
            pass

        os.close(_fd)
        # Last one
        if _glock:
            self.locks+=1
            self.glockwriter.write(_glock)

        self.glockwriter.writePids(self.pids)
        self.glockwriter.writeLocks(self.locks)
        return ""

def main():
   import sys
   logging.basicConfig()
   #logging.getLogger().setLevel(logging.INFO)
   #GFS.logger.setLevel(logging.DEBUG)
   ComSystem.__EXEC_REALLY_DO=None
   _gfs=GFS(sys.argv[2])
   _gfs.glockwriter=GraphvizGLockWriter()

   getattr(_gfs, sys.argv[1])()

if __name__ == "__main__":
    main()