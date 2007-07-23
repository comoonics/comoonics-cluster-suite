#!/usr/bin/python
"""Comoonics GFS module

provides analysis functions and the like for gfs

"""

# here is some internal information
# $Id $
#


__version__ = "$Revision: 1.2 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/ComGFS.py,v $

import os
import os.path
import re
import sys
import logging
import fcntl
import struct
import array
from exceptions import OSError, IndexError

from comoonics import ComSystem


class GFSError(OSError):
    def __init__(self, msg):
        self.value=msg
    def __str__(self):
        return "%s: %s" %(self.value, os.strerror(os.error))

class DictWriter(object):
    logger=logging.getLogger("comoonics.ComGFS.DictWriter")
    NAME=None
    def __init__(self, _out=sys.stdout):
        self.out=_out
        self.print_only_value=True
        self.prefix=None
        self.prefix_delim="."
        self.writehead=True
        self.writetail=False
        self.only_values=False
        self.filteredKeys=None

    def write(self, _dict, _tabs=0, _head=True, _tail=True, _actkey=None):
        if self.writehead and _head:
            self.writeHead(_dict, _tabs)
        else:
            _tabs=_tabs-1
        _keys=None
        if self.filteredKeys:
            if not _actkey:
                _actkey="default"
            if self.filteredKeys.has_key(_actkey):
                self.logger.debug("Setting filteredKeys %s" %_actkey)
                _keys=self.filteredKeys[_actkey]
        if not _keys:
            _keys=_dict.keys()
            _keys.sort()
        for key in _keys:
            if not _dict.has_key(key):
                self.filterDictValue(key)
                continue
            value=_dict[key]
            if key.startswith("__") and key.endswith("__"):
                continue
            if isinstance(value, basestring) or type(value)==int or type(value)==float or type(value)==long:
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeKeyValue(key, value, _tabs+1)
            elif type(value)==dict:
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeDictValue(key, value, _tabs+1)
            elif type(value)==list or type(value)==tuple:
                if not self.only_values:
                    self._write(self.formatPrefix(_dict))
                self.writeTupleValue(key, value, _tabs+1)
        if self.writetail and _tail:
            self.writeTail(_dict, _tabs)

    def formatPrefix(self, _dict):
        buf=""
        if self.prefix:
            buf="%s%s" %(self.getPrefix(_dict), self.prefix_delim)
        return buf

    # Methods to be overwritten defaults to just output

    def filterDictValue(self, key):
        pass

    def getPrefix(self, _dict):
        if _dict.has_key(self.prefix):
            return _dict[self.prefix]
        else:
            return self.prefix

    def writeHead(self, _dict, _tabs=0):
        if type(_dict)==dict and not self.only_values:
            if _dict.has_key("__name__") and _dict.has_key("__info__"):
                self._write("%s(%s)\n" %(_dict["__name__"], _dict["__info__"]), _tabs)
            elif _dict.has_key("__name__"):
                self._write("%s\n" %(_dict["__name__"]), _tabs)

    def writeKeyValue(self, _key, _value, _tabs=0):
        if not self.only_values and (not self.print_only_value or _value):
            self._write("%s = %s\n" %(_key, str(_value)), _tabs)
        elif self.only_values:
            self._write("%s\n" %(str(_value)))

    def writeDictValue(self, _key, _dict, _tabs=0):
        #self._write("dict<%s>\n" %_key, _tabs)
        self.write(_dict, _tabs)

    def writeTupleValue(self, _key, _tuple, _tabs=0):
        self.writeKeyValue(_key, ",".join(_tuple), _tabs)

    def writeTail(self, _dict, _tabs=0):
        pass

    def _write(self, _str, _tabs=0):
        self.out.write("\t"*_tabs+_str.expandtabs())

_countersWriterRegistry=dict()
def getCountersWriterRegistry():
    return _countersWriterRegistry

def addCountersWriter(_writer):
    if isinstance(_writer, DictWriter):
        getCountersWriterRegistry()[_writer.NAME]=_writer

def getCountersWriter(_name=None):
    if not _name:
        _name="__default__"
    if getCountersWriterRegistry().has_key(_name):
        return getCountersWriterRegistry()[_name]
    else:
        return None

_lockdumpWriterRegistry=dict()
def getLockdumpWriterRegistry():
    return _lockdumpWriterRegistry

def addLockdumpWriter(_writer):
    if isinstance(_writer, DictWriter):
        getLockdumpWriterRegistry()[_writer.NAME]=_writer

def getLockdumpWriter(_name=None):
    if not _name:
        _name="__default__"
    if getLockdumpWriterRegistry().has_key(_name):
        return getLockdumpWriterRegistry()[_name]
    else:
        return None

