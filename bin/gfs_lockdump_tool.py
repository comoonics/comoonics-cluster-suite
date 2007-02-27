#!/usr/bin/python
"""Com.oonics gfs lockdump tool

Tool for gfs lockdump analysis

"""

# here is some internal information
# $Id: gfs_lockdump_tool.py,v 1.1 2007-02-27 15:39:55 mark Exp $
#

__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/bin/gfs_lockdump_tool.py,v $

from exceptions import Exception
import sys
import getopt
import logging
import warnings
import os
import re

sys.path.append("../lib")

from comoonics import ComSystem, ComLog, GetOpts

ComSystem.__EXEC_REALLY_DO=""

class Config(GetOpts.BaseConfig):
    def __init__(self):
        GetOpts.BaseConfig.__init__(self, sys.argv[0], "Checks if all nodes in this cluster are reachable until a given timeout occures.", __version__)
        self.debug=GetOpts.Option("debug", "toggle debugmode", False, False, "d", self.setDebug)
        self.verbose=GetOpts.Option("verbose", "toggle verbosemode", False, False, "V")

    def do(self, args_proper):
        if len(args_proper) > 0 and os.path.isfile(args_proper[0]):
            self.filename=args_proper[0]
        elif len(args_proper) == 0:
            print >>self.__stderr__, "No file given to execute."
            self.usage()
            return 1
        return 0

    def setDebug(self, value):
        ComLog.setLevel(logging.DEBUG)


''' parent class for locking information '''
class GFSLockObject:
    def __init__(self):
        self.entries=dict()
        pass

    def setValue(self, key, val):
        self.entries.update({key: val})

    def pprint(self):
        print self.entries

class GFSLock(GFSLockObject):
    ENTRIES= ["gl_flags", "gl_count", "gl_state", "req_gh", "req_bh", "lvb_count", "object = no",
              "new_le", "incore_le", "reclaim", "aspace", "ail_bufs"]
    HEADERNAME="Glock"
    HEADERFLAG=1

    def __init__(self, ln_type, ln_number):
        self.ln_type=ln_type
        self.ln_number=ln_number
        GFSLockObject.__init__(self)

    def pprint(self):
        print "ln_type: " + self.ln_type
        print "ln_number " + self.ln_number
        print self.entries

class GFSLockHolder(GFSLockObject):
    HEADERNAME="Holder"
    HEADERFLAG=2
    ENTRIES= ["owner","gh_state","gh_flags","error","gh_iflags"]

    def __init__(self):
        GFSLockObject.__init__(self)

class GFSLockWaiter(GFSLockObject):
    HEADERNAME0="Request"
    HEADERFLAG0=10
    HEADERNAME1="Waiter1"
    HEADERFLAG1=11
    HEADERNAME2="Waiter2"
    HEADERFLAG2=12
    HEADERNAME3="Waiter3"
    HEADERFLAG3=13
    ENTRIES= ["owner","gh_state","gh_flags","error","gh_iflags"]

    def __init__(self):
        GFSLockObject.__init__(self)

class GFSLockInode(GFSLockObject):
    ENTRIES= ["num", "type", "i_count", "i_flags", "vnode"]
    HEADERNAME="Inode"
    HEADERFLAG=6
    def __init__(self):
        GFSLockObject.__init__(self)

