"""analysis.ComGlockWriters

analysis objects for the glock writers

"""

# here is some internal information
# $Id $
#

import logging
import sys

from ComObjects import BaseObject
from ComWriters import DictWriter

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComGLockWriters.py,v $

# The registry
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
        if isinstance(_dict, BaseObject):
            _dict.decipher()
        DictWriter.write(self, _dict, _tabs, _head, _tail, _actKey)

class DefaultGLockWriter(GLockWriter):
    NAME="__default__"
    logger=logging.getLogger("comoonics.ComGFS.DefaultGLockWriter")

    def __init__(self, _out=sys.stdout):
        GLockWriter.__init__(self, _out)
        self.print_only_value=True

    def isSupported(self):
        return True

addLockdumpWriter(DefaultGLockWriter())

class CSVGlockWriter(GLockWriter):
    NAME="csv"

    VALID_COLS={ "default": ["glockid", "glock", "ail_bufs", "aspace", "gl_count", "gl_state", "gl_flags",
                             "incore_le", "lvb_count", "new_le", "object", "reclaim", "req_bh", "req_gh",
                             "Inode", "Holder"],
                 "Glock": ["glockid", "glock", "ail_bufs", "aspace", "gl_count", "gl_state", "gl_flags",
                             "incore_le", "lvb_count", "new_le", "object", "reclaim", "req_bh", "req_gh"],
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
        self.filteredKeys=self.VALID_COLS
        self.writebegin=True

    def writeBegin(self):
        if self.writebegin:
            _buf=self.delimiter.join(self.VALID_COLNAMES)
            _buf+=self.dictdelimiter
            self._write(_buf)

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
    
    def isSupported(self):
        return True
#addLockdumpWriter(CSVGlockWriter())

class SQLGlockWriter(CSVGlockWriter):
    NAME="sql"
    TABLES={ "Glock": "Glocks%s",
             "default": "Glocks%s",
             "Inode": "Inodes%s",
             "Holder": "Holders%s",
             "Request": "Holders%s",
             "Waiter1": "Holders%s",
             "Waiter2": "Holders%s",
             "Waiter3": "Holders%s" }
    BITLISTS=["gh_flags", "gh_iflags", "i_flags", "gl_flags"]
    CREATE_TABLES_STATEMENT="""
    CREATE TABLE IF NOT EXISTS %s (
       glockid int(64) NOT NULL,
       glock int(8) NOT NULL,
       ail_bufs ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       aspace int(64) DEFAULT NULL,
       gl_count int(64),
       gl_state int(8) NOT NULL,
       gl_flags int(64),
       lvb_count int(64),
       incore_le  ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       new_le ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       object ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       reclaim ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       req_bh ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       req_gh ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       PRIMARY KEY (glockid)
    ) TYPE=InnoDB COMMENT="Table to hold all locks.";
    CREATE TABLE IF NOT EXISTS %s (
       glockid int(64) NOT NULL,
       type ENUM ("Request", "Holder", "Waiters1", "Waiters2", "Waiters3"),
       owner int(64) NOT NULL,
       gh_state int(64),
       gh_flags int(64),
       gh_iflags int(64),
       error int(64),
       PRIMARY KEY (glockid, owner)
    ) TYPE=InnoDB COMMENT="Table holding all holders, waiters and requests";
    CREATE TABLE IF NOT EXISTS %s (
       glockid int(64) NOT NULL,
       i_count int(64) NOT NULL,
       num int(64) NOT NULL,
       type int(32) NOT NULL,
       vnode ENUM ('yes', 'no') NOT NULL DEFAULT "no",
       i_flags int(64),
       PRIMARY KEY (glockid)
    ) TYPE=InnoDB COMMENT="Table holding all inodes referenced by glocks";
    """

    def __init__(self, _glocks_table="Glocks", _name=None, _out=sys.stdout):
        CSVGlockWriter.__init__(self, _out)
        self.writehead=False
        self.writetail=True
        if not _name:
            _name="analysis"
        self._name=_name

    def decipherGlock(self, _glock):
#        self.logger.debug("decipherGlock %s" %_glock["__name__"])
        if hasattr(_glock, "glockid"):
            self._baseglockid=_glock.glockid
        for _bitlist in self.BITLISTS:
            if hasattr(_glock, "_bitlist") and _glock._bitlist != "":
                self.logger.debug("decipherGlock bitlist<%s>: %s" %(_bitlist, _glock._bitlist))
                _glock[_bitlist]=int(self._resolvebitlist(_glock._bitlist))
                self.logger.debug("decipherGlock bitlist<%s>: %u" %(_bitlist, _glock._bitlist))
        if hasattr(_glock, "num"):
            _glock.num=int(_glock.num.split("/")[0])

    def _resolvebitlist(self, _bitlist):
        _res=0
        for _bit in _bitlist.split(" "):
            _res|=1<<int(_bit)
        return _res


    def filterDictValue(self, key):
        pass

    def writeBegin(self):
        if self.writebegin:
            return self.CREATE_TABLES_STATEMENT %(self.TABLES["Glock"] %self._name, self.TABLES["Holder"] %self._name,
                                                  self.TABLES["Inode"] %self._name)

    def writeKeyValue(self, _key, _value, _tabs=0):
        pass

    def writeTupleValue(self, _key, _tuple, _tabs=0):
        pass

    def writeDictValue(self, _key, _dict, _tabs=0):
        self.decipherGlock(_dict)
        _tableskey=_key
        _values=list()
        if not self.VALID_COLS.has_key(_tableskey):
            return
        for _key in self.VALID_COLS[_tableskey]:
            _val=_dict[_key]
            _resval=None
            try:
                if type(_val) == int or int(_val):
                    _resval=str(_val)
            except ValueError:
                pass
            if isinstance(_val, basestring) and not _resval:
                _resval="\"%s\"" %(_val)
            _values.append(_resval)

        if _dict.has_key("__name__") and _dict["__name__"]=="Glock":
            _sqlquery="INSERT INTO %s (%s) VALUES (%s);\n" %(self.TABLES[_tableskey] %self._name, ",".join(self.VALID_COLS[_tableskey]),
                                                                          ",".join(_values))
        else:
            _sqlquery="INSERT INTO %s (glockid, %s) VALUES (%s, %s);\n" %(self.TABLES[_tableskey] %str(self._name), ",".join(self.VALID_COLS[_tableskey]),
                                                                          str(self._baseglockid), ",".join(_values))
        self._write(_sqlquery)

    def writeTail(self, _dict, _tabs=0):
        if isinstance(_dict, BaseObject):
            self.writeDictValue(_dict.__class__.__name__, _dict, _tabs)
        else:
            self.writeDictValue(_dict["__name__"], _dict, _tabs)
    
    def writeEnd(self):
        pass
    
    def isSupported(self):
        return True

#addLockdumpWriter(SQLGlockWriter())

#############################
# $Log: ComGLockWriters.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#