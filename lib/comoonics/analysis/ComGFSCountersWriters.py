"""
analysis.ComGFSCountersWriters

analysis objects for the gfscounter writers

"""

# here is some internal information
# $Id $
#

import logging
import sys
from ComWriters import DictWriter

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComGFSCountersWriters.py,v $

# The registry
_countersWriterRegistry=dict()
def getCountersWriterRegistry():
    return _countersWriterRegistry

def addCountersWriter(_writer):
    if isinstance(_writer, DictWriter) and _writer.isSupported():
        getCountersWriterRegistry()[_writer.NAME]=_writer

def getCountersWriter(_name=None):
    if not _name:
        _name="__default__"
    if getCountersWriterRegistry().has_key(_name):
        return getCountersWriterRegistry()[_name]
    else:
        return None

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
    
    def isSupported(self):
        return True

addCountersWriter(DefaultCountersWriter())

class CountersValueWriter(DefaultCountersWriter):
    NAME="values"
    def __init__(self, _out=sys.stdout):
        DefaultCountersWriter.__init__(self, _out)
        self.print_only_value=False
        self.writehead=False
        self.only_values=True
    
    def isSupported(self):
        return True
addCountersWriter(CountersValueWriter())

#############################
# $Log: ComGFSCountersWriters.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#