''' this class presents a raw GFS Lock Entry '''
class GFSLockEntryRaw:

    def __init__(self, ln_type, ln_number):
        self.lock=GFSLock(ln_type, ln_number)
        self.inode=None
        self.holder=None
        self.request=None
        self.waiter1=None
        self.waiter2=None
        self.Waiter3=None

        self.datalines=list()
        pass

    def addLine(self,line):
        self.datalines.append(line)

    def parseLines(self):
        ltype=GFSLock.HEADERFLAG
        print GFSLockInode.HEADERNAME
        print GFSLockHolder.HEADERNAME
        for line in self.datalines:
            # search for GFSLock.ENTRIES

            if re.search(GFSLockInode.HEADERNAME, line):
                #we have an inode entry here
                ltype=GFSLockInode.HEADERFLAG
                self.inode=GFSLockInode()
                continue

            if re.search(GFSLockHolder.HEADERNAME , line):
                #we have a Holder entry here
                ltype=GFSLockHolder.HEADERFLAG
                self.holder=GFSLockHolder()
                continue

            if re.search(GFSLockWaiter.HEADERNAME0 , line):
                #we have a Holder entry here
                ltype=GFSLockWaiter.HEADERFLAG0
                self.request=GFSLockWaiter()
                continue

            if re.search(GFSLockWaiter.HEADERNAME1, line):
                #we have a Waiter1 entry here
                ltype=GFSLockWaiter.HEADERFLAG1
                self.waiter1=GFSLockWaiter()
                continue

            if re.search(GFSLockWaiter.HEADERNAME2, line):
                #we have a Waiter2 entry here
                ltype=GFSLockWaiter.HEADERFLAG2
                self.waiter2=GFSLockWaiter()
                continue

            if re.search(GFSLockWaiter.HEADERNAME3, line):
                #we have a Waiter3 entry here
                ltype=GFSLockWaiter.HEADERFLAG3
                self.waiter3=GFSLockWaiter()
                continue


            if ltype == GFSLock.HEADERFLAG:
                for entry in GFSLock.ENTRIES:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.lock.setValue(entry, m.group(1))
                        continue

            if ltype == GFSLockInode.HEADERFLAG:
                for entry in GFSLockInode.ENTRIES:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.inode.setValue(entry, m.group(1))
                        continue

            if ltype == GFSLockHolder.HEADERFLAG:
                for entry in GFSLockHolder.ENTRIES:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.holder.setValue(entry, m.group(1))
                        continue

            if ltype == GFSLockWaiter.HEADERFLAG1:
                for entry in GFSLockWaiter.ENTRIES1:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.waiter1.setValue(entry, m.group(1))
                        continue

            if ltype == GFSLockWaiter.HEADERFLAG2:
                for entry in GFSLockWaiter.ENTRIES2:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.waiter2.setValue(entry, m.group(1))
                        continue

            if ltype == GFSLockWaiter.HEADERFLAG3:
                for entry in GFSLockWaiter.ENTRIES3:
                    m=re.search(entry + " = (.*)", line)
                    if m :
                        self.waiter3.setValue(entry, m.group(1))
                        continue

    def printData(self):
        print "Glock Entry:"
        self.lock.pprint()
        if self.holder:
            print("Holder:")
            self.holder.pprint()
        if self.inode:
            print("Inode:")
            self.inode.pprint()
        if self.waiter1:
            print("Waiter1")
            self.waiter1.pprint()
        if self.waiter2:
            print("Waiter2")
            self.waiter2.pprint()
        if self.Waiter3:
            print("Waiter3")
            self.waiter3.pprint()


class GFSLockEntryDeciphered:
    def __init__(self, lines):
        pass

''' this class presents a deciphered Multinode Lockentry'''
class GFSLockEntryMultinodeDeciphered:
    def __init__(self, lines):
        pass

class GFSLockCollection:
    def __init__(self):
        pass

    def setEntryCount(entries):
        self.entries=entries

    def printData(self):
        pass

class LockEntryParserMultinode:
    def __init__(self):
        pass

class LockEntryParser:
    def __init__(self):
        pass

    def parse(self, file):
        fobj=open(file)

        self.lockentries=dict()

        # Now parse the lock entries
        for line in fobj:
            #print line
            if re.match("^Glock \\(", line):
                #print "matches Glock"
                #we are at the start of a lockentry
                m=re.match("^Glock \\((\d+), (\d+)\\)", line)
                ln_type=m.group(1)
                ln_number=m.group(2)
                lockentry=GFSLockEntryRaw(ln_type, ln_number)
                self.lockentries.update({int(ln_number) : lockentry})
                continue
            lockentry.addLine(line)

        for entry in self.lockentries.values():
            entry.parseLines()


    def getLockentries(self):
        return self.lockentries

class cli:
    def __init__(self):
        pass

    def help(self):
        print "help - prints this help message"
        print "load <lockdump> - load a lockdump"
        print "parse - parse lockdump"


    def do(self):
        while True:
            sys.stdout.write("cmd> ")
            sys.stdout.flush()
            line=sys.stdin.readline()

            if not line: #EOF
                return 0

            line = line.strip()

            if line == "help":
                self.help()
            if line == "exit" or line == "quit":
                return 0


def verbose(config, text):
    if config.verbose.value:
        print text,

ComLog.setLevel(logging.INFO)
config=Config()
ret=config.getopt(sys.argv[1:])
if ret < 0:
    sys.exit(0)
elif ret > 0:
    sys.exit(ret)

mycli=cli()
mycli.do()

parser=LockEntryParser()
parser.parse(config.filename)

for e in parser.getLockentries().values():
    e.printData()