class GLockWriter(DictWriter):
    def __init__(self, _out=sys.stdout):
        DictWriter.__init__(self, _out)

    def write(self, _dict, _tabs=0, _head=True, _tail=True, _actKey=None):
        self.decipherGlock(_dict)
        DictWriter.write(self, _dict, _tabs, _head, _tail, _actKey)

    def writePids(self, pids):
        pass

    def writeLocks(self, locks):
        pass

    def decipherGlock(self, _glock):
        return 1

class DefaultCountersWriter(DictWriter):
    NAME="__default__"
    logger=logging.getLogger("comoonics.ComGFS.DefaultCountersWriter")
    FILTERED_COLS={ "default": ["locks",
                       "locks held",
                       "incore inodes",
                       "metadata buffers",
                       "unlinked inodes",
                       "quota IDs",
                       "incore log buffers",
                       "log space used",
                       "meta header cache entries",
                       "glock dependencies",
                       "glocks on reclaim list",
                       "log wraps",
                       "outstanding LM calls",
                       "outstanding BIO calls",
                       "fh2dentry misses",
                       "glocks reclaimed",
                       "glock nq calls",
                       "glock dq calls",
                       "glock prefetch calls",
                       "lm_lock calls",
                       "lm_unlock calls",
                       "lm callbacks"
                       "address operations",
                       "dentry operations",
                       "export operations",
                       "file operations",
                       "inode operations",
                       "super operations",
                       "vm operations",
                       "block I/O reads",
                       "block I/O writes"]}

    def __init__(self, _out=sys.stdout):
        DictWriter.__init__(self, _out)
        self.print_only_value=False
        self.writehead=False
        self.filteredKeys=self.FILTERED_COLS
addCountersWriter(DefaultCountersWriter())

class CountersValueWriter(DefaultCountersWriter):
    NAME="values"
    def __init__(self, _out=sys.stdout):
        DefaultCountersWriter.__init__(self, _out)
        self.print_only_value=False
        self.writehead=False
        self.only_values=True
addCountersWriter(CountersValueWriter())

class DefaultGLockWriter(GLockWriter):
    NAME="__default__"
    logger=logging.getLogger("comoonics.ComGFS.DefaultGLockWriter")

    def __init__(self, _out=sys.stdout):
        GLockWriter.__init__(self, _out)
        self.print_only_value=True

    # Methods to be overwritten defaults to just output

    def writePids(self, _pids):
        _keys=_pids.keys()
        _keys.sort()
        self._write("Pids:\nlock: pids\n")
        for _key in _keys:
            self._write("%s: %s\n" %(_key, ",".join(_pids[_key])))

    def writeLocks(self, _locks):
        self._write("Locks: %u\n" %_locks)

    def decipherGlock(self, _glock):
        if _glock.has_key("glock"):
            _type=int(_glock["glock"])
            _glock["glocktype"]=GFS.GLOCKTYPES[_type]
            if _type==1:
                # nondisk
                _glock["nondisk"]=int(_glock["glockid"])
                _glock["nondisk_type"]=self._maparray(_glock, "nondisk", GFS.GLOCK_NONDISK_TYPES)
                del _glock["glockid"]
            elif _type==4:
                # meta
                _glock["metadata"]=int(_glock["glockid"])
                _glock["metadata_type"]=self._maparray(_glock, "metadata", GFS.GLOCK_METADATA_TYPES)
                del _glock["glockid"]
            elif _type==8:
                # meta
                _glock["quota"]=int(_glock["glockid"])%2
                _glock["quota_type"]=self._maparray(_glock, "quota", GFS.GLOCK_QUOTA_TYPES)
                del _glock["glockid"]

        if _glock.has_key("gl_flags"):
            _glock["gl_flags_name"]=self._maparray(_glock, "gl_flags", GFS.GLOCK_GLFLAGS)
        if _glock.has_key("gh_state"):
            _glock["gh_state_name"]=self._maparray(_glock, "gh_state", GFS.GLOCK_STATE)
        if _glock.has_key("gh_flags"):
            _glock["gh_flags_name"]=self._maparray(_glock, "gh_flags", GFS.GLOCK_GHFLAGS)
        if _glock.has_key("gh_iflags"):
            _glock["gh_iflags_name"]=self._maparray(_glock, "gh_iflags", GFS.GLOCK_GHIFLAGS)
        if _glock.has_key("type"):
            _glock["type_name"]=self._maparray(_glock, "type", GFS.GLOCK_TYPE)
        if _glock.has_key("iflags"):
            _glock["iflags"]=self._maparray(_glock, "iflags", GFS.GLOCK_IFLAGS)

    def _maparray(self, _dict, _key, _array):
        try:
            _str=_dict[_key]
            _ret=None
            if isinstance(_str, basestring) and len(_str.split(" "))>1:
                _ret=list()
                for _id in _str.split(" "):
                    _ret.append(_array[int(_id)])
            else:
                _ret=_array[int(_dict[_key])]
            return _ret
        except IndexError:
            self.logger.warn("Unkown %s type %s" %(_key, _dict[_key]))
        except ValueError:
            self.logger.debug("Cannot convert \"%s\" to int" %(_dict[_key]))
