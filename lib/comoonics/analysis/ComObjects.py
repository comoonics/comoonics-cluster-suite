#!/usr/bin/python
"""Comoonics Objects

analysis objects for the parsers and writers

"""

# here is some internal information
# $Id $
#

import logging

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComObjects.py,v $

class BaseObject(object):
    _delimiter="\n"
    _equals="="
    def __init__(self):
        super(BaseObject, self).__init__()
        self.__deciphered=False
        self._children=list()
    def isDiciphered(self):
        return self.__deciphered
    def decipher(self):
        if not self.isDiciphered():
            self.__deciphered=True
            self._decipher()
    def _decipher(self):
        pass
    def __str__(self, _tabs=""):
        import StringIO
        self.decipher()
        _buf=StringIO.StringIO()
        _buf.write(_tabs)
        _buf.write(self.__class__.__name__)
        _buf.write(self._delimiter)
        for _name, _value in self.__dict__.items():
            if _name[0]!= "_" and _value != None:
                _buf.write("   %s" %_tabs)
                _buf.write("%s%s%s" %(_name, self._equals, _value))
                _buf.write(self._delimiter)
        for _child in self.children():
            _buf.write(_child.__str__("   "))
#            _buf.write(self._delimiter)
        return _buf.getvalue()
    def addChild(self, _child):
        self._children.append(_child)
    def children(self):
        return self._children

class GLock(BaseObject):
    """
    Class representing a glock
    """
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
    
    logger=logging.getLogger("comoonics.ComGFS.GLock")

    def __init__(self):
        super(GLock, self).__init__()
        self.glockid=None
        self.glocktype=None
        self.glock=None
    
    def _decipher(self):
        if self.glock != None:
            _type=int(self.glock)
            self.glocktype=self.GLOCKTYPES[_type]
            if _type==1:
                # nondisk
                self.nondisk=int(self.glockid)
                self.nondisk_type=self._maparray(self, "nondisk", self.GLOCK_NONDISK_TYPES)
#                del self["glockid"]
            elif _type==4:
                # meta
                self.metadata=int(self.glockid)
                self.metadata_type=self._maparray("metadata", self.GLOCK_METADATA_TYPES)
#                del self["glockid"]
            elif _type==8:
                # meta
                self.quota=int(self.glockid)%2
                self.quota_type=self._maparray("quota", self.GLOCK_QUOTA_TYPES)
#                del self["glockid"]
#        self.__name__=self.getName()

        if hasattr(self, "gl_flags"):
            self.gl_flags_name=self._maparray("gl_flags", self.GLOCK_GLFLAGS)
        if hasattr(self, "gh_state"):
            self.gh_state_name=self._maparray("gh_state", self.GLOCK_STATE)
        if hasattr(self, "gh_flags"):
            self.gh_flags_name=self._maparray("gh_flags", self.GLOCK_GHFLAGS)
        if hasattr(self, "gh_iflags"):
            self.gh_iflags_name=self._maparray("gh_iflags", self.GLOCK_GHIFLAGS)
        if hasattr(self, "type"):
            self.type_name=self._maparray("type", self.GLOCK_TYPE)
        if hasattr(self, "iflags"):
            self.iflags=self._maparray("iflags", self.GLOCK_IFLAGS)

    def _maparray(self, _key, _array):
        try:
            _str=getattr(self, _key)
            _ret=None
            if isinstance(_str, basestring) and len(_str.split(" "))>1:
                _ret=list()
                for _id in _str.split(" "):
                    _ret.append(_array[int(_id)])
            else:
                _ret=_array[int(_str)]
            return _ret
        except IndexError:
            self.logger.warn("Unkown %s type %s" %(_key, _str))
        except ValueError:
            self.logger.debug("Cannot convert \"%s\" to int" %(_str))
    
    def getName(self):
        _name=""
        if hasattr(self, "glocktype"):
            _name="%s[%s]" %(self.glocktype, self.glock)
        else:
            _name="%s" %self.glock
        
        _name+=" %s" %self.glockid
        return _name

class Holder(GLock):
    """
    Class representing an holder of a lock
    """
    def __init__(self):
        super(Holder, self).__init__()
        self.owner="-1"
        self.nodeid="-1"
        self.gh_state="-1"
    def getName(self):
        self.decipher()
        return "%s.%s" %(self.nodeid, self.owner)
    def getConnectionName(self):
        self.decipher()
        return "%s<%s>" %(getattr(self, "gh_state_name", "unknown"), self.gh_state)
class Waiter(Holder):
    """
    Class representing a waiter on a lock
    """
    def __init__(self):
        super(Waiter, self).__init__()
        self.level="3"

class Inode(GLock):
    """
    Class representing an inode
    """
    pass
############################
# $Log: ComObjects.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#