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
log.critical("This is really critical");

ComSystem.execLocal("echo \"hallo du\"")