addLockdumpWriter(DefaultGLockWriter())

class CSVGlockWriter(GLockWriter):
    NAME="csv"

    VALID_COLS={ "default": ["glockid", "glock", "ail_bufs", "aspace", "gl_count", "gl_state", "gl_flags",
                             "incore_le", "lvb_count", "new_le", "object", "reclaim", "req_bh", "req_gh",
                             "Inode", "Holder"],
                 "Inode": ["i_count", "num", "type", "vnode", "i_flags" ],
                 "Holder": ["error", "gh_flags", "gh_iflags", "gh_state", "owner", ],
                 "Request": ["error", "gh_flags", "gh_iflags", "gh_state", "owner", ],
                 "Waiter1": ["error", "gh_flags", "gh_iflags", "gh_state", "owner", ],
                 "Waiter2": ["error", "gh_flags", "gh_iflags", "gh_state", "owner", ],
                 "Waiter3": ["error", "gh_flags", "gh_iflags", "gh_state", "owner", ]
                 }

    VALID_COLNAMES= [ "glockid", "glock", "ail_bufs", "aspace", "gl_count", "gl_flags", "gl_state", "incore_le",
                     "lvb_count", "new_le", "object", "reclaim", "req_bh", "req_gh",
                      "Inode.i_count", "Inode.num", "Inode.type", "Inode.vnode", "Inode.i_flags",
                      "Request.error", "Request.gh_flags", "Request.gh_iflags", "Request.gh_state", "Request.owner",
                      "Holder.error", "Holder.gh_flags", "Holder.gh_iflags", "Holder.gh_state", "Holder.owner",
                      "Waiter1.error", "Waiter1.gh_flags", "Waiter1.gh_iflags", "Waiter1.gh_state", "Waiter1.owner",
                      "Waiter2.error", "Waiter2.gh_flags", "Waiter2.gh_iflags", "Waiter2.gh_state", "Waiter2.owner",
                      "Waiter3.error", "Waiter3.gh_flags", "Waiter3.gh_iflags", "Waiter3.gh_state", "Waiter3.owner",
                       ]

    def __init__(self, _out=sys.stdout, _delimiter=";", _dictdelimiter="\n", _head=True):
        GLockWriter.__init__(self, _out)
        self.writehead=_head
        self.delimiter=_delimiter
        self.dictdelimiter=_dictdelimiter
        self.writetail=True
        self._firstLine=False
        self.filteredKeys=self.VALID_COLS

    def writeHead(self, _dict, _tabs=0):
        _buf=""
        if self.writehead and not self._firstLine:
            _buf=self.delimiter.join(self.VALID_COLNAMES)
            _buf+=self.dictdelimiter
            self._write(_buf)
            self._firstLine=True
        return _buf

    def filterDictValue(self, key):
        if self.filteredKeys.has_key(key):
            self._write(self.delimiter * len(self.filteredKeys[key]))
        else:
            self._write(self.delimiter)

    def writeTail(self, _dict, _tabs=0):
        self._write(self.dictdelimiter)

    def writeKeyValue(self, _key, _value, _tabs=0):
        self._write(_value+self.delimiter, 0)

    def writeDictValue(self, _key, _dict, _tabs=0):
        #self._write("dict<%s>\n" %_key, _tabs)
        self.logger.debug("writeDictValue %s, %s, %s" %(_key, _dict, self.filteredKeys))
        if self.filteredKeys.has_key(_key):
            self.write(_dict, _tabs, False, False, _key)

    def writeTupleValue(self, _key, _tuple, _tabs=0):
        self.writeKeyValue(_key, " ".join(_tuple), _tabs)
addLockdumpWriter(CSVGlockWriter())

class SQLGlockWriter(CSVGlockWriter):
    CREATE_TABLES_STATEMENT="""
    CREATE TABLE IF NOT EXISTS Glocks%s (
       glockid int(64) NOT NULL,
       glock int(8) NOT NULL,
       ail_bufs ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       aspace int(64) DEFAULT NULL,
       gl_count int(64),
       gl_state int(8) NOT NULL,
       gl_flags int(64)
       lvb_count int(64),
       incore_le  ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       new_le ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       object ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       reclaim ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       req_bh ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       req_gh ENUM ('yes', 'no') NOT NULL DEFAULT "no")
    ) TYPE=InnoDB COMMENT="Table to hold all locks.";
    CREATE TABLE IF NOT EXISTS Holders (
       type ENUM ("Request", "Holder", "Waiters1", "Waiters2", "Waiters3"),
       glockid int(64) NOT NULL,
       owner int(64) NOT NULL,
       gh_state int(64),
       gh_flags int(64),
       gh_iflags int(64),
       error int(64),
    ) TYPE=InnoDB COMMENT="Table holding all holders, waiters and requests";
    """

    def __init__(self, _glocks_table="Glocks", _holders_table="Holders", _inodes_table="Inodes", _out=sys.stdout):
        CSVGlockWriter.__init__(self, _out)
