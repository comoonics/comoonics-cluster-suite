#!/usr/bin/python
"""analysis.ComGlockParser

analysis objects for the glock writers

"""

# here is some internal information
# $Id $
#

import logging
import sys
import re
import shlex

from ComParser import Parser
from ComObjects import GLock, Holder, Waiter, Inode
__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/analysis/ComGLockParser.py,v $

class GLockParser(Parser):
    """
    GFS Class as base class for parsing glockdumps
    """

    logger=logging.getLogger("comoonics.analysis.ComGLockParser")
    GLOCK_TOKEN="Glock"
    HOLDER_TOKEN="Holder"
    WAITER_TOKEN=re.compile("Waiter(?P<num>\d+)")
    INODE_TOKEN="Inode"
    INODEBUSY_TOKEN="busy"
    ATTRIBS_EQUALS=[ "=" ]
    def __init__(self, instream=None, infile=None):
        Parser.__init__(self, instream, infile, False)
        self.locks=[]

    def items(self):
        _token=self.get_token()
        _obj=None
        while _token != "":
            if _token == self.GLOCK_TOKEN:
                _lock=GLock()
                _obj=_lock
                self.locks.append(_lock)
                # drop next token (
                self.get_token()
                # next is glocktype
                _lock.glock=self.get_token()
                # then , drop
                self.get_token()
                _lock.glockid=self.get_token()
                self.parseObjAttribs(_lock)
            elif _token == self.HOLDER_TOKEN:
                _obj=Holder()
                _lock.addChild(_obj)
                self.parseObjAttribs(_obj)
            elif self.WAITER_TOKEN.match(_token):
                _obj=Waiter()
                _lock.addChild(_obj)
                _obj.level=self.WAITER_TOKEN.match(_token).group("num")
                self.parseObjAttribs(_obj)
            elif _token == self.INODE_TOKEN:
                # skip :
                self.get_token()
                _obj=Inode()
                _lock.addChild(_obj)
                # if next is busy then set to busy and skip
                _token=self.get_token()
                if _token == self.INODEBUSY_TOKEN:
                    _obj.busy=True
                else:
                    self.push_token(_token)
                self.parseObjAttribs(_obj)
            _token=self.get_token()
        return self.locks

    def parseObjAttribs(self, _obj):
        while True:
            _key=self.get_token()
            _skip=self.get_token()
            _oldws=self.whitespace
            _oldwc=self.wordchars
            # blanks are no whitespaces at this point
            self.whitespace=self.whitespace.replace(" ", "")
            self.wordchars+=" "
            _value=self.get_token()
            self.wordchars=_oldwc
            self.whitespace=_oldws
            if _skip in self.ATTRIBS_EQUALS:
                setattr(_obj, _key.strip(), _value.strip())
            else:
                self.push_token(_key)
                self.push_token(_skip)
                self.push_token(_value)
                break
        

######################
# $Log: ComGLockParser.py,v $
# Revision 1.1  2009-09-28 15:27:11  marc
# *** empty log message ***
#