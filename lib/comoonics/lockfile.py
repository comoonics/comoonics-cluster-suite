"""
lockfile  can  be  used  to  create  one  or  more semaphore files.  If lockfile can’t create all the specified files (in the specified order), it waits sleeptime
(defaults to 8) seconds and retries the last file that didn’t succeed.  You can specify the number of retries to do until failure is returned.  If the  number  of
retries is -1 (default, i.e., -r-1) lockfile will retry forever.

If the number of retries expires before all files have been created, lockfile returns failure and removes all the files it created up till that point.

Using  lockfile as the condition of a loop in a shell script can be done easily by using the -!  flag to invert the exit status.  To prevent infinite loops, fail-
ures for any reason other than the lockfile already existing are not inverted to success but rather are still returned as failures.

All flags can be specified anywhere on the command line, they will be processed when encountered.  The command line is simply parsed from left to right.

All files created by lockfile will be read-only, and therefore will have to be removed with rm -f.

If you specify a locktimeout then a lockfile will be removed by force after locktimeout seconds have passed since the lockfile  was  last  modified/created  (most
likely  by some other program that unexpectedly died a long time ago, and hence could not clean up any leftover lockfiles).  Lockfile is clock skew immune.  After
a lockfile has been removed by force, a suspension of suspend seconds (defaults to 16) is taken into account,  in  order  to  prevent  the  inadvertent  immediate
removal of any newly created lockfile by another program (compare SUSPEND in procmail(1)).

Mailbox locks
   If the permissions on the system mail spool directory allow it, or if lockfile is suitably setgid, it will be able to lock and unlock your system mailbox by using
   the options -ml and -mu respectively.
"""

from comoonics import ComLog, ComSystem

logger=ComLog.getLogger("comoonics.lockfile")

class lockfile(object):
    COMMAND="lockfile"
    """
    The lockfile class
    """
    def __init__(self, _filename):
        self.filename=_filename
    
    def _buildOptions(self, sleeptime=-1, retries=-1, locktimeout=-1, suspend=-1):
        _opts=list()
        if sleeptime>=0:
            _opts.append("-%u" %sleeptime)
        if retries>=0:
            _opts.append("-r %u" %retries)
        if locktimeout>=0:
            _opts.append("-l %u" %locktimeout)
        if suspend>=0:
            _opts.append("-s %u" %suspend)
        return " ".join(_opts)
    
    def lock(self, sleeptime=-1, retries=-1, locktimeout=-1, suspend=-1):
        ComSystem.execLocalOutput("%s %s %s" %(self.COMMAND, self._buildOptions(sleeptime, retries, locktimeout, suspend), self.filename))
        
    def unlock(self):
        ComSystem.execLocalOutput("rm -f %s" %self.filename)

#########################
# $Log: lockfile.py,v $
# Revision 1.1  2008-03-14 10:38:30  marc
# initial revision
#
