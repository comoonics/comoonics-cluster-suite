"""

Init this package

"""

import sys,os.path
# to make debian work
if os.path.isdir('/usr/lib/python%s/site-packages/oldxml' % sys.version[:3]):
    sys.path.insert(0, '/usr/lib/python%s/site-packages/oldxml' % sys.version[:3])
# to make SLES and all work
if os.path.isdir('/usr/lib/python%s/site-packages' % sys.version[:3]):
    sys.path.append('/usr/lib/python%s/site-packages' % sys.version[:3])
if os.path.isdir('/usr/lib64/python%s/site-packages' % sys.version[:3]):
    sys.path.append('/usr/lib64/python%s/site-packages' % sys.version[:3])

from exceptions import ImportError

try:
    import comoonics.backup
except ImportError:
#    print "Importerror of comoonics.backup"
            pass

def asConfigParser():
    from comoonics import XMLConfigParser
    import sys
    sys.modules["ConfigParser"]=XMLConfigParser

########
# $Log: __init__.py,v $
# Revision 1.4  2009-06-10 15:20:34  marc
# - added debian and sles paths.
#
# Revision 1.3  2007/06/13 09:15:12  marc
# - added asConfigParser
#
# Revision 1.2  2007/03/26 08:15:21  marc
# automatically importing comoonics.backup if available
#
# Revision 1.1  2006/07/19 14:29:15  marc
# removed the filehierarchie
#