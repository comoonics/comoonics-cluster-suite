# $Id: testlog.py,v 1.3 2007-06-13 09:17:22 marc Exp $
import sys
import traceback

sys.path.append("../lib")
#print sys.path

try:
    from comoonics import ComLog
    from comoonics import ComSystem
except ImportError:
    print "Exception in import "
    print traceback.print_exc()

log=ComLog.getLogger()
print log
log.critical("This is really critical");

try:
    raise TypeError, "bogus typerror for testing"
except Exception, e:
    log.exception("Huston, we have a problem")

#ComSystem.execLocal("echo \"hallo du\"")

#################
# $Log: testlog.py,v $
# Revision 1.3  2007-06-13 09:17:22  marc
# - better testing, but obsolete??
#