addLockdumpWriter(SQLGlockWriter)

class GFS(object):
    """
    GFS Class as base class for any GFS Filesystem
    """

    logger=logging.getLogger("comoonics.ComGFS.GFS")

    GLOCKTYPES= [ "reserved", "nondisk", "inode", "rgrp", "meta", "iopen", "flock", "jid", "quota" ]

    GLOCK_NONDISK_TYPES = [ "mount", "live", "trans", "rename" ]
    GLOCK_METADATA_TYPES = [ "super", "crap" ]
    GLOCK_QUOTA_TYPES = [ "user", "group" ]
    GLOCK_GLFLAGS = ["plug", "lock", "sticky", "prefetch", "sync", "dirty", "skip_waiters", "greedy" ]
    GLOCK_STATE = [ "unlocked", "exclusive", "deferred", "shared" ]
    GLOCK_GHFLAGS = [ "try", "try_1cb", "noexp", "any", "priority", "local_excl", "async", "exact", "skip", "atime", "nocache", "sync", "nocancel" ]
    GLOCK_GHIFLAGS= [ "mutex", "promote", "demote", "greedy", "allocated", "dealloc", "holder", "first", "recurse", "aborted" ]
    GLOCK_TYPE = [ "none", "regular", "directory", "symbolic link", "block device", "char device", "fifo", "socket" ]
    GLOCK_IFLAGS = [ "qd_locked", "paged", "sw_paged" ]

    DEV_PATH="/dev"

    PROC_FS="/proc/fs/gfs"
    PROC_MOUNTS="/proc/mounts"

    LIST_CMD="list"
    LIST_SIZE=1048576
    LIST_MATCH=re.compile("(\S+)\s(\S+)\s(\S+):(\S+)\.(\S+)", re.I)

    LOCKDUMP_CMD="lockdump %s"
    LOCKDUMP_SIZE=4194304

    GFS_TYPE="gfs"

    GLOCK_MATCH=re.compile(r"Glock \((?P<glock>\d+), (?P<glockid>\d+)\)")
    GLOCK_KEYVALUE_MATCH=re.compile(r"^\s*(?P<key>\S+)\s+=\s*(?P<value>.*)$")
    GLOCK_SUBTREE_MATCH =re.compile(r"^\s*(?P<key>\w+)\W*$")

    GFS_SUPER_IOCTL=18221

    GFS_TOOL="/sbin/gfs_tool"
    COUNTERS_CMD="counters"
    COUNTERS_MATCH_NUMBER=re.compile("^\s*(?P<key>.+)\s(?P<value>\d+)$")
    COUNTERS_MATCH_PERCENTAGE=re.compile("^\s*(?P<key>.+)\s(?P<value>[0-9.]+)%$")

    def __init__(self, *_params, **_keys):
        self.glockwriter=getLockdumpWriter()
        self.counterswriter=getCountersWriter()
        self.pids=dict()
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

        if len(_params)>0:
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
        if not hasattr(self, "filename") or not self.filename:
            _fd=GFS._cmdPROC_FS(GFS.LOCKDUMP_CMD %(self.cookie), size, True)
        else:
            _fd=os.open(self.filename, os.O_RDONLY)
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
                            _glock=_re.groupdict()
                            _glock["__name__"]="Glock"
                            _glock["__info__"]=",".join(_re.groupdict().values())
                            _actdict=_glock

                        _re=GFS.GLOCK_KEYVALUE_MATCH.match(_line)
                        if not _matched and _re:
                            _matched=True
                            if _re.group("key")=="owner" and int(_re.group("value")) > 0:
                                if not self.pids.has_key(_glock['glockid']):
                                    self.pids[_glock['glockid']]=list()
                                self.pids[_glock['glockid']].append(_re.group("value"))
                            _actdict[_re.group("key").strip()]=_re.group("value").strip()

                        _re=GFS.GLOCK_SUBTREE_MATCH.match(_line)
                        if not _matched and _re:
                            _matched=True
                            _subtree=dict()
                            _glock[_re.group("key").strip()]=_subtree
                            _subtree["__name__"]=_re.group("key").strip()
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

   print getattr(_gfs, sys.argv[1])()

if __name__ == "__main__":
    main